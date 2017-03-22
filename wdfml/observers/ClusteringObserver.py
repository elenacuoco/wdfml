"""
This class implement the clustering of triggers found by wdf pipeline
  .. function:: Cluster(triggers,deltaT,deltaSNR)

   :module: wdml.observers.clustering
"""

import logging

from wdfml.observers.observer import Observer
from pytsa.tsa import *
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Clustering(Observer):
    def __init__ ( self, parameters ):
        """
        :type deltaT: float
        :type deltaSNR: float
        :type triggers: pandas DataFrame
        """
        self.deltaT = parameters.deltaT
        self.deltaSNR = parameters.deltaSNR
        self.clusteredEvent = ClusterizedEventFullFeatured(parameters.Ncoeff)
        self.factorF = parameters.resampling / (2.0 * parameters.window)
        self.evP = EventFullFeatured(parameters.Ncoeff)
        self.evN = EventFullFeatured(parameters.Ncoeff)
        self.Cmax = np.empty(parameters.Ncoeff)
        self.SNRmax = 0.0
        self.ClevelMax = 0
        self.TimeMax = 0.0
        self.WaveMax = ''
        self.Ncoeff = parameters.Ncoeff
        self.EventsNumber = 0
        self.CEV = ClusterizedEventFullFeatured(parameters.Ncoeff)

    def update ( self, event ):
        if np.fabs(event.mTime - self.evN.mTime) > self.deltaT \
                or (np.fabs(event.mSNR - self.evN.mSNR) / self.evN.mSNR) > self.deltaSNR:
            self.clusteredEvent.mTime = self.evP.mTime  # starting time
            self.clusteredEvent.mTimeMax = self.TimeMax  # gps of peak
            self.clusteredEvent.mSNR = self.SNRmax  # snr of peak
            self.clusteredEvent.mLenght = np.fabs(self.evN.mTime - self.evP.mTime)  # duration
            for i in range(0, self.Ncoeff):
                self.clusteredEvent.SetCoeff(i, self.Cmax[i])  # wavelet coefficient at peak

            self.clusteredEvent.mlevel = self.ClevelMax * self.factorF  # frequency at peak
            self.clusteredEvent.mWave = self.WaveMax  # wavelet at peak

            self.CEV.mTime = self.clusteredEvent.mTime
            self.CEV.mTimeMax = self.clusteredEvent.mTimeMax
            self.CEV.mSNR = self.clusteredEvent.mSNR
            self.CEV.mlevel = self.clusteredEvent.mlevel
            self.CEV.mWave = self.clusteredEvent.mWave
            self.CEV.mLenght = self.clusteredEvent.mLenght

            for i in range(0, self.Ncoeff):
                self.CEV.SetCoeff(i, self.Cmax[i])  # wavelet coefficient at peak
            #print(event.mTime, self.CEV.mTime)
            self.clusteredEvent = ClusterizedEventFullFeatured(self.Ncoeff)
            self.evP.EVcopy(event)
            self.evN.EVcopy(event)
            ##new values to identify next peak
            self.SNRmax = event.mSNR
            self.TimeMax = event.mTime
            for i in range(0, self.Ncoeff):
                self.Cmax[i] = event.GetCoeff(i)
            self.WaveMax = event.mWave
            self.ClevelMax = event.mlevel  # insert triggers into file

        else:
            self.evN.EVcopy(event)
            if event.mSNR > self.SNRmax:
                self.SNRmax = event.mSNR
                self.TimeMax = event.mTime
                for i in range(0, self.Ncoeff):
                    self.Cmax[i] = event.GetCoeff(i)
                self.WaveMax = event.mWave
                self.ClevelMax = event.mlevel


