"""
This class implement the clustering of triggers found by wdf pipeline
  .. function:: Cluster(triggers,deltaT,deltaSNR)

   :module: wdml.observers.clustering
"""

import logging

from pytsa.tsa import *

from wdfml.observers.observer import Observer
from wdfml.observers.observable import Observable
from wdfml.structures.ClusteredEvent import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# @TODO modify the estimate of SNR. Use the local threshold with the dohono-johnstone

class Clustering(Observer, Observable):
    def __init__(self, parameters):
        """
        :type parameters: class Parameters object
        """
        Observable.__init__(self)
        Observer.__init__(self)
        self.deltaT = parameters.deltaT
        self.deltaSNR = parameters.deltaSNR
        self.deltaFeq = parameters.deltaFeq
        self.factorF = parameters.resampling / (2.0 * parameters.window)
        self.Ncoeff = parameters.Ncoeff
        self.evP = EventFullFeatured(parameters.Ncoeff)
        self.evN = EventFullFeatured(parameters.Ncoeff)
        self.Cmax = np.empty(parameters.Ncoeff)
        self.SNRmax = parameters.threshold
        self.ClevelMax = parameters.resampling / (2.0 * parameters.window)
        self.TimeMax = parameters.gpsStart
        self.WaveMax = 'Haar'
        self.evP.mWave = 'Haar'
        self.evN.mWave = 'Haar'
        self.evP.mTime = parameters.gpsStart
        self.evN.mTime = parameters.gpsStart
        self.evN.mSNR = parameters.threshold
        self.evP.mSNR = parameters.threshold
        self.evN.mlevel = parameters.resampling / (2.0 * parameters.window)
        self.evP.mlevel = parameters.resampling / (2.0 * parameters.window)

    def update(self, event):
        if (np.fabs(event.mTime - self.evN.mTime) > self.deltaT)\
                or ((np.fabs(event.mlevel - self.evN.mlevel)/self.evN.mlevel) > self.deltaFeq):
            #or (np.fabs(event.mSNR - self.evN.mSNR) / (self.evN.mSNR + 1.0)) > self.deltaSNR:
            CEV=ClusteredEvent(self.evP.mTime, self.SNRmax, self.ClevelMax,\
                               self.TimeMax, np.fabs(self.evN.mTime - self.evP.mTime),  \
                               self.WaveMax,self.Cmax)
            self.update_observers(CEV)
            self.evP.EVcopy(event)
            self.evN.EVcopy(event)
            ##new values to identify next peak
            self.SNRmax = event.mSNR
            self.TimeMax = event.mTime
            for i in range(0, self.Ncoeff):
                self.Cmax[i] = event.GetCoeff(i)
            self.WaveMax = event.mWave
            self.ClevelMax = event.mlevel* self.factorF

        else:
            self.evN.EVcopy(event)
            if event.mSNR > self.SNRmax:
                self.SNRmax = event.mSNR
                self.TimeMax = event.mTime
                for i in range(0, self.Ncoeff):
                    self.Cmax[i] = event.GetCoeff(i)
                self.WaveMax = event.mWave
                self.ClevelMax = event.mlevel * self.factorF
