__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"
import logging

from wdfml.observers.observer import Observer
from pytsa.tsa import *
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Classifier(Observer):
    def __init__ ( self, parameters, clf ):
        """

        :rtype: list containing the classified triggers
        """
        self.parameters = parameters
        self.clf = clf
        self.label = 0
        self.nfeatures = self.parameters.Ncoeff + 3  # adding SNR,Freq and duration
        self.features = np.empty(self.nfeatures)
        self.classified = []

    def update ( self, Cev ):
        for i in range(self.parameters.Ncoeff):
            self.features[i] = Cev.GetCoeff(i)
        self.features[self.parameters.Ncoeff] = Cev.mSNR
        self.features[self.parameters.Ncoeff + 1] = Cev.mlevel
        self.features[self.parameters.Ncoeff + 2] = Cev.mLenght
        self.label = self.clf.predict(np.asarray(self.features))
        self.classified.append([Cev.mTime, Cev.mTimeMax, Cev.mLenght, Cev.mlevel, Cev.mSNR, self.label])
