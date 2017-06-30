__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

from pytsa.tsa import SeqView_double_t as SV
class array2SeqView(object):
    def __init__(self, start, sampling,N):

        try:
            self.start = float(start)
        except ValueError:
            logging.info("starting time not defined")
        try:
            self.sampling = float(sampling)
        except ValueError:
            logging.info("sampling not defined")
        try:
            self.N = N
        except ValueError:
            logging.info("lenght not defined")
        self.SV=SV(self.start,1.0/self.sampling,self.N)


    def Fill(self, start, array):

        self.SV.SetStart(start)
        for i in range(self.N):
            self.SV.FillPoint(0, i, float(array[i]))
        return self.SV
    def SetStart(self, N):
        self.SV.SetStart(float(self.N) / self.sampling)

    def GetStart ( self ):
        return self.SV.GetStart()


