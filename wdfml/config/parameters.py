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


class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__ ( self, *args, **kwargs ):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__ ( self, attr ):
        return self.get(attr)

    def __setattr__ ( self, key, value ):
        self.__setitem__(key, value)

    def __setitem__ ( self, key, value ):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__ ( self, item ):
        self.__delitem__(item)

    def __delitem__ ( self, key ):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


# class to handle the parameters
class Parameters(object):
    def __init__ ( self, **kwargs ):
        self.__dict__ = kwargs

        def __getattr__ ( self, attr ):
            return self.__dict__[attr]

    def dump ( self, filename ):
        """

        :param filename: name of file where saving the parameters
        :type filename: basestring
        """
        self.filename = filename
        with open(self.filename, mode='w', encoding='utf-8') as f:
            json.dump(self.__dict__, f)

    def load ( self, filename ):
        """

                :param filename: name of file where loading the parameters
                :type filename: basestring
                """
        self.filename = filename
        with open(self.filename) as data_file:
            data = json.load(data_file)
        self.__dict__ = data
        return self.__dict__


class wdfParameters(Parameters):
    def __init__ ( self, window=1, overlap=1, threshold=1.0, sigma=1.0, sampling=1.0 ):
        self.window = window
        self.overlap = overlap
        self.threshold = threshold
        self.sigma = sigma
        self.sampling = sampling
