__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

import csv
import os.path
from wdfml.observers.observer import Observer
import gzip

class SingleEventPrintTriggers(Observer):
    def __init__ ( self, par, fullPrint=0 ):
        self.filesave = par.dir + 'WDFTrigger-%s-GPS%s-AR%s-Win%s-Ov%s-SNR%s.csv' % (
            par.channel, int(par.gps), par.ARorder, par.window, par.overlap, int(par.threshold))
        self.id = 0
        if os.path.isfile(self.filesave):
            try:
                os.remove(self.filesave)
            except OSError:
                pass
        self.fullPrint = fullPrint
        self.headers = ['gps', 'snr', 'snrMax', 'freq', 'freqMax', 'duration', 'wave']
        self.headersFull = ['gps', 'snr', 'snrMax', 'freq', 'freqMax', 'duration', 'wave']
        for i in range(par.Ncoeff):
            self.headers.append("wt" + str(i))
            self.headersFull.append("wt" + str(i))
        for i in range(par.Ncoeff):
            self.headersFull.append("rw" + str(i))

            ### write on disk in ordered way

    def update ( self, CEV ):
        self.file_exists = os.path.isfile(self.filesave)
        self.ev = CEV.__dict__
        self.id += 1
        self.ev['ID'] = self.id
        if self.fullPrint == 0:
            with open(self.filesave, 'a') as csvfile:
                headers = ['gps', 'snr', 'snrMax', 'freq', 'freqMax', 'duration', 'wave']
                toprint = dict((k, self.ev[k]) for k in
                               ('gps', 'snr', 'snrMax', 'freq', 'freqMax', 'duration', 'wave'))
                writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
                if not self.file_exists:
                    writer.writeheader()
                writer.writerow(toprint)
        if self.fullPrint == 1:
            with open(self.filesave, 'a') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=self.headers)
                toprint = dict((k, self.ev[k]) for k in self.headers)
                if not self.file_exists:
                    writer.writeheader()
                writer.writerow(toprint)
        if self.fullPrint == 2:
            with open(self.filesave, 'a') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=self.headersFull)
                toprint = dict((k, self.ev[k]) for k in self.headersFull)
                if not self.file_exists:
                    writer.writeheader()
                writer.writerow(toprint)
