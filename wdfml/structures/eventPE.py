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
    def __init__ ( self, gps, snr, snrMax, freq, freqMax, duration, wave, coeff, Icoeff ):
        self.gps = gps
        self.snr = snr
        self.snrMax = snrMax
        self.freq = freq
        self.freqMax = freqMax
        self.duration = duration
        self.wave = wave
        self.Ncoeff = len(coeff)
        for i in range(len(coeff)):
            setattr(self, "wt" + str(i), coeff[i])
        for i in range(len(Icoeff)):
            setattr(self, "rw" + str(i), Icoeff[i])

    def update ( self, gps, snr, snrMax, freq, freqMax, duration, wave, coeff, Icoeff ):
        self.gps = gps
        self.snr = snr
        self.snrMax = snrMax
        self.freq = freq
        self.freqMax = freqMax
        self.duration = duration
        self.wave = wave
        for i in range(len(coeff)):
            setattr(self, "wt" + str(i), coeff[i])
        for i in range(len(Icoeff)):
            setattr(self, "rw" + str(i), Icoeff[i])

    def evCopy ( self, ev ):
        self.gps = ev.gps
        self.snr = ev.snr
        self.snrMax = ev.snrMax
        self.freq = ev.freq
        self.freqMax = ev.freqMax
        self.duration = ev.duration
        self.wave = ev.wave
        for i in range(self.Ncoeff):
            setattr(self, "wt" + str(i),  setattr(ev, "wt" + str(i)))
            setattr(self, "rw" + str(i) ,  setattr(ev, "rw" + str(i)))
