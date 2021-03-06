from pytsa.tsa import *
import logging


class downsamplig(object):
    def __init__(self, Parameters):
        try:
            self.Noutdata = int(Parameters.Noutdata)
        except ValueError:
            logging.error("Noutdata not defined")
        try:
            self.sampling = int(Parameters.sampling)
        except ValueError:
            logging.error("sampling not defined")

        try:
            self.resampling = int(Parameters.resampling)
        except ValueError:
            logging.error("Resampling factor not defined")

        try:
            self.BLfilterOrder = int(Parameters.BLfilterOrder)
        except ValueError:
            logging.error("Filter order not defined")

        self.BLfilter = BLInterpolation(1, self.Noutdata, self.sampling, self.resampling, self.BLfilterOrder)

    def GetDataAvailable(self):
        return self.BLfilter.GetDataAvailable()

    def Process(self, data, data_ds):

        self.BLfilter.Input(data)
        if self.BLfilter.GetDataAvailable() > self.Noutdata:
            self.BLfilter.Output(data_ds)
        else:
            logging.warning('Downsampling filter: Not enough input data, loading new data')
        return
