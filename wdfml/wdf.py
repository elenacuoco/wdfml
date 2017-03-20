__author__ ='Elena Cuoco'
__project__ ='wdfml'

import pytsa

class wdf(object):
    def __init__(self, parameters):
        self.parameters = parameters
        self.DetectD = pytsa.WDF2Classify(parameters["window"],
                                          parameters["overlap"],
                                          parameters["threshold"],
                                          parameters["sigma"],
                                          parameters["Ncoeff"])

    def FindEvents(self,data):
        """

        :return: Event over threshold found in the data
        :type data: pytsa.SeqViewDouble()
        :rtype: pytsa.EventFullFeatured
        """
         # to be multiplied by central frequency
        self.trigger = pytsa.EventFullFeatured(self.parameters["Ncoeff"])
        self.DetectD(data,self.parameters["sigma"])
        self.DetectD(self.trigger)
        return self.trigger

