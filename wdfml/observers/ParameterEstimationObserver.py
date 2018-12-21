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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def estimate_meta_features(sig, fs):
    peakind = signal.find_peaks_cwt(sig, np.arange(1, 64))
    tMax = np.argmax(np.abs(sig)) / fs
    duration = (np.max(peakind) - np.min(peakind)) / fs

    freq, psd = signal.welch(sig, fs, nfft=len(sig), nperseg=len(sig))

    peaks, _ = find_peaks(psd, height=psd.mean())

    freqs = freq[peaks]
    freqMean = np.mean(freqs)
    freqMax = np.max(freqs)
    prominences = peak_prominences(psd, peaks)[0]
    snrMax = np.max(prominences) / (4.0 * psd.mean())

    return tMax, duration, snrMax, freqMean, freqMax


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

        tMax, duration, snrMax, freqMean, freqMax = estimate_meta_features(Icoeff, self.sampling)
        tnew = t0 + tMax
        eventParameters = eventPE(tnew, snrMean, snrMax, freqMean, freqMax, duration, wave, coeff, Icoeff)
        self.update_observers(eventParameters)
