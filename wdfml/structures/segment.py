__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"


class Segment(object):
    def __init__ ( self, start=0, end=1, minSlice=1 ):
        try:
            self.minSlice = float(minSlice)
        except ValueError:
            logging.info("Minimun slice not defined")
        try:
            self.start = float(start)
        except ValueError:
            logging.info("Starting time not defined")
        try:
            self.end = float(end)
        except ValueError:
            logging.info("Ending time not defined")
        try:
            (self.end - self.start) > 0
        except ValueError:
            logging.info("segment lenght is <=0")

        self.segment = [self.start, self.end]

    def isValid ( self ):
        if (self.end - self.start) >= self.minSlice:
            return True
        else:
            return False

    def SetStart ( self, start ):
        self.start = start

    def SetEnd ( self, end ):
        self.end = end

    def GetStart ( self ):
        return self.start

    def GetEnd ( self ):
        return self.end

    def GetSlice ( self ):
        return (self.end - self.start)
