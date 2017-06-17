"""
This class implement the clustering of triggers found by wdf pipeline
  .. function:: Cluster(triggers,deltaT,deltaSNR)

   :module: wdml.observers.clustering
"""

import logging

from pytsa.tsa import *

from wdfml.observers.observer import Observer
from wdfml.observers.observable import Observable
from wdfml.structures.eventPE import *
from pytsa.tsa import *
from pytsa.tsa import SeqView_double_t as SV
from wdfml.structures.array2SeqView import *
from scipy import signal
import numpy as np
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def estimate_freq(sig,fs):
    freq, psd = signal.periodogram(sig, fs)
    threshold = 0.2* max(abs(psd))
    mask = abs(psd) > threshold
    peaks = freq[mask]
    freqmean =np.mean(peaks)
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

    def update ( self, event ):
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
        if event.mWave!='DCT':
            wt = getattr(WaveletTransform, wave)
            WT = WaveletTransform(self.Ncoeff, wt)
            WT.Inverse(data)
            for i in range(self.Ncoeff):
                Icoeff[i] = data.GetY(0, i)
        else:
            idct=IDCT(self.Ncoeff)
            idct(data,dataIdct)
            for i in range(self.Ncoeff):
                Icoeff[i] = dataIdct.GetY(0, i)
        freq =estimate_freq(Icoeff, self.sampling)
        snr = event.mSNR
        eventParameters = eventPE(t0, snr, freq, wave, coeff, Icoeff)
        self.update_observers(eventParameters)
