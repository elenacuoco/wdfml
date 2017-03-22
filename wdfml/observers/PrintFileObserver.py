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


class PrintTriggers(Observer):
    def __init__ ( self, par ):
        self.filesave= par.outdir + 'WDFTrigger-%s-GPS%s-AR%s-Win%s-Ov%s-SNR%s.csv' % (
        par.chan, int(par.gpsStart), par.ARorder, par.window, par.overlap, int(par.threshold))
        self.Ncoeff= par.Ncoeff
        self.f = open(self.filesave, 'w')
        stringa = 'GPSMax,SNRMax,FreqMax,GPSstart,Duration,WaveletFam'
        for i in range(par.Ncoeff):
            stringa += ',' + 'WavCoeff' + str(i)
        stringa += '\n'
        self.f.write(stringa)

    def update( self, Cev):
        if (Cev!=None and Cev.mTime!=0.0):
            stringa = repr(Cev.mTimeMax) + ',' + repr(Cev.mSNR) + ',' + repr(Cev.mlevel) + ',' + repr(Cev.mTime) + ',' + repr(Cev.mLenght) + ',' + repr(Cev.mWave)
            for i in range(0, self.Ncoeff):
                stringa += ',' + repr(Cev.GetCoeff(i))
            stringa += '\n'
            self.f.write(stringa)
            self.f.flush()
