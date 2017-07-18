__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

import logging
import time

from pytsa.tsa import *
from pytsa.tsa import SeqView_double_t as SV

from wdfml.config.parameters import *
from wdfml.observers.ParameterEstimationObserver import *
from wdfml.observers.PrintFilePEObserver import *
from wdfml.observers.SingleEventPrintFileObserver import *
from wdfml.processes.filtering import *
from wdfml.processes.wdf import *
from wdfml.processes.whitening import *

class wdfAdaptiveWorker(object):
    def __init__ ( self, parameters, fullPrint=1 ):
        self.par = Parameters()
        self.par.copy(parameters)
        self.par.Ncoeff = parameters.window
        self.learnlen = 1.5 * float(parameters.learn)
        self.fullPrint = fullPrint
        try:
            self.Alambda = float(parameters.Alambda)
        except:
            logging.error("Adaptive lambda not defined")
        try:
            self.Elambda = float(parameters.Elambda)
        except:
            logging.error("Adaptive Estimation lambda not defined")

    def segmentProcess ( self, segment, wavThresh=WaveletThreshold.dohonojohnston ):
        gpsStart = segment[0]
        gpsEnd = segment[1]
        logging.info("Analyzing segment: %s-%s for channel %s" % (gpsStart, gpsEnd, self.par.channelnel))
        start_time = time.time()
        ID = str(self.par.run) + '_' + str(self.par.channelnel) + '_' + str(int(gpsStart))
        dir_chunk = self.par.outdir + ID + '/'
        # create the output dir
        if not os.path.exists(dir_chunk):
            os.makedirs(dir_chunk)

        strLearn = FrameIChannel(self.par.file, self.par.channelnel, self.learnlen, gpsStart)
        Learn = SV()
        Learn_DS = SV()
        self.par.Noutdata = int(self.par.learn * self.par.resampling)
        ds = downsamplig(self.par)
        strLearn.GetData(Learn)
        ds.Process(Learn, Learn_DS)
        # estimate rough sigma
        y = np.empty(self.par.Noutdata)
        for j in range(self.par.Noutdata):
            y[j] = Learn_DS.GetY(0, j)
        self.par.sigma = np.std(y) * np.std(y) * self.par.resampling

        logging.info('Rough Estimated sigma= %s' % self.par.sigma)
        LSL = LSLLearning(self.par.ARorder, self.par.sigma, self.Elambda)
        ## update the self.parameters to be saved in local json file
        self.par.ID = ID
        self.par.dir = dir_chunk
        self.par.gps = gpsStart
        self.par.gpsStart = gpsStart
        self.par.gpsEnd = gpsEnd

        ######################
        ######################
        # self.parameter for sequence of data and the resampling
        self.par.Noutdata = int(self.par.len * self.par.resampling)
        ds = downsamplig(self.par)
        # gpsstart = gpsStart - self.par.preWhite * self.par.len
        streaming = FrameIChannel(self.par.file, self.par.channelnel, 2 * self.par.len, gpsStart)
        data = SV()
        data_ds = SV()
        dataw = SV()
        ###---preheating---###
        # reading data, downsampling and whitening

        streaming.GetData(data)
        ds.Process(data, data_ds)
        LSL(data_ds, dataw)
        ds.Process(data, data_ds)
        LSL(data_ds, dataw)
        lsl = LSLfilter(LSL, self.Alambda, self.par.Noutdata, False)
        for i in range(self.par.preWhite):
            streaming.GetData(data)
            ds.Process(data, data_ds)
            lsl(data_ds, dataw)

        ### WDF process
        WDF = wdf(self.par, wavThresh)

        # WDF=wdf(self.par)
        ## register obesevers to WDF process
        # put 0 to save only metaself.parameters, 1 for wavelet coefficients and 2 for waveform estimation
        savetrigger = SingleEventPrintTriggers(self.par, self.fullPrint)
        parameterestimation = ParameterEstimation(self.par)
        parameterestimation.register(savetrigger)
        WDF.register(parameterestimation)
        self.par.LSLfile = dir_chunk + "LSLcoeff-AR%s-fs%s-%s.txt" % (
            self.par.ARorder, self.par.resampling, self.par.channelnel)
        filejson = 'parametersUsed.json'
        self.par.dump(self.par.dir + filejson)

        lsl.Save(self.par.LSLfile)
        ###Start detection loop
        logging.info("Starting detection loop")
        while data.GetStart() < gpsEnd:
            streaming.GetData(data)
            ds.Process(data, data_ds)
            lsl(data_ds, dataw)
            WDF.SetData(dataw)
            WDF.Process()

        lsl.Save(self.par.LSLfile)

        elapsed_time = time.time() - start_time
        timeslice = gpsEnd - gpsStart
        logging.info('analyzed %s seconds in %s seconds' % (timeslice, elapsed_time))
        fileEnd = self.par.dir + "ProcessEnded.check"
        open(fileEnd, 'a').close()
