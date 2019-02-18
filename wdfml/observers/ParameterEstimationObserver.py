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

def thresh(coeff):
    sigma=np.median(np.abs(coeff))/0.645
    threshold = np.sqrt(2 * np.log(len(coeff))) * sigma;

    return threshold

def extract_meta_features(sigIn, fs,duration):
    sig = np.pad(sigIn, (int(fs), int(fs)), 'constant')
    freqs, psd = signal.welch(sig, fs, nperseg=1024)
    freqMax = freqs[np.argmax(psd)]
    freqMean = np.mean(freqs[psd.argsort()[-3:][::-1]])
    rmse = np.sqrt(2.0*np.average(psd))
    snrMax = np.sqrt(np.sqrt(duration)*np.max(np.abs(sigIn))/ rmse)

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
        sorted = np.nonzero(np.abs(coeff))
        duration = np.abs(np.max(sorted) - np.min(sorted)) / self.sampling
        tMax = np.argmax(np.abs(coeff)) / self.sampling
        snrMax, freqMean, freqMax = extract_meta_features(Icoeff, self.sampling,duration)
        tnew = t0 + tMax
        eventParameters = eventPE(tnew, snrMean, snrMax, freqMean, freqMax, duration, wave, coeff, Icoeff)
        self.update_observers(eventParameters)
