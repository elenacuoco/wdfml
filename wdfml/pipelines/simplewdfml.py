import logging
import sys
from pytsa.tsa import *
from pytsa.tsa import SeqView_double_t as SV
import os
import numpy as np
import time
from wdfml.config.parameters import Parameters
from wdfml.processes.whitening import *
from wdfml.processes.filtering import *
from wdfml.processes.wdf import *
from wdfml.observers.observable import Observable
from wdfml.observers.ClusteringObserver import Clustering
from wdfml.observers.PrintFileObserver import PrintTriggers
from wdfml.observers.ClassifierObserver import Classifier
from sklearn.externals import joblib



def main ( ):
    logging.basicConfig(level=logging.INFO)
    logging.info("read Parameters")
    par = Parameters()
    par.load("fileParameters.json")
    # logging.info(par.__dict__)
    # Parameter for sequence of data
    gpsE = float(par.gpsStart) + 10.0
    Learn = SV()
    Learn_DS = SV()
    # logging.info(par.sampling, par.resampling)

    # parameter for whitening and its estimation parameters
    whiten = Whitening(par.ARorder)
    ###Name of the files where the whitening parameters are saved
    LVfile = "./ARparameters/LVstate_%s_%s_%s.txt" % (par.ARorder, par.channel, int(par.gps))
    ARfile = "./ARparameters/ARstate_%s_%s_%s.txt" % (par.ARorder, par.channel, int(par.gps))
    if par.estimation == "True":
        logging.info('Start AR parameter estimation')
        ######## read data for AR estimation###############
        learnlen = 2.0 * float(par.learn)
        strLearn = FrameIChannel(par.file, par.channel, learnlen, gpsE)
        par.Noutdata = int(par.learn * par.resampling)
        ds = downsamplig(par)
        strLearn.GetData(Learn)
        ds.Process(Learn, Learn_DS)
        whiten.ParametersEstimate(Learn_DS)
        whiten.ParametersSave(ARfile, LVfile)
    else:
        logging.info('Load AR parameter')
        whiten.ParametersLoad(ARfile, LVfile)

    ######################
    # Parameter for sequence of data
    # read data
    par.Noutdata = int(par.len * par.resampling)
    ds = downsamplig(par)
    gpsstart = par.gpsStart - par.len
    streaming = FrameIChannel(par.file, par.channel, par.lenStart, gpsstart)
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
    logging.info('Estimated sigma= %s' % par.sigma)
    par.Ncoeff = par.window

    ###Start detection loop
    logging.info("Starting detection loop")

    streaming.SetDataLength(par.len)
    startT = data.GetStart()
    ## gpsEnd=par.gpsEnd +par.lenStart
    clf = joblib.load('./pipelines/pca-gmm.pkl')
    WDF = wdf(par)

    observable = Observable()
    observableO = Observable()
    clustering = Clustering(par)
    savetrigger = PrintTriggers(par)
    classifier=Classifier(par,clf)
    observable.register(clustering)
    observableO.register(savetrigger)
    observableO.register(classifier)
    while data.GetStart() < par.gpsEnd:
        streaming.GetData(data)
        ds.Process(data, data_ds)
        whiten.Process(data_ds, dataw)
        WDF.SetData(dataw)
        while WDF.wdf2classify.GetDataNeeded() > 0:
            ev = WDF.FindEvents()
            observable.update_observers(ev)
            cev=clustering.CEV
            observableO.update_observers(cev)
    logging.info(classifier.classified)
    logging.info('Program terminated')
    par.dump("fileParametersUsed.json")


if __name__ == '__main__':  # pragma: no cover
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    logging.info('elapsed_time= %s' % elapsed_time)
