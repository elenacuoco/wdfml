__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"
import logging

from wdfml.observers.observer import Observer
from pytsa.tsa import *
import pickle
import os.path

import pickle
class PrintTriggers(Observer):
    def __init__(self, par):
        self.filesave = par.outdir + 'WDFTrigger-%s-GPS%s-AR%s-Win%s-Ov%s-SNR%s.csv' % (
            par.chan, int(par.gpsStart), par.ARorder, par.window, par.overlap, int(par.threshold))
        self.Ncoeff = par.Ncoeff
        try:
            os.remove(self.filesave)
        except OSError:
            pass
        self.f=open(self.filesave, 'w')

        stringa = 'GPSMax,SNRMax,FreqMax,GPSstart,Duration,WaveletFam'
        for i in range(self.Ncoeff):
            stringa += ',' + 'WavCoeff' + str(i)
        stringa += '\n'
        self.f.write(stringa)

    def update(self, Cev):
        self.file_exists = os.path.isfile(self.filesave)
        stringa = repr(Cev.GPSMax) + ',' + repr(Cev.SNRMax) + ',' + repr(Cev.FreqMax) + ',' \
                  + repr(Cev.GPSstart) + ',' + repr(Cev.Duration) + ',' + repr(Cev.WaveletFam)
        for i in range(self.Ncoeff):
            stringa += ',' + repr(Cev.getWavCoeff(i))
        stringa += '\n'
        self.f.write(stringa)
        self.f.flush()

        #with open(self.filesave, 'ab') as output:
        #    pickle.dump(self.CEV, output)

