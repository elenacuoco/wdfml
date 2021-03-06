__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = ["http://www.giantflyingsaucer.com/"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

from collections import OrderedDict



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
        self.WaveletFam = "Haar"
        for i in range(Ncoeff):
            setattr(self, "WaveCoeff" + str(i), 0.0)



    def update(self, tmax, SNR, freq, Wave, Coeff):
        self.GPSMax = tmax
        self.SNRMax = SNR
        self.FreqMax = freq
        self.WaveletFam = Wave
        for i in range(len(Coeff)):
            setattr(self, "WaveCoeff"+str(i), Coeff[i])
