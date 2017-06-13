__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = ["http://www.giantflyingsaucer.com/"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

from collections import OrderedDict
import numpy as np


class OrderedMeta(type):
    @classmethod
    def __prepare__ ( metacls, name, bases ):
        return OrderedDict()

    def __new__ ( cls, name, bases, clsdict ):
        c = type.__new__(cls, name, bases, clsdict)
        c._orderedKeys = clsdict.keys()
        return c


class eventPE(object):
    def __init__ ( self, gps, snr, freq, wave, coeff, Icoeff ):
        self.gps = gps
        self.snr = snr
        self.freq = freq
        self.wave = wave
        self.wt = np.empty(len(coeff))
        self.rw = np.empty(len(Icoeff))
        for i in range(len(coeff)):
            self.wt[i] = coeff[i]
        for i in range(len(Icoeff)):
            self.rw[i] = Icoeff[i]

    def update ( self, gps, snr, freq, wave, coeff, Icoeff ):
        self.gps = gps
        self.snr = snr
        self.freq = freq
        self.wave = wave
        for i in range(len(coeff)):
            self.wt[i] = coeff[i]
        for i in range(len(Icoeff)):
            self.rw[i] = Icoeff[i]

    def evCopy ( self, ev ):
        self.gps = ev.gps
        self.snr = ev.snr
        self.freq = ev.freq
        self.wave = ev.wave
        for i in range(len(ev.wt)):
            self.wt[i] = ev.wt[i]
        for i in range(len(ev.rw)):
            self.rw[i] = ev.rw[i]
