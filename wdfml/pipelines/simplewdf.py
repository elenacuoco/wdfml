import logging
import time
import os
from pytsa.tsa import *
from pytsa.tsa import SeqView_double_t as SV

from wdfml.config.parameters import Parameters
from wdfml.observers.ClusteringObserver import Clustering
from wdfml.observers.PrintFileObserver import PrintTriggers
from wdfml.observers.observable import Observable
from wdfml.processes.filtering import *
from wdfml.processes.wdf import *
from wdfml.processes.whitening import *


def main(param):
    start_time = time.time()
    logging.basicConfig(level=logging.INFO)
    logging.info("read Parameters")
    par = Parameters()
    par.load(param)
    ID = str(par.chan) + '_' + str(par.gps)
    par.outdir = par.outdir + ID + '/'
    if not os.path.exists(par.outdir):
        os.makedirs(par.outdir)
    par.ID = ID

    # parameter for whitening and its estimation parameters
    whiten = Whitening(par.ARorder)
    par.ARfile = par.outdir + "ARfile.txt"
    par.LVfile = par.outdir + "LVfile.txt"

    if os.path.isfile(par.ARfile) and os.path.isfile(par.LVfile):
        logging.info('Load AR parameter')
        whiten.ParametersLoad(par.ARfile, par.LVfile)
    else:
        logging.info('Start AR parameter estimation')
        ######## read data for AR estimation###############
        # Parameter for sequence of data
        gpsE = float(par.gps) + 10.0
        Learn = SV()
        Learn_DS = SV()
        learnlen = 2.0 * float(par.learn)
        strLearn = FrameIChannel(par.file, par.chan, 1.0, gpsE)
        strLearn.GetData(Learn)

        par.sampling = int(1.0 / Learn.GetSampling())
        par.resampling = int(sampling / 2)

        strLearn = FrameIChannel(par.file, par.chan, learnlen, gpsE)
        par.Noutdata = int(par.learn * par.resampling)
        ds = downsamplig(par)
        strLearn.GetData(Learn)
        ds.Process(Learn, Learn_DS)
        whiten.ParametersEstimate(Learn_DS)
        whiten.ParametersSave(par.ARfile, par.LVfile)

    ######################
    # Parameter for sequence of data
    # read data
    par.Noutdata = int(par.len * par.resampling)
    ds = downsamplig(par)
    gpsstart = par.gpsStart - par.len
    streaming = FrameIChannel(par.file, par.chan, par.lenStart, gpsstart)
    data = SV()
    data_ds = SV()
    dataw = SV()
    ###---preheating---###
    streaming.GetData(data)
    ds.Process(data, data_ds)
    whiten.Process(data_ds, dataw)
    ### WDF process
    # sigma for the noise
    par.sigma = whiten.GetSigma()
    print('Estimated sigma= %s' % par.sigma)
    par.Ncoeff = par.window
    streaming.SetDataLength(par.len)

    WDF = wdf(par)
    clustering = Clustering(par)
    savetrigger = PrintTriggers(par)
    clustering.register(savetrigger)
    WDF.register(clustering)
    ###Start detection loop
    print("Starting detection loop")
    while data.GetStart() < par.gpsEnd:
        streaming.GetData(data)
        ds.Process(data, data_ds)
        whiten.Process(data_ds, dataw)
        WDF.SetData(dataw)
        WDF.Process()
    print('Program terminated')
    par.dump(par.outdir + "fileParametersUsed.json")
    elapsed_time = time.time() - start_time
    timeslice=par.gpsEnd-par.gpsStart
    print('analyzed %s seconds in %s seconds' % (timeslice,elapsed_time))

if __name__ == '__main__':  # pragma: no cover
    main()

