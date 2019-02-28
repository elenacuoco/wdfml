"""
This class implement the clustering of triggers found by wdf pipeline
  .. function:: Cluster(triggers,deltaT,deltaSNR)

   :module: wdml.observers.clustering
"""

import logging
import numpy as np
from pytsa.tsa import *
from scipy import signal

from wdfml.observers.observable import Observable
from wdfml.observers.observer import Observer
from wdfml.structures.array2SeqView import *
from wdfml.structures.eventPE import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from numpy import argmax, sqrt, mean, diff, log

from scipy.signal import find_peaks


def extract_meta_features(sigIn, fs):
    sig = np.pad(sigIn, (int(fs), int(fs)), 'constant')
    peaks, _ = find_peaks(sig, height=np.min(sig))
    tMax = argmax(np.abs(sigIn)) / fs
    duration = np.abs(np.max(peaks) - np.min(peaks)) / fs

    freqs, psd = signal.welch(sig, fs, nperseg=1024)
    sel_freqs = freqs[psd.argsort()[-3:][::-1]]
    freqMean = np.mean(sel_freqs)
    freqMax = np.max(sel_freqs)
    snrMax = np.sqrt(np.max(np.abs(sigIn)) / np.sqrt(np.average(psd)))

    return tMax, snrMax, freqMean, freqMax, duration


class ParameterEstimation(Observer, Observable):
    def __init__(self, parameters):
        """
        :type parameters: class Parameters object
        """
        Observable.__init__(self)
        Observer.__init__(self)
        self.sampling = parameters.resampling
        self.Ncoeff = parameters.Ncoeff

    def update(self, event):
        wave = event.mWave
        t0 = event.mTime
        coeff = np.zeros(self.Ncoeff)
        Icoeff = np.zeros(self.Ncoeff)
        for i in range(self.Ncoeff):
            coeff[i] = event.GetCoeff(i)

        data = array2SeqView(t0, self.sampling, self.Ncoeff)
        data = data.Fill(t0, coeff)
        dataIdct = array2SeqView(t0, self.sampling, self.Ncoeff)
        dataIdct = dataIdct.Fill(t0, coeff)
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

        snrMean = event.mSNR
        # sorted = np.nonzero(Icoeff)
        # duration = np.abs(np.max(sorted) - np.min(sorted)) / self.sampling
        # tMax = np.argmax(np.abs(coeff)) / self.sampling
        tMax, snrMax, freqMean, freqMax, duration = extract_meta_features(Icoeff, self.sampling)
        tnew = t0 + tMax
        eventParameters = eventPE(tnew, snrMean, snrMax, freqMean, freqMax, duration, wave, coeff, Icoeff)
        self.update_observers(eventParameters)
