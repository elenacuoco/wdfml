__author__ = 'Elena Cuoco'
__project__ = 'wdfml'

from pytsa.tsa import *

from  wdfml.observers.observable import *


class wdf(Observable):
    def __init__ ( self, parameters, wTh=WaveletThreshold.dohonojohnston):
        """
        :type parameters: class Parameters
        """
        Observable.__init__(self)
        self.parameters = parameters
        self.wdf2classify = WDF2Classify(self.parameters.window,
                                         self.parameters.overlap,
                                         self.parameters.threshold,
                                         self.parameters.sigma,
                                         self.parameters.Ncoeff,
                                         wTh)
        self.trigger = EventFullFeatured(self.parameters.Ncoeff)

    def SetData ( self, data ):
        """
        :return: Event over threshold found in the data
        :type data: pytsa.SeqViewDouble()
        :rtype: pytsa.EventFullFeatured
        """
        # to be multiplied by central frequency

        self.wdf2classify(data, self.parameters.sigma)
        return

    def FindEvents ( self ):
        """
        :return: Event over threshold found in the data
        :type data: pytsa.SeqViewDouble()
        :rtype: pytsa.EventFullFeatured
        """
        # to be multiplied by central frequency
        self.wdf2classify(self.trigger)
        return self.trigger

    def Process ( self ):
        while self.wdf2classify.GetDataNeeded() > 0:
            self.wdf2classify(self.trigger)
            if self.trigger.mWave != '':
                self.update_observers(self.trigger)
