"""
This class implement the clustering of triggers found by wdf pipeline
  .. function:: Cluster(triggers,deltaT,deltaSNR)

   :module: wdml.observers.clustering
"""

import logging
from collections import defaultdict
from heapq import nlargest

from numpy.fft import fft
from pytsa.tsa import *
from scipy import signal, integrate

from wdfml.observers.observable import Observable
from wdfml.observers.observer import Observer
from wdfml.structures.array2SeqView import *
from wdfml.structures.eventPE import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def estimate_snr(a, axis=0, ddof=0):
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m / sd)


def estimate_freq_mean(sig, fs):
    freq, psd = signal.welch(sig, fs, window='hanning', nperseg=512, noverlap=None, nfft=None, detrend=False,
                             return_onesided=True, scaling='density', axis=-1)
    threshold = np.mean(psd)

    mask = np.abs(psd) >= threshold
    peaks = freq[mask]
    freq_mean = peaks.mean()
    return freq_mean


def estimate_freq(sig, fs):
    freq, psd = signal.welch(sig, fs, window='hanning', nperseg=1024, noverlap=None, nfft=None, detrend=False,
                             return_onesided=True, scaling='density', axis=-1)
    threshold = np.mean(psd)
    mask = np.abs(psd) >= threshold
    peaks = freq[mask]
    freq_mean = peaks.mean()
    return freq_mean


def estimate_freq_mean_max(sig, fs):
    freq, psd = signal.welch(sig, fs, window='hanning', nperseg=None, noverlap=None, nfft=None, detrend=False,
                             return_onesided=True, scaling='density', axis=-1)
    threshold = np.mean(psd)
    mask = np.abs(psd) >= threshold
    peaks = freq[mask]
    freq_mean = peaks.mean()
    psdm = psd[mask]
    locY = np.argmax(psdm)  # Find its location
    freqMax = freq[locY]  # Get the actual frequency value

    return freq_mean, freqMax


def wave_freq(sig, fs):
    domain = float(len(sig))
    assert domain > 0
    index = np.argmax(abs(fft(sig)[1:])) + 2
    if index > len(sig) / 2:
        index = len(sig) - index + 2
    freq = (fs / domain) * (index - 1)
    return freq


def estimate_freqMax(x, fs):
    Hn = fft.fft(x)
    freqs = fft.fftfreq(len(Hn), 1 / fs)
    idx = np.argmax(np.abs(Hn))
    freq_in_hertz = freqs[idx]
    return freq_in_hertz


class ParameterEstimation(Observer, Observable):
    def __init__(self, parameters):
        """
        :type parameters: class Parameters object
        """
        Observable.__init__(self)
        Observer.__init__(self)
        self.sampling = parameters.resampling
        self.Ncoeff = parameters.Ncoeff
        self.scale = int(np.log2(parameters.Ncoeff))
        self.snr = parameters.threshold
        self.ARsigma = parameters.sigma
        self.df = (self.sampling / self.Ncoeff)  # *np.sqrt(2)

    # def update(self, event):
    #     wave = event.mWave
    #     t0 = event.mTime
    #     #logging.info(str(t0))
    #     coeff = np.zeros(self.Ncoeff)
    #     Icoeff = np.zeros(self.Ncoeff)
    #     for i in range(self.Ncoeff):
    #         coeff[i] = event.GetCoeff(i)
    #     sigma = 1.0 / (event.mSNR / np.sqrt(np.sum([x * x for x in coeff])))
    #     #### here we reconstruct really the event in the wavelet plane
    #
    #     new = np.zeros((int(self.scale), int(2 ** ((self.scale) - 1))))
    #     dnew = defaultdict(list)
    #
    #     for j in range(int(self.scale)):
    #         for k in range(int(2 ** (j - 1))):
    #             new[j, k] = np.abs(coeff[j + k])
    #             dnew[new[j, k]].append((j, k))
    #
    #     for value, positions in nlargest(1, dnew.items(), key=lambda item: item[0]):
    #         index0 = positions[0][0] + positions[0][1]
    #         scale0 = positions[0][0]
    #         value0 = value
    #         maxvalue = (scale0, index0, value0)
    #
    #     indicesnew = []
    #     valuesnew = []
    #     for value, positions in nlargest(self.Ncoeff, dnew.items(), key=lambda item: item[0]):
    #         index = positions[0][0] + positions[0][1]
    #         if np.abs(index - index0) <200:
    #             indicesnew.append(index)
    #             valuesnew.append(value)
    #             index0 = index
    #
    #     for i in range(self.Ncoeff):
    #         if i not in indicesnew:
    #             coeff[i] = 0.0
    #
    #     data = array2SeqView(t0, self.sampling, self.Ncoeff)
    #     data = data.Fill(t0, coeff)
    #     dataIdct = array2SeqView(t0, self.sampling, self.Ncoeff)
    #     dataIdct = dataIdct.Fill(t0, coeff)
    #     if event.mWave != 'DCT':
    #         wt = getattr(WaveletTransform, wave)
    #         WT = WaveletTransform(self.Ncoeff, wt)
    #         WT.Inverse(data)
    #         for i in range(self.Ncoeff):
    #             Icoeff[i] = data.GetY(0, i)
    #     else:
    #         idct = IDCT(self.Ncoeff)
    #         idct(data, dataIdct)
    #         for i in range(self.Ncoeff):
    #             Icoeff[i] = dataIdct.GetY(0, i)
    #
    #     timeDuration = np.abs(np.max(indicesnew) - np.min(indicesnew)) / self.sampling
    #     timeDetailnew = np.float(maxvalue[1]) / self.sampling
    #     # timeDetailnew = np.median(indicesnew)/ self.sampling
    #     snrDetailnew = np.sqrt(np.sum([x * x for x in valuesnew]))
    #     tnew = t0 + timeDetailnew
    #
    #     snrMax = snrDetailnew / (sigma)  # *self.df)
    #     snr = event.mSNR  # /self.df
    #     freqatpeak = wave_freq(Icoeff, self.sampling)
    #     freq = estimate_freq_mean(Icoeff, self.sampling)
    #     eventParameters = eventPE(tnew, snr, snrMax, freq, freqatpeak, timeDuration, wave, coeff, Icoeff)
    #
    #     self.update_observers(eventParameters)

    # def update ( self, event ):
    #     wave = event.mWave
    #     t0 = event.mTime
    #     coeff = np.zeros(self.Ncoeff)
    #     Icoeff = np.zeros(self.Ncoeff)
    #
    #     for i in range(1,self.Ncoeff):
    #         coeff[i] = event.GetCoeff(i)
    #
    #     #sigma = 1.0 / (event.mSNR / np.sqrt(np.sum([x * x for x in coeff])))
    #     #
    #     isnews=np.argsort(np.abs(coeff))
    #     index0 = isnews[0]
    #     #
    #     indicesnew = []
    #     #
    #     #
    #     for index in isnews:
    #          if np.abs(index - index0) < 100:
    #              indicesnew.append(index)
    #              index0 = index
    #     #
    #
    #     for i in range(1,self.Ncoeff):
    #          if i not in indicesnew:
    #             coeff[i]=0.0
    #
    #     coeff[0] = event.GetCoeff(0)
    #     data = array2SeqView(t0, self.sampling, self.Ncoeff)
    #     data = data.Fill(t0, coeff)
    #     dataIdct = array2SeqView(t0, self.sampling, self.Ncoeff)
    #     dataIdct = dataIdct.Fill(t0, coeff)
    #     if event.mWave != 'DCT':
    #         wt = getattr(WaveletTransform, wave)
    #         WT = WaveletTransform(self.Ncoeff, wt)
    #         WT.Inverse(data)
    #         for i in range(self.Ncoeff):
    #             Icoeff[i] = data.GetY(0, i)
    #     else:
    #         idct = IDCT(self.Ncoeff)
    #         idct(data, dataIdct)
    #         for i in range(self.Ncoeff):
    #             Icoeff[i] = dataIdct.GetY(0, i)
    #
    #     timeDuration = np.abs(np.max(indicesnew) - np.min(indicesnew)) / self.sampling
    #     timeDetailnew =  indicesnew[0]/self.sampling
    #
    #     tnew = t0 + timeDetailnew
    #
    #     freqmean,freqMax,snrMax =estimate_freq_mean_max_snr(Icoeff, self.sampling)
    #     snr=event.mSNR
    #
    #     #
    #
    #
    #     eventParameters = eventPE(tnew, snr, snrMax, freqmean, freqMax, timeDuration, wave, coeff, Icoeff)
    #     self.update_observers(eventParameters)

    def update(self, event):
        wave = event.mWave
        t0 = event.mTime
        coeff = np.zeros(self.Ncoeff)
        coeffMax = np.zeros(self.Ncoeff)
        Icoeff = np.zeros(self.Ncoeff)
        IcoeffMax = np.zeros(self.Ncoeff)

        for i in range(0, self.Ncoeff):
            coeff[i] = event.GetCoeff(i)

        sigma = 1.0 / (event.mSNR / np.sqrt(np.sum([x * x for x in coeff])))

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

        snr= event.mSNR
        freqmean = estimate_freq(Icoeff, self.sampling)

        #### here we reconstruct really the event in the wavelet plane

        new = np.zeros((int(self.scale), int(2 ** ((self.scale) - 1))))
        dnew = defaultdict(list)

        for j in range(int(self.scale)):
            for k in range(int(2 ** (j - 1))):
                new[j, k] = np.abs(coeff[j + k])
                dnew[new[j, k]].append((j, k))

        for value, positions in nlargest(1, dnew.items(), key=lambda item: item[0]):
            index0 = positions[0][0] + positions[0][1]
            scale0 = positions[0][0]
            value0 = value
            maxvalue = (scale0, index0, value0)

        indicesnew = []
        valuesnew = []
        for value, positions in nlargest(self.Ncoeff, dnew.items(), key=lambda item: item[0]):
            index = positions[0][0] + positions[0][1]
            if np.abs(index - index0) < 128:
                indicesnew.append(index)
                valuesnew.append(value)
                index0 = index

        for i in indicesnew:
            coeffMax[i] = event.GetCoeff(i)

        coeffMax[0] = event.GetCoeff(0)

        data = array2SeqView(t0, self.sampling, self.Ncoeff)
        data = data.Fill(t0, coeffMax)
        dataIdct = array2SeqView(t0, self.sampling, self.Ncoeff)
        dataIdct = dataIdct.Fill(t0, coeffMax)
        if event.mWave != 'DCT':
            wt = getattr(WaveletTransform, wave)
            WT = WaveletTransform(self.Ncoeff, wt)
            WT.Inverse(data)
            for i in range(self.Ncoeff):
                IcoeffMax[i] = data.GetY(0, i)
        else:
            idct = IDCT(self.Ncoeff)
            idct(data, dataIdct)
            for i in range(self.Ncoeff):
                IcoeffMax[i] = dataIdct.GetY(0, i)

        snrMax = np.sqrt(np.sum([x * x for x in coeffMax])) / sigma
        freqMax = estimate_freq(IcoeffMax, self.sampling)
        timeDuration = np.abs(np.max(indicesnew) - np.min(indicesnew)) / self.sampling
        timeDetailnew =  indicesnew[0]/self.sampling
        #
        tnew = t0 + timeDetailnew

        eventParameters = eventPE(tnew, snr, snrMax, freqmean, freqMax, timeDuration, wave, coeff, Icoeff)
        self.update_observers(eventParameters)
