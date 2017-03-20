__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"
__project__ = 'wdfml'

import json


class parameters(object):
    def __init__(self, window=1, overlap=1, threshold=1, sigma=1, sampling=1):
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

    def dump(self, filename):
        self.filename = filename
        with open(self.filename, mode='w', encoding='utf-8') as f:
            json.dump(self.dict_param, f)

    def load(self, filename):
        self.filename = filename

        with open(self.filename) as data_file:
            data = json.load(data_file)

        parload=self.__init__(data["window"],data["overlap"],data["threshold"],data["sigma"],data["sampling"])
        return parload

