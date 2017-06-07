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


class Clustering(Observer, Observable):
    def __init__(self, parameters):
        """
        :type parameters: class Parameters object
        """
        Observable.__init__(self)
        Observer.__init__(self)
        self.deltaT = parameters.deltaT
        self.deltaSNR = parameters.deltaSNR
        self.factorF = parameters.resampling / (2.0 * parameters.window)
        self.evP = EventFullFeatured(parameters.Ncoeff)
        self.evN = EventFullFeatured(parameters.Ncoeff)

        self.Cmax = np.empty(parameters.Ncoeff)
        self.SNRmax = parameters.threshold
        self.ClevelMax = 0
        self.TimeMax = parameters.gpsStart
        self.WaveMax = 'initWave'
        self.Ncoeff = parameters.Ncoeff
        self.Cev = ClusteredEvent(self.Ncoeff)
        self.EventsNumber=0

    def update(self, ev):
        if ev.mTime != self.evN.mTime:
            if self.EventsNumber == 0:
                self.EventsNumber = 1
                self.evP.EVcopy(ev)
                self.evN.EVcopy(ev)
                ###inizialite parameter at peak
                self.SNRmax = ev.mSNR
                for i in range(self.Ncoeff):
                    self.Cmax[i] = ev.GetCoeff(i)
                self.ClevelMax = ev.mlevel
                self.TimeMax = ev.mTime
                self.WaveMax = ev.mWave
            self.EventsNumber += 1
            if np.fabs(ev.mTime - self.evN.mTime) > self.deltaT or (np.fabs(ev.mSNR - self.evN.mSNR) / self.evN.mSNR) > self.deltaSNR:
                self.Cev.update(self.evP.mTime, self.SNRmax, self.ClevelMax, self.TimeMax,
                                np.fabs(self.evN.mTime - self.evP.mTime), self.WaveMax, self.Cmax)
                self.update_observers(self.Cev)

                self.evP.EVcopy(ev)
                self.evN.EVcopy(ev)
                ##new values to identify next peak
                self.SNRmax = ev.mSNR
                self.TimeMax = ev.mTime
                for i in range(0, self.Ncoeff):
                    self.Cmax[i] = ev.GetCoeff(i)
                self.WaveMax = ev.mWave
                self.ClevelMax = ev.mlevel * self.factorF  # insert triggers into file

            else:
                self.evN.EVcopy(ev)
                if ev.mSNR > self.SNRmax:
                    self.SNRmax = ev.mSNR
                    self.TimeMax = ev.mTime
                    for i in range(0, self.Ncoeff):
                        self.Cmax[i] = ev.GetCoeff(i)
                    self.WaveMax = ev.mWave
                    self.ClevelMax = ev.mlevel* self.factorF

