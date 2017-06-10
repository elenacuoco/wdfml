__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"


from wdfml.observers.observer import Observer
import csv
import os.path



class PrintTriggers(Observer):
    def __init__(self, par):
        self.filesave = par.outdir + 'WDFTrigger-%s-GPS%s-AR%s-Win%s-Ov%s-SNR%s.csv' % (
            par.chan, int(par.gpsStart), par.ARorder, par.window, par.overlap, int(par.threshold))

        try:
            os.remove(self.filesave)
        except OSError:
            pass

### write on disk in ordered way
    def update(self, Cev):
        self.file_exists = os.path.isfile(self.filesave)
        self.CEV = Cev.__dict__
        with open(self.filesave, 'a') as csvfile:
            headers = sorted(self.CEV.keys(), key=lambda x:x[:3])
            writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
            if not self.file_exists:
                writer.writeheader()
            writer.writerow(self.CEV)
