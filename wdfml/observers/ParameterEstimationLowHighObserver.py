"""
This class implement the clustering of triggers found by wdf pipeline
  .. function:: Cluster(triggers,deltaT,deltaSNR)

   :module: wdml.observers.clustering
"""

import logging

from pytsa.tsa import *
from pytsa.tsa import *

from wdfml.observers.observable import Observable
from wdfml.observers.observer import Observer
from wdfml.structures.eventPE import *
from wdfml.structures.array2SeqView import *
from scipy import signal
import numpy as np
from numpy.fft import fft
from heapq import nlargest
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def estimate_freq ( sig, fs ):
    freq, psd = signal.welch(sig, fs)
    threshold = 0.5 * max(abs(psd))
    mask = abs(psd) > threshold
    peaks = freq[mask]
    freq = np.max(peaks)
    return freq


def wave_freq ( sig, fs ):
    domain = float(len(sig))
    assert domain > 0
    index = np.argmax(abs(fft(sig)[1:])) + 2
    if index > len(sig) / 2:
        index = len(sig) - index + 2
    freq = (fs / domain) * (index - 1)
    return freq


def estimate_freq_mean ( sig, fs ):
    freq, psd = signal.periodogram(sig, fs)
    threshold = 0.5 * max(abs(psd))
    mask = abs(psd) > threshold
    peaks = freq[mask]
    freqmean = np.mean(peaks)
    return freqmean


class ParameterEstimation(Observer, Observable):
    def __init__ ( self, parameters ):
        """
        :type parameters: class Parameters object
        """
        Observable.__init__(self)
        Observer.__init__(self)
        self.sampling = parameters.resampling
        self.sigma = parameters.sigma
        self.Ncoeff = parameters.Ncoeff
        self.scale = int(np.log2(parameters.Ncoeff))
        self.sigma = parameters.sigma
        self.snr = parameters.threshold

    def update ( self, event ):
        wave = event.mWave
        t0 = event.mTime
        coeff = np.zeros(self.Ncoeff)
        Icoeff = np.zeros(self.Ncoeff)
        for i in range(self.Ncoeff):
            coeff[i] = event.GetCoeff(i)

        #### here we reconstruct really the event in the wavelet plane

        low = np.zeros((int(self.scale), int(2 ** ((self.scale) - 1))))
        high = np.zeros((int(self.scale), int(2 ** ((self.scale) - 1))))

        dlow = defaultdict(list)
        dhigh = defaultdict(list)

        for j in range(int(self.scale-3)):
            for k in range(int(2 ** (j - 1))):
                low[j, k] = coeff[j + k]
                dlow[low[j, k]].append((j, k))

        for j in range(int(self.scale-3), int(self.scale)):
            for k in range(int(2 ** (j - 1))):
                high[j, k] = coeff[j + k]
                dhigh[high[j, k]].append((j, k))

        for value, positions in nlargest(1, dlow.items(), key=lambda item: item[0]):
            index0 = positions[0][0] + positions[0][1]
            scale0 = positions[0][0]
            value0 = value
            maxvalue = (scale0, index0, value0)

        indiceslow = []
        valueslow = []
        for value, positions in nlargest(32, dlow.items(), key=lambda item: item[0]):
            index = positions[0][0] + positions[0][1]
            if np.abs(index - index0) < 3:
                indiceslow.append(index)
                valueslow.append(value)
                index0 = index

        timeDetaillow = np.mean(indiceslow)
        #        timeDuration = np.max(indices) - np.min(indices)
        snrDetaillow = np.sqrt(np.sum([x * x for x in valueslow]))

        for value, positions in nlargest(1, dhigh.items(), key=lambda item: item[0]):
            index0 = positions[0][0] + positions[0][1]
            scale0 = positions[0][0]
            value0 = value
            maxvalue = (scale0, index0, value0)

        indiceshigh = []
        valueshigh = []
        for value, positions in nlargest(32, dhigh.items(), key=lambda item: item[0]):
            index = positions[0][0] + positions[0][1]
            if np.abs(index - index0) < 3:
                indiceshigh.append(index)
                valueshigh.append(value)
                index0 = index

        timeDetailhigh = np.mean(indiceshigh)
        #        timeDuration = np.max(indices) - np.min(indices)
        snrDetailhigh = np.sqrt(np.sum([x * x for x in valueshigh]))
        coeffhigh=np.zeros(self.Ncoeff)
        coefflow = np.zeros(self.Ncoeff)
        for i in range(self.Ncoeff):
            coefflow[i] = coeff[i]
            coeffhigh[i] = coeff[i]

        for i in range(self.Ncoeff):
            if i not in indiceslow:
                coefflow[i] = 0.0

        tlow =t0+ timeDetaillow / self.sampling
        data = array2SeqView(t0, self.sampling, self.Ncoeff)
        data = data.Fill(t0, coefflow)
        dataIdct = array2SeqView(t0, self.sampling, self.Ncoeff)
        dataIdct = dataIdct.Fill(t0, coefflow)
        if event.mWave != 'DCT':
            wt = getattr(WaveletTransform, wave)
            WT = WaveletTransform(self.Ncoeff, wt)
            WT.Inverse(data)
            for i in range(self.Ncoeff):
                Icoeff[i] = data.GetY(0, i)
        else:
            idct = IDCT(self.Ncoeff)
            idct(data, dataIdct)
            for i in range(self.Ncoeff):
                Icoeff[i] = dataIdct.GetY(0, i)

        snr = snrDetaillow / (np.sqrt(2.0) * self.sigma)
        if snr >= self.snr:
            freq = wave_freq(Icoeff, self.sampling)
            # snr = event.mSNR
            eventParameters = eventPE(tlow, snr, freq, wave, coefflow, Icoeff)
            self.update_observers(eventParameters)

        for i in range(self.Ncoeff):
            if i not in indiceshigh:
                coeffhigh[i] = 0.0

        thigh = t0 + timeDetailhigh / self.sampling
        data = array2SeqView(t0, self.sampling, self.Ncoeff)
        data = data.Fill(t0, coeffhigh)
        dataIdct = array2SeqView(t0, self.sampling, self.Ncoeff)
        dataIdct = dataIdct.Fill(t0, coeffhigh)
        if event.mWave != 'DCT':
            wt = getattr(WaveletTransform, wave)
            WT = WaveletTransform(self.Ncoeff, wt)
            WT.Inverse(data)
            for i in range(self.Ncoeff):
                Icoeff[i] = data.GetY(0, i)
        else:
            idct = IDCT(self.Ncoeff)
            idct(data, dataIdct)
            for i in range(self.Ncoeff):
                Icoeff[i] = dataIdct.GetY(0, i)

        snr = snrDetailhigh / (np.sqrt(2.0) * self.sigma)
        if snr >= self.snr:
            freq = estimate_freq(Icoeff, self.sampling)
            # snr = event.mSNR
            eventParameters = eventPE(thigh, snr, freq, wave, coeffhigh, Icoeff)
            self.update_observers(eventParameters)
