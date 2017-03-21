from pytsa.tsa import *


class downsamplig(object):
    def __init__(self, Parameters):
        if Parameters['Nchannels'] != None:
            self.Nchannels = int(Parameters['Nchannels'])
        else:
            self.Nchannels = 1

        try:
            self.Noutdata = int(Parameters['Noutdata'])
        except ValueError:
            print("Noutdata not defined")

        try:
            self.sampling = int(Parameters['sampling'])
        except ValueError:
            print("sampling not defined")

        try:
            self.resampling = int(Parameters['resampling'])
        except ValueError:
            print("Resampling factor not defined")

        try:
            self.order = int(Parameters['order'])
        except ValueError:
            print("Filter order not defined")

        self.BLfilter = BLInterpolation(self.Nchannels, self.Noutdata, self.sampling, self.resampling, self.order)

    def Process(self, data):
        self.BLfilter.Input(data)
        if BLfilter.GetDataAvailable() >= self.Noutdata:
            BLfilter.Output(data_ds)
        else:
            print('not enough input data')
        return data_ds
