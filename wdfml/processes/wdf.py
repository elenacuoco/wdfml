__author__ = 'Elena Cuoco'
__project__ = 'wdfml'


from pytsa.tsa import *

class wdf(object):
    def __init__(self, parameters):
        """

        :type parameters: class Parameters
        """
        self.parameters = parameters

        self.wdf2classify = WDF2Classify(self.parameters.window,
                                          self.parameters.overlap,
                                          self.parameters.threshold,
                                          self.parameters.sigma,
                                          self.parameters.Ncoeff)
        self.trigger = EventFullFeatured(self.parameters.Ncoeff)





    def FindEvents (self,data):
        """

        :return: Event over threshold found in the data
        :type data: pytsa.SeqViewDouble()
        :rtype: pytsa.EventFullFeatured
        """
        # to be multiplied by central frequency
        self.wdf2classify(data, self.parameters.sigma)
        self.wdf2classify(self.trigger)
        return self.trigger
