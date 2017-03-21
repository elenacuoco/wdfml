__author__ = 'Elena Cuoco'
__project__ = 'wdfml'


from pytsa.tsa import *

class  wdf(object):
    def __init__(self, parameters):
        """

        :type parameters: class Parameters
        """
        self.parameters = parameters
        self.parameters['Ncoeff'] = self.parameters['window']
        self.DetectD = WDF2Classify(self.parameters["window"],
                                          self.parameters["overlap"],
                                          self.parameters["threshold"],
                                          self.parameters["sigma"],
                                          self.parameters["Ncoeff"])

    def FindEvents(self, data):
        """

        :return: Event over threshold found in the data
        :type data: pytsa.SeqViewDouble()
        :rtype: pytsa.EventFullFeatured
        """
        # to be multiplied by central frequency
        self.trigger = EventFullFeatured(self.parameters["Ncoeff"])
        self.DetectD(data, self.parameters["sigma"])
        self.DetectD(self.trigger)
        return self.trigger
