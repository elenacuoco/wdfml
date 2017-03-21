import logging
import sys
from pytsa.tsa import *
from pytsa.tsa import SeqView_double_t as SV
import os
import numpy as np
import time
from wdfml.config.parameters import Parameters
from wdfml.processes.whitening import *
from wdfml.processes.wdf import *
def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("read Parameters")
    par = Parameters()
    par.load("fileParameters.json")
    print(par.__dict__)
    # Parameter for sequence of data
    par.Nchannels = 1
    gpsE = float(par.gpsStart) + 10.0
    strLearn = FrameIChannel(par.file, par.chan, 1.0, gpsE)
    # Parameter for AR estimation
    Learn = SV()
    strLearn.GetData(Learn)
    sampling = int(1.0 / Learn.GetSampling())
    par.sampling = sampling
    resampling = int(sampling / 2)
    par.resampling = resampling
    print(sampling, resampling)

    learnlen = 2.0 * float(par.learn)
    Learn_DS = SV()
    Noutdata = int(par.learn * resampling)
    order = 9
    par.BLfilter_order = order
    strLearn = FrameIChannel(par.file, par.chan, learnlen, gpsE)
    # Parameter for AR estimation
    Learn = SV()
    strLearn.GetData(Learn)
    bf_estimation = BLInterpolation(par.Nchannels, Noutdata, sampling, resampling, order)
   # parameter for whitening and its estimation parameters
    whiten=Whitening(par.ARorder)
    ###Name of the files where the whitening parameters are saved
    LVfile = "./ARparameters/LVstate_%s_%s_%s.txt" % (par.ARorder, par.chan, int(par.gps))
    ARfile = "./ARparameters/ARstate_%s_%s_%s.txt" % (par.ARorder, par.chan, int(par.gps))
    if par.estimation=="True":
        logging.info('Start AR parameter estimation')
        strLearn.GetData(Learn)
        bf_estimation.Input(Learn)
        if bf_estimation.GetDataAvailable() >= Noutdata:
            bf_estimation.Output(Learn_DS)
        else:
            print('not enough input data')
        ADE,LV=whiten.ParametersEstimate(Learn_DS)
        whiten.ParametersSave(ARfile,LVfile)
        LF = whiten.initLatticeFilter()
    else:
        logging.info('Load AR parameter')
        ADE,LV=whiten.ParametersLoad(ARfile,LVfile)
        LF = whiten.initLatticeFilter()

    del Learn, bf_estimation, Learn_DS, strLearn
    ######################
    # Parameter for sequence of data
    # read data
    nout = int(par.len * resampling)
    bf = BLInterpolation(par.Nchannels, nout, sampling, resampling, order)
    gpsstart = par.gpsStart - par.len
    streaming = FrameIChannel(par.file, par.chan, par.lenStart, gpsstart)
    data = SV()
    data_ds = SV()
    dataw = SV()

    ###---preheating---###

    streaming.GetData(data)
    bf.Input(data)
    bf.Output(data_ds)
    LF(data_ds, dataw)

    ### WDF process
    # sigma for the noise
    par.sigma = ADE.GetAR(0)
    print('Estimated sigma= %s' % par.sigma)
    par.Ncoeff = par.window
    WDF=wdf(par)

    # event class
    Ncoeff = par.Ncoeff
    outfile = par.outdir + 'WDFTrigger-%s-GPS%s-AR%s-Win%s-Ov%s-SNR%s.csv' % (
        par.chan, int(par.gpsStart), par.ARorder, par.window, par.overlap, int(par.threshold))
    f = open(outfile, 'a')
    logging.info('Starting WDF process')

    stringa = 'GPSMax,SNRMax,FreqMax,WaveletFam'
    for i in range(Ncoeff):
        stringa += ',' + 'WavCoeff' + str(i)
    stringa += '\n'
    f.write(stringa)

    ###Start detection loop
    print("Starting detection loop")

    factorF = resampling / (2.0 * par.window);
    streaming.SetDataLength(par.len)
    startT = data.GetStart()
    ## gpsEnd=par.gpsEnd +par.lenStart
    Nevents=0
    while data.GetStart() < par.gpsEnd:
        if bf.GetDataAvailable() <= nout:
            # bf.DelData(data)
            streaming.GetData(data)
            bf.Input(data)
        bf.Output(data_ds)
        LF(data_ds, dataw)

        while WDF.wdf2classify.GetDataNeeded() > 0:
            ev=WDF.FindEvents(dataw)
            frequency = ev.mlevel * factorF
            stringa = repr(ev.mTime) + ',' + repr(ev.mSNR) + ',' + repr(frequency) + ','+ repr(ev.mWave)
            for i in range(0, Ncoeff):
                stringa += ',' + repr(ev.GetCoeff(i))
            stringa += '\n'
            f.write(stringa)
            f.flush()
            Nevents += 1
            del ev


    f.close()

    print('Program terminated. Done %d seconds, found %s Events.' % (par.gpsEnd - startT, Nevents))

    par.dump("fileParametersUsed.json")


if __name__ == '__main__':  # pragma: no cover
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    print('elapsed_time= %s' % elapsed_time)
