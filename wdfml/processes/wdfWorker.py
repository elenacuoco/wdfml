__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"
from pytsa.tsa import *
from pytsa.tsa import SeqView_double_t as SV
from wdfml.config.parameters import *
from wdfml.observers.ClusteringObserver import Clustering
from wdfml.observers.PrintFilePEObserver import *
from wdfml.observers.ParameterEstimationObserver import *
from wdfml.observers.ClusteredPrintFileObserver import *
from wdfml.processes.filtering import *
from wdfml.processes.wdf import *
from wdfml.processes.whitening import *
import time


class wdfWorker(object):
    def __init__ ( self, parameters ):
        self.par = Parameters()
        self.par.copy(parameters)
        #self.par.deltaT = 1.5 * (parameters.window - parameters.overlap) / parameters.resampling
        self.par.Ncoeff = parameters.window
        self.learnlen = 1.5 * float(parameters.learn)

    def segmentProcess ( self, segment ):
        gpsStart = segment[0]
        gpsEnd = segment[1]
        logging.info("Analyzing segment: %s-%s for channel %s" % (gpsStart, gpsEnd, self.par.channel))
        start_time = time.time()
        ID = str(self.par.run) + "_" + str(self.par.channel) + '_' + str(int(gpsStart))
        dir_chunk = self.par.outdir + ID + '/'
        # create the output dir
        if not os.path.exists(dir_chunk):
            os.makedirs(dir_chunk)
        # self.parameter for whitening and its estimation self.parameters
        whiten = Whitening(self.par.ARorder)
        self.par.ARfile = dir_chunk + "ARcoeff-AR%s-fs%s-%s.txt" % (
            self.par.ARorder, self.par.resampling, self.par.channel)
        self.par.LVfile = dir_chunk + "LVcoeff-AR%s-fs%s-%s.txt" % (
            self.par.ARorder, self.par.resampling, self.par.channel)

        if os.path.isfile(self.par.ARfile) and os.path.isfile(self.par.LVfile):
            logging.info('Load AR self.parameter')
            whiten.ParametersLoad(self.par.ARfile, self.par.LVfile)
        else:
            logging.info('Start AR self.parameter estimation')
            ######## read data for AR estimation###############
            # self.parameter for sequence of data.
            # Add a 10.0 seconds delay to not include too much after lock noise in the estimation
            gpsE = gpsStart + 10.0

            strLearn = FrameIChannel(self.par.file, self.par.channel, self.learnlen, gpsE)
            Learn = SV()
            Learn_DS = SV()
            self.par.Noutdata = int(self.par.learn * self.par.resampling)
            ds = downsamplig(self.par)
            strLearn.GetData(Learn)
            ds.Process(Learn, Learn_DS)
            whiten.ParametersEstimate(Learn_DS)
            whiten.ParametersSave(self.par.ARfile, self.par.LVfile)
            del Learn, ds, strLearn, Learn_DS
        # sigma for the noise
        self.par.sigma = 2.0 * whiten.GetSigma()
        logging.info('Estimated sigma= %s' % self.par.sigma)
        ## update the self.parameters to be saved in local json file
        self.par.ID = ID
        self.par.dir = dir_chunk
        self.par.gps = gpsStart
        self.par.gpsStart = gpsStart
        self.par.gpsEnd = gpsEnd
        self.par.chan = self.par.channel
        ######################
        # self.parameter for sequence of data and the resampling
        self.par.Noutdata = int(self.par.len * self.par.resampling)
        ds = downsamplig(self.par)
        gpsstart = gpsStart - self.par.preWhite * self.par.len
        streaming = FrameIChannel(self.par.file, self.par.channel, self.par.len, gpsstart)
        data = SV()
        data_ds = SV()
        dataw = SV()
        ###---preheating---###
        # reading data, downsampling and whitening
        for i in range(self.par.preWhite):
            streaming.GetData(data)
            ds.Process(data, data_ds)
            whiten.Process(data_ds, dataw)
        ### WDF process
        WDF = wdf(self.par, WaveletThreshold.dohonojohnston)
        # WDF=wdf(self.par)
        ## register obesevers to WDF process

        clustering = Clustering(self.par)
        # put 0 to save only metaself.parameters, 1 for wavelet coefficients and 2 for waveform estimation
        savetrigger = PrintClusteredTriggers(self.par, fullPrint=1)
        parameterestimation = ParameterEstimation(self.par)
        parameterestimation.register(clustering)
        clustering.register(savetrigger)
        WDF.register(parameterestimation)
        filejson = 'parametersUsed.json'
        self.par.dump(self.par.dir + filejson)
        ###Start detection loop
        logging.info("Starting detection loop")

        while data.GetStart() < gpsEnd:
            streaming.GetData(data)
            ds.Process(data, data_ds)
            whiten.Process(data_ds, dataw)
            WDF.SetData(dataw)
            WDF.Process()

        elapsed_time = time.time() - start_time
        timeslice = gpsEnd - gpsStart
        logging.info('analyzed %s seconds in %s seconds' % (timeslice, elapsed_time))
