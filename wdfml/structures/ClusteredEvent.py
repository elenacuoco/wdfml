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
from scipy.sparse import csr_matrix


class OrderedMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        return OrderedDict()

    def __new__(cls, name, bases, clsdict):
        c = type.__new__(cls, name, bases, clsdict)
        c._orderedKeys = clsdict.keys()
        return c


class ClusteredEvent(object):
    def __init__(self, t0, snrMean,freqMean,tmax,snrMax, freqMax, duration, Wave, Coeff, ICoeff):
        self.gpsStart = t0
        self.snrMean = snrMean
        self.freqMean = freqMean
        self.gpsMax = tmax
        self.snrMax = snrMax
        self.freqMax = freqMax
        self.duration = duration
        self.wave = Wave
        for i in range(len(Coeff)):
            setattr(self, "wt"+str(i), Coeff[i])
        for i in range(len(Coeff)):
            setattr(self, "rw"+str(i), ICoeff[i])
