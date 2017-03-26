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


class Clustering(Observer,Observable):
    def __init__ ( self, parameters ):
        """
        :type parameters: class Parameters object
        """
        Observable.__init__(self)
        Observer.__init__(self)
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
        self.CEV = None

    def update ( self, event ):
        if np.fabs(event.mTime - self.evN.mTime) > self.deltaT \
                or (np.fabs(event.mSNR - self.evN.mSNR) / (self.evN.mSNR+1.0)) > self.deltaSNR:
            self.clusteredEvent.mTime = self.evP.mTime  # starting time
            self.clusteredEvent.mTimeMax = self.TimeMax  # gps of peak
            self.clusteredEvent.mSNR = self.SNRmax  # snr of peak
            self.clusteredEvent.mLenght = np.fabs(self.evN.mTime - self.evP.mTime)  # duration
            for i in range(0, self.Ncoeff):
                self.clusteredEvent.SetCoeff(i, self.Cmax[i])  # wavelet coefficient at peak

            self.clusteredEvent.mlevel = self.ClevelMax * self.factorF  # frequency at peak
            self.clusteredEvent.mWave = self.WaveMax  # wavelet at peak
            self.CEV = ClusteredEvent(self.clusteredEvent,self.Ncoeff)

            if (self.CEV != None and self.CEV.GPSstart > 0.0):
                self.update_observers(self.CEV)
            self.clusteredEvent = ClusterizedEventFullFeatured(self.Ncoeff)
            self.evP.EVcopy(event)
            self.evN.EVcopy(event)
            ##new values to identify next peak
            self.SNRmax = event.mSNR
            self.TimeMax = event.mTime  #fare update
            # cev = clustering.CEV
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
            self.CEV=None

