__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

import time

from pytsa.tsa import *
from pytsa.tsa import SeqView_double_t as SV

from wdfml.config.parameters import *
from wdfml.observers.ParameterEstimationObserver import *
from wdfml.observers.SingleEventPrintFileObserver import *
from wdfml.processes.wdf import *


class wdfAdaptiveWorker(object):
    def __init__(self, parameters, fullPrint=1):
        self.par = Parameters()
        self.par.copy(parameters)
        self.par.Ncoeff = parameters.window
        self.len = float(parameters.len)
        self.fullPrint = fullPrint
        self.sampling = parameters.sampling
        self.par.resampling = parameters.sampling

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
            streaming = FrameIChannel(self.par.file, self.par.channel, self.len, gpsStart)

            ndata = int(self.len * self.sampling)
            logging.info(ndata)
            # estimate rough sigma
            y = np.empty(ndata)
            data = SV()
            streaming.GetData(data)
            for j in range(ndata):
                y[j] = data.GetY(0, j)

            self.par.sigma = np.std(y) * np.std(y) * self.sampling
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
            # reading data and whitening
            dataw = SV()

            streaming.GetData(data)
            LSL(data, dataw)
            self.par.sigma = LSL.GetSigma()
            logging.info('LSL Estimated sigma= %s' % self.par.sigma)
            lsl = LSLfilter(LSL, self.Alambda, ndata, False)
            for i in range(self.par.preWhite):
                streaming.GetData(data)
                lsl(data, dataw)

            self.par.sigma = lsl.GetSigma(ndata - 1)
            logging.info('lsl Estimated sigma= %s' % self.par.sigma)
            self.par.LSLfile = dir_chunk + "LSLcoeff-AR%s-fs%s-%s.txt" % (
                self.par.ARorder, self.par.sampling, self.par.channel)
            lsl.Save(self.par.LSLfile)
            filejson = 'parametersUsed.json'
            self.par.dump(self.par.dir + filejson)

            ### WDF process
            WDF = wdf(self.par, wavThresh)

            ## register obesevers to WDF process
            # put 0 to save only metaself.parameters, 1 for wavelet coefficients and 2 for waveform estimation
            savetrigger = SingleEventPrintTriggers(self.par, self.fullPrint)

            parameterestimation = ParameterEstimation(self.par)

            parameterestimation.register(savetrigger)

            WDF.register(parameterestimation)


            ###Start detection loop
            logging.info("Starting detection loop")
            while data.GetStart() < gpsEnd:
                streaming.GetData(data)
                lsl(data, dataw)
                WDF.SetData(dataw)
                WDF.Process()
            lsl.Save(self.par.LSLfile)
            elapsed_time = time.time() - start_time
            timeslice = gpsEnd - gpsStart
            logging.info('analyzed %s seconds in %s seconds' % (timeslice, elapsed_time))
            fileEnd = self.par.dir + "ProcessEnded.check"
            open(fileEnd, 'a').close()
