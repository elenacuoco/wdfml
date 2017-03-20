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

# class to handle the parameters
class Parameters(object):

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def dump(self, filename):

        self.filename = filename
        with open(self.filename, mode='w', encoding='utf-8') as f:
            json.dump(self.__dict__, f)

    def load(self, filename):
        self.filename = filename
        with open(self.filename) as data_file:
            data = json.load(data_file)
        self.__dict__ = data
        return self.__dict__
