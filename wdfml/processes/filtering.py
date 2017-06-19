from pytsa.tsa import *


class downsamplig(object):
    def __init__(self, Parameters):
        try:
            self.Noutdata = int(Parameters.Noutdata)
        except ValueError:
            print("Noutdata not defined")
        try:
            self.sampling = int(Parameters.sampling)
        except ValueError:
            print("sampling not defined")

        try:
            self.resampling = int(Parameters.resampling)
        except ValueError:
            print("Resampling factor not defined")

        try:
            self.BLfilterOrder = int(Parameters.BLfilterOrder)
        except ValueError:
            print("Filter order not defined")

        self.BLfilter = BLInterpolation(1, self.Noutdata, self.sampling, self.resampling, self.BLfilterOrder)

    def GetDataAvailable(self):
        return self.BLfilter.GetDataAvailable()

    def Process(self, data, data_ds):

        self.BLfilter.Input(data)
        if self.BLfilter.GetDataAvailable() > self.Noutdata:
            self.BLfilter.Output(data_ds)
        else:
            print('not enough input data')
        return
