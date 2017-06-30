__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"
import logging
import numpy as np
import time
import pandas as pd
from sklearn.externals import joblib
from wdfml.processes.classify import *

def main ( ):
    logging.basicConfig(level=logging.INFO)
    infile='/users/cuoco/home/CleanWorks/wdfml/output/WDFTrigger-V1:LSC_B1p_DC-GPS1174179689-AR3000-Win1024-Ov900-SNR4.csv'
    triggers = pd.read_csv(infile, index_col=False)
    list_todrop = ['GPSMax', 'GPSstart','WaveletFam']
    triggers = triggers[triggers.SNRMax >= 10]
    new = triggers.drop(list_todrop, axis=1)
    X = np.asarray(new.astype(np.float))
    logging.info(X.shape)
    pca_comp = 10
    spectral_emb = 2
    n_neighbors = 15
    upper_bound=20
    clf=GMMpipeline(X, upper_bound, pca_comp, spectral_emb, n_neighbors)
    joblib.dump(clf, 'pca-gmm.pkl')

if __name__ == '__main__':  # pragma: no cover
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    logging.info('elapsed_time= %s' % elapsed_time)
