__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = ['Marco Drago']
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"


from wdfml.observers.observer import Observer
import os.path
from pytsa import *


class DefineSegments(Observer):
    def __init__(self, par):
        self.segmentslist = []

### write on disk in ordered way
    def update(self,frame_t,ifo,bitmask_ifo,DQ_channel_rate_ifo,bitmask_list):
        states=map(lambda x:int(float(x.strip())) & bitmask_ifo,bitmask_list.split("\n"))
        print("states=%s" % (repr(states)))
        #s = self.segmentslist
        #rate = dq_channel_rate_ifo
        #nsec = len(states) / rate
        #for q in range(0, nsec):
        #    fstart = frame_t.start + q
        #    bad = 0
        #for b in range(0, rate):
        #    if (states[q * rate + b] != bitmask_ifo):
        #        bad = 1
        #if bad == 0:
        #    s.append(segment(fstart, fstart + 1))
        #s.coalesce()
        #return s
