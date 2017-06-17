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
import csv
import os.path
from wdfml.structures.SingleEvent import *
import numpy as np

class SingleEventPrintTriggers(Observer):
    def __init__(self, par):
        self.filesave = par.dir + 'WDFTrigger-%s-GPS%s-AR%s-Win%s-Ov%s-SNR%s.csv' % (
            par.chan, int(par.gpsStart), par.ARorder, par.window, par.overlap, int(par.threshold))
        self.event = SingleEvent(par.window)
        self.Ncoeff=par.window
        try:
            os.remove(self.filesave)
        except OSError:
            pass


    def update(self, ev):
        self.file_exists = os.path.isfile(self.filesave)
        Cmax=np.zeros(self.Ncoeff)
        for i in range(0, self.Ncoeff):
            Cmax[i] = ev.GetCoeff(i)
        self.event.update(ev.mTime, ev.mSNR, ev.mlevel, ev.mWave, Cmax)
        self.EV = self.event.__dict__
        with open(self.filesave, 'a') as csvfile:
            headers = sorted(self.EV.keys())
            writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
            if not self.file_exists:
                writer.writeheader()
            writer.writerow(self.EV)
