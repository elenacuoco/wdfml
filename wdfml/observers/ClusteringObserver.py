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
from wdfml.structures.eventPE import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#

class Clustering(Observer, Observable):
    def __init__ ( self, par ):
        """
        :type parameters: class Parameters object
        """
        Observable.__init__(self)
        Observer.__init__(self)
        self.deltaT = par.deltaT
        self.deltaSNR = par.deltaSNR
        self.deltaFeq = par.deltaFeq
        self.Ncoeff = par.Ncoeff
        self.evP = eventPE(par.gpsStart, 0., 0., '', np.zeros(par.Ncoeff), np.zeros(par.Ncoeff))
        self.evN = eventPE(par.gpsStart, 0., 0., '', np.zeros(par.Ncoeff), np.zeros(par.Ncoeff))
        self.CMax = np.zeros(par.Ncoeff)
        self.ICMax = np.zeros(par.Ncoeff)
        self.snr = 0.0
        self.freq = 0.0
        self.gpsStart = par.gpsStart
        self.timeMax = par.gpsStart
        self.duration = 0
        self.waveMax = ''
        self.num_ev = 1.0
        self.freqMean = 0.0
        self.freqMax = 0.0
        self.snrMean = 0.0
        self.snrMax = 0.0

    def update ( self, event ):
        if (np.fabs(event.gps - self.evN.gps) >= self.deltaT) \
                or (np.fabs(event.freq - self.evN.freq) / (self.evN.freq + 1.0)) >= self.deltaFeq \
                or (np.fabs(event.snr - self.evN.snr) / (self.evN.snr + 1.0)) >= self.deltaSNR:
            self.freqMean /= self.num_ev
            self.snrMean /= self.num_ev
            CEV = ClusteredEvent(self.evP.gps, self.snrMean, self.freqMean, \
                                 self.timeMax, self.snrMax, self.freqMax, np.fabs(self.evN.gps - self.evP.gps), \
                                 self.waveMax, self.CMax, self.ICMax)
            self.update_observers(CEV)
            self.evP.evCopy(event)
            self.evN.evCopy(event)
            ##new values to identify next peak
            self.snrMax = event.snr
            self.timeMax = event.gps
            for i in range(0, self.Ncoeff):
                self.CMax[i] = event.wt[i]
                self.ICMax[i] = event.rw[i]
            self.waveMax = event.wave
            self.freqMax = event.freq
            self.freqMean = event.freq
            self.snrMean = event.snr
            self.num_ev = 1.0

        else:
            self.num_ev += 1.0
            self.evN.evCopy(event)
            if event.snr > self.snrMax:
                self.snrMax = event.snr
                self.timeMax = event.gps
                for i in range(0, self.Ncoeff):
                    self.CMax[i] = event.wt[i]
                    self.ICMax[i] = event.rw[i]
                self.waveMax = event.wave
                self.freqMax = event.freq
            self.freqMean += event.freq
            self.snrMean += event.snr
