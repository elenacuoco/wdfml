__author__ = 'Elena Cuoco'
__project__ = 'wdfml'

from pytsa.tsa import *
from pytsa.tsa import SeqView_double_t as SV
from  wdfml.observers.observable import *
from wdfml.structures.segment import *

import time
import logging
logging.basicConfig(level=logging.DEBUG)

class createSegments(Observable):
    def __init__ ( self, parameters ):
        """
        :type parameters: class Parameters
        """
        Observable.__init__(self)
        self.file = parameters.file
        self.state_chan = parameters.state_chan
        self.gps = parameters.gps
        self.minSlice = parameters.minSlice
        self.lastGPS = parameters.lastGPS

    def Process ( self ):
        itfStatus = FrameIChannel(self.file, self.state_chan, 1., self.gps)
        Info = SV()
        timeslice = 0.
        start=self.gps
        while start<=self.lastGPS:

            try:
                itfStatus.GetData(Info)
                # logging.info("GPStime: %s" % Info.GetX(0))
                if Info.GetY(0, 0) == 1:
                    timeslice += 1.0
                else:
                    if (timeslice >= self.minSlice):
                        gpsEnd = Info.GetX(0)
                        gpsStart = gpsEnd - timeslice
                        logging.info(
                            "New science segment created: Start %s End %s Duration %s" % (
                                gpsStart, gpsEnd, timeslice))
                        self.update_observers([[gpsStart, gpsEnd]])
                        timeslice = 0.
                    else:
                        continue
            except:
                logging.warning("GPS time: %s. Waiting for new acquired data"% Info.GetX(0))
                time.sleep(2000)

            continue
            start=Info.GetX(0)
