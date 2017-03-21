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

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("read Parameters")
    par = Parameters()
    par.load("fileParameters.json")
    #print(par.__dict__)

    # Parameter for sequence of data
    gpsE = float(par.gpsStart) + 10.0
    Learn = SV()
    Learn_DS = SV()
    #print(par.sampling, par.resampling)

   # parameter for whitening and its estimation parameters
    whiten=Whitening(par.ARorder)
    ###Name of the files where the whitening parameters are saved
    LVfile = "./ARparameters/LVstate_%s_%s_%s.txt" % (par.ARorder, par.chan, int(par.gps))
    ARfile = "./ARparameters/ARstate_%s_%s_%s.txt" % (par.ARorder, par.chan, int(par.gps))
    if par.estimation=="True":
        logging.info('Start AR parameter estimation')
        ######## read data for AR estimation###############
        learnlen = 2.0 * float(par.learn)
        strLearn = FrameIChannel(par.file, par.chan, learnlen, gpsE)
        par.Noutdata = int(par.learn * par.resampling)
        ds = downsamplig(par)
        strLearn.GetData(Learn)
        ds.Process(Learn,Learn_DS)
        whiten.ParametersEstimate(Learn_DS)
        whiten.ParametersSave(ARfile,LVfile)
    else:
        logging.info('Load AR parameter')
        whiten.ParametersLoad(ARfile,LVfile)

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
    ds.Process(data,data_ds)
    whiten.Process(data_ds,dataw)
    ### WDF process
    # sigma for the noise
    par.sigma = whiten.GetSigma()
    print('Estimated sigma= %s' % par.sigma)
    par.Ncoeff = par.window


    ##listener
    outfile = par.outdir + 'WDFTrigger-%s-GPS%s-AR%s-Win%s-Ov%s-SNR%s.csv' % (
        par.chan, int(par.gpsStart), par.ARorder, par.window, par.overlap, int(par.threshold))
    f = open(outfile, 'a')
    logging.info('Starting WDF process')
    stringa = 'GPSMax,SNRMax,FreqMax,WaveletFam'
    for i in range(par.Ncoeff):
        stringa += ',' + 'WavCoeff' + str(i)
    stringa += '\n'
    f.write(stringa)
   #############
    ###Start detection loop
    print("Starting detection loop")
    factorF = par.resampling / (2.0 * par.window);
    streaming.SetDataLength(par.len)
    startT = data.GetStart()
    ## gpsEnd=par.gpsEnd +par.lenStart
    Nevents=0
    WDF = wdf(par)
    while data.GetStart() < par.gpsEnd:
        streaming.GetData(data)
        ds.Process(data,data_ds)
        whiten.Process(data_ds, dataw)
        WDF.SetData(dataw)
        while WDF.wdf2classify.GetDataNeeded() > 0:
            ev=WDF.FindEvents()
            frequency = ev.mlevel * factorF
            ##listener
            stringa = repr(ev.mTime) + ',' + repr(ev.mSNR) + ',' + repr(frequency) + ','+ repr(ev.mWave)
            for i in range(0, par.Ncoeff):
                stringa += ',' + repr(ev.GetCoeff(i))
            stringa += '\n'
            f.write(stringa)
            f.flush()
            Nevents += 1
            del ev
            ############

    f.close()
    print('Program terminated. Done %d seconds, found %s Events.' % (par.gpsEnd - startT, Nevents))
    par.dump("fileParametersUsed.json")


if __name__ == '__main__':  # pragma: no cover
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    print('elapsed_time= %s' % elapsed_time)

