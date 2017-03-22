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


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("read Parameters")
    par = Parameters()
    par.load("fileParameters.json")
    # print(par.__dict__)
    # Parameter for sequence of data
    gpsE = float(par.gps) + 10.0
    Learn = SV()
    Learn_DS = SV()
    # print(par.sampling, par.resampling)

    # parameter for whitening and its estimation parameters
    whiten = Whitening(par.ARorder)
    ID = str(par.chan)+'_'+str(par.gps)
    par.outdir = par.outdir + ID + '/'
    if not os.path.exists(par.outdir):
        os.makedirs(par.outdir)
    par.ID = ID
    par.ARfile = par.outdir + "ARfile.txt"
    par.LVfile = par.outdir + "LVfile.txt"

    if os.path.isfile(par.ARfile) and os.path.isfile(par.LVfile):
        logging.info('Load AR parameter')
        whiten.ParametersLoad(par.ARfile, par.LVfile)
    else:
        logging.info('Start AR parameter estimation')
        ######## read data for AR estimation###############
        learnlen = 2.0 * float(par.learn)
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

    ###Start detection loop
    print("Starting detection loop")

    streaming.SetDataLength(par.len)
    startT = data.GetStart()
    ## gpsEnd=par.gpsEnd +par.lenStart

    WDF = wdf(par)

    observable = Observable()
    observableO = Observable()
    clustering = Clustering(par)
    savetrigger = PrintTriggers(par)
    observable.register(clustering)
    observableO.register(savetrigger)

    while data.GetStart() < par.gpsEnd:
        streaming.GetData(data)
        ds.Process(data, data_ds)
        whiten.Process(data_ds, dataw)
        WDF.SetData(dataw)
        while WDF.wdf2classify.GetDataNeeded() > 0:
            ev = WDF.FindEvents()
            observable.update_observers(ev)
            cev = clustering.CEV
            if (cev != None and cev.mTime > 0.0):
                observableO.update_observers(cev)

    print('Program terminated')
    par.dump(par.outdir + "fileParametersUsed.json")


if __name__ == '__main__':  # pragma: no cover
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    print('elapsed_time= %s' % elapsed_time)
