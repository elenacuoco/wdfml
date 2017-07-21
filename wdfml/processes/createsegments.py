__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

import logging
import time

from pytsa.tsa import *
from pytsa.tsa import SeqView_double_t as SV

from  wdfml.observers.observable import *

logging.basicConfig(level=logging.DEBUG)


class createSegments(Observable):
    def __init__ ( self, parameters ):
        """
        :type parameters: class Parameters
        """
        Observable.__init__(self)
        self.file = parameters.file
        self.state_chan = parameters.status_itf
        self.gps = parameters.gps
        self.minSlice = parameters.minSlice
        self.lastGPS = parameters.lastGPS
        self.flag = parameters.flag
        self.process = parameters.process  # define if if you are running while taking data

    def Process ( self ):
        itfStatus = FrameIChannel(self.file, self.state_chan, 1., self.gps)
        Info = SV()
        timeslice = 0.
        start = self.gps
        last = False
        fails=0
        while start < self.lastGPS:
            try:
                itfStatus.GetData(Info)
            except:
                if self.process == 1:  # online
                    logging.warning("GPS time: %s. Waiting for new acquired data" % start)
                    time.sleep(1000)
                else:
                    fails+=1
                    start = start + 1.0
                    itfStatus = FrameIChannel(self.file, self.state_chan, 1., start)
                    Info = SV()
                    time.sleep(1)
                    pass
            else:
                if Info.GetY(0, 0) == self.flag:
                    start = Info.GetX(0)
                    timeslice += 1.0
                else:
                    if (timeslice >= self.minSlice):
                        gpsEnd = start + 1.0
                        gpsStart = gpsEnd - timeslice
                        logging.info(
                            "New segment created: Start %s End %s Duration %s" % (
                                gpsStart, gpsEnd, timeslice))
                        self.update_observers([[gpsStart, gpsEnd]], last)
                        logging.error("Total Fails: %s" % fails)
                        fails=0
                        timeslice = 0.
                    else:
                        timeslice = 0.
                if start == self.lastGPS:
                    last = True
                    gpsEnd = start
                    gpsStart = gpsEnd - timeslice
                    logging.info("Segment creation completed")
                    self.update_observers([[gpsStart, gpsEnd]], last)
                    self.unregister_all()
                    break
                if Info.GetY(0, 0) == 0:
                    logging.error("MISSING DATA @GPS %s" % start)
                    fails += 1
                    timeslice = 0.

                    pass
