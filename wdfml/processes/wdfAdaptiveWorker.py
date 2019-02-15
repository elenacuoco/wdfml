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
from wdfml.observers.SingleEventPrintFileObserver import *
from wdfml.processes.filtering import *
from wdfml.processes.wdf import *


class wdfAdaptiveWorker(object):
    def __init__(self, parameters, fullPrint=1):
        self.par = Parameters()
        self.par.copy(parameters)
        self.par.Ncoeff = parameters.window
        self.learn = 20.0 * float(parameters.len)
        self.lenin = 2.0 * float(parameters.len)
        self.fullPrint = fullPrint
        try:
            self.Alambda = float(parameters.Alambda)
        except:
            logging.error("Adaptive lambda not defined")
        try:
            self.Elambda = float(parameters.Elambda)
        except:
            logging.error("Adaptive Estimation lambda not defined")

    def segmentProcess(self, segment, wavThresh=WaveletThreshold.dohonojohnston):
        gpsStart = segment[0]
        gpsEnd = segment[1]
        logging.info("Analyzing segment: %s-%s for channel %s" % (gpsStart, gpsEnd, self.par.channel))
        start_time = time.time()
        ID = str(self.par.run) + '_' + str(self.par.channel) + '_' + str(int(gpsStart))
        dir_chunk = self.par.outdir + ID + '/'
        # create the output dir
        if not os.path.exists(dir_chunk):
            os.makedirs(dir_chunk)
        if not os.path.isfile(dir_chunk + 'ProcessEnded.check'):
            streaming = FrameIChannel(self.par.file, self.par.channel, self.learn, gpsStart)
            data = SV()
            data_ds = SV()
            dataw = SV()
            self.par.Noutdata = int(10 * self.par.len * self.par.resampling)
            ds = downsamplig(self.par)
            streaming.GetData(data)
            ds.Process(data, data_ds)
            streaming.GetData(data)
            ds.Process(data, data_ds)
            # estimate rough sigma
            y = np.empty(self.par.Noutdata)
            for j in range(self.par.Noutdata):
                y[j] = data_ds.GetY(0, j)
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
            ###---preheating---###
            # reading data, downsampling and whitening
            self.par.Noutdata = int(self.par.len * self.par.resampling)
            gpsstart = data.GetStart()
            streaming = FrameIChannel(self.par.file, self.par.channel, self.lenin, gpsstart)
            ds = downsamplig(self.par)
            streaming.GetData(data)
            ds.Process(data, data_ds)
            LSL(data_ds, dataw)
            ds.Process(data, data_ds)
            LSL(data_ds, dataw)
            lsl = LSLfilter(LSL, self.Alambda, self.par.Noutdata, False)
            for i in range(self.par.preWhite):
                #streaming.GetData(data)
                ds.Process(data, data_ds)
                lsl(data_ds, dataw)

            self.par.sigma = lsl.GetSigma(self.par.Noutdata - 1)
            logging.info('LSL Estimated sigma= %s' % self.par.sigma)
            self.par.LSLfile = dir_chunk + "LSLcoeff-AR%s-fs%s-%s.txt" % (
                self.par.ARorder, self.par.resampling, self.par.channel)
            lsl.Save(self.par.LSLfile)
            ### WDF process
            WDF = wdf(self.par, wavThresh)

            ## register obesevers to WDF process
            # put 0 to save only metaself.parameters, 1 for wavelet coefficients and 2 for waveform estimation
            savetrigger = SingleEventPrintTriggers(self.par, self.fullPrint)
            parameterestimation = ParameterEstimation(self.par)
            parameterestimation.register(savetrigger)
            WDF.register(parameterestimation)

            filejson = 'parametersUsed.json'
            self.par.dump(self.par.dir + filejson)
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
