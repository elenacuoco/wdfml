__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = ["http://www.giantflyingsaucer.com/"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

import numpy as np
from collections import OrderedDict
class OrderedMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        return OrderedDict()

    def __new__(cls, name, bases, clsdict):
        c = type.__new__(cls, name, bases, clsdict)
        c._orderedKeys = clsdict.keys()
        return c

class ClusteredEvent(metaclass=OrderedMeta):
    def __init__(self, Cev,Ncoeff):
        self.GPSMax = Cev.mTimeMax
        self.SNRMax = Cev.mSNR
        self.FreqMax = Cev.mlevel
        self.GPSstart = Cev.mTime
        self.Duration = Cev.mLenght
        self.WaveletFam = Cev.mWave

        for i in range(Ncoeff):
            key='WavCoeff'+str(i)
            setattr(self, key,  Cev.GetCoeff(i))
    def getWavCoeff(self,i):
        key = 'WavCoeff' + str(i)
        return getattr(self, key)


