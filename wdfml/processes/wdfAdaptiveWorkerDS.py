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


class wdfAdaptiveWorkerDS(object):
    def __init__(self, parameters, fullPrint=1):
        self.par = Parameters()
        self.par.copy(parameters)
        self.par.Ncoeff = parameters.window
        self.learn = 10 * float(parameters.len)

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
        logging.info("Analyzing segment: %s-%s for channel %s downslampled at %dHz" % (
            gpsStart, gpsEnd, self.par.channel, self.par.resampling))
        start_time = time.time()
        ID = str(self.par.run) + '_' + str(self.par.channel) + '_' + str(int(gpsStart))
        dir_chunk = self.par.outdir + ID + '/'
        self.par.LSLfile = dir_chunk + "LSLcoeff-AR%s-fs%s-%s.txt" % (
            self.par.ARorder, self.par.resampling, self.par.channel)
        # create the output dir
        if not os.path.exists(dir_chunk):
            os.makedirs(dir_chunk)
        if not os.path.isfile(dir_chunk + 'ProcessEnded.check'):
            if os.path.isfile(self.par.LSLfile):
                logging.info('Load LSL parameter')
                LSL = LSLLearning(self.par.ARorder, 1.0, self.Elambda)
                LSL.Load(self.par.LSLfile)
            else:
                logging.info('Start LSL parameter estimation')
                streamL = FrameIChannel(self.par.file, self.par.channel, self.learn, gpsStart)
                data = SV()
                data_ds = SV()
                self.par.Noutdata = int(5 * self.par.len * self.par.resampling)
                dsL = downsamplig(self.par)
                self.par.sigma = 0.0
                while self.par.sigma == 0.0:
                    streamL.GetData(data)
                    dsL.Process(data, data_ds)
                    # estimate rough sigma
                    y = np.empty(self.par.Noutdata)
                    for j in range(self.par.Noutdata):
                        y[j] = data_ds.GetY(0, j)
                    self.par.sigma = np.std(y) * np.std(y) * self.par.resampling

                logging.info('Rough Estimated sigma= %s' % self.par.sigma)
                LSL = LSLLearning(self.par.ARorder, self.par.sigma, self.Elambda)
                dataw = SV()
                ######################
                streamL.GetData(data)
                dsL.Process(data, data_ds)
                LSL(data_ds, dataw)
                LSL.Save(self.par.LSLfile)
                del data, data_ds, dataw, dsL, streamL
            self.par.sigma = np.sqrt(LSL.GetSigma())
            # sigma for the noise
            logging.info('LSL Estimated sigma= %s' % self.par.sigma)

            ## update the self.parameters to be saved in local json file
            self.par.ID = ID
            self.par.dir = dir_chunk
            self.par.gps = gpsStart
            self.par.gpsStart = gpsStart
            self.par.gpsEnd = gpsEnd

            ######################
            # self.parameter for sequence of data and the resampling
            self.par.Noutdata = int(self.par.len * self.par.resampling)
            ds = downsamplig(self.par)
            # gpsstart = gpsStart - self.par.preWhite * self.par.len
            streaming = FrameIChannel(self.par.file, self.par.channel, self.par.len, gpsStart)
            data = SV()
            data_ds = SV()
            dataw = SV()
            lsl = LSLfilter(LSL, self.Alambda, self.par.Noutdata, False)
            ###---preheating---###
            # reading data, downsampling and whitening
            streaming.GetData(data)
            ds.Process(data, data_ds)
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

            elapsed_time = time.time() - start_time
            timeslice = gpsEnd - gpsStart
            logging.info('analyzed %s seconds in %s seconds' % (timeslice, elapsed_time))
            fileEnd = self.par.dir + "ProcessEnded.check"
            open(fileEnd, 'a').close()
        else:
            logging.info('Segment already processed')