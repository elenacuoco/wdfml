__author__ ='Elena Cuoco'
__project__ ='wdfml'

import pytsa

class wdf(object):
    def __init__(self, parameters):
        self.parameters = parameters
        """

                     :type sigma: float
                     :type threshold: float
                     :type sampling: float
                     :type overlap: int
                     :type window: int

                     """
        self.dict_param = {}
        self.dict_param['window'] = window
        self.dict_param['overlap'] = overlap
        self.dict_param['threshold'] = threshold
        self.dict_param['sigma'] = sigma
        self.dict_param['sampling'] = sampling
        self.dict_param['Ncoeff'] = window

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

