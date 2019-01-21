"""
This class implement the clustering of triggers found by wdf pipeline
  .. function:: Cluster(triggers,deltaT,deltaSNR)

   :module: wdml.observers.clustering
"""

import logging

from pytsa.tsa import *
from scipy import signal
from scipy.signal import find_peaks, peak_prominences

from wdfml.observers.observable import Observable
from wdfml.observers.observer import Observer
from wdfml.structures.array2SeqView import *
from wdfml.structures.eventPE import *
import numpy as np
import librosa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def estimate_meta_features(sig, fs):
#     peakind = signal.find_peaks_cwt(sig, np.arange(1, 128))
#     duration = (np.max(peakind) - np.min(peakind)) / fs
#
#     tMax = np.argmax(np.abs(sig)) / fs
#     freq, psd = signal.welch(sig, fs, nfft=len(sig), nperseg=len(sig))
#     peaks, _ = find_peaks(psd, height=psd.mean())
#
#     freqs = freq[peaks]
#     freqMean = np.mean(freqs)
#     freqMax = np.max(freqs)
#     prominences = peak_prominences(psd, peaks)[0]
#     snrMax = np.sqrt(np.max(prominences) / (4.0 * psd.mean()))
#
#     return tMax, duration, snrMax, freqMean, freqMax


def extract_meta_features(sig, fs):
    freqMean = np.mean(librosa.feature.spectral_centroid(sig, sr=fs,n_fft=len(sig),hop_length=len(sig)))
    freqMax = np.mean(librosa.feature.spectral_rolloff(sig, sr=fs,n_fft=len(sig),hop_length=len(sig)))
    rmse = librosa.feature.rmse(y=sig)
    snrMax = np.max(np.abs(sig)) / np.mean(rmse)
    return snrMax, freqMean, freqMax


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
        ########clustering in the wavelet plane################

        # isnews = np.argsort(np.abs(coeff))
        # index0 = isnews[0]
        # indicesnew = []
        # for index in isnews:
        #     if np.abs(index - index0) < 100:
        #         indicesnew.append(index)
        #         index0 = index
        #
        # for i in range(1, self.Ncoeff):
        #     if i not in indicesnew:
        #         coeff[i] = 0.0
        #
        # coeff[0] = event.GetCoeff(0)
        ##############end of clustering#######################

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

        tMax = np.argmax(np.abs(coeff)) / self.sampling
        sorted = np.argsort(np.abs(coeff))
        duration = np.abs(sorted[0] - sorted[10]) / self.sampling
        snrMax, freqMean, freqMax = extract_meta_features(Icoeff, self.sampling)
        tnew = t0 + tMax
        eventParameters = eventPE(tnew, snrMean, snrMax, freqMean, freqMax, duration, wave, coeff, Icoeff)
        self.update_observers(eventParameters)
