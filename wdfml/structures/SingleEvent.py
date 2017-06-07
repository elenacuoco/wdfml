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


class SingleEvent(object):
    def __init__(self, Ncoeff):
        self.GPSMax = 0
        self.SNRMax = 0
        self.FreqMax = 0
        self.WaveletFam = ""
        self.WavCoeff = []


    def update(self, tmax, SNR, freq, Wave, Coeff):
        self.GPSMax = tmax
        self.SNRMax = SNR
        self.FreqMax = freq
        self.WaveletFam = Wave
        self.WavCoeff = list(Coeff)
