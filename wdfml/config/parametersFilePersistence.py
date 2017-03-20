__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

import json


class ParametersFilePersistence(object):
    def __init__(self, parameters):
        self.__dict__ = parameters.__dict__

    def dump(self, filename):
        self.filename = filename
        with open(self.filename, mode='w', encoding='utf-8') as f:
            json.dump(self.__dict__, f)

    def load(self, filename):
        self.filename = filename
        with open(self.filename) as data_file:
            self.__dict__ = json.load(data_file)
        return self.__dict__
