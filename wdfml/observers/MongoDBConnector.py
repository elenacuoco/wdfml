_author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

import pymongo
from pymongo import MongoClient

from wdfml.observers.observer import Observer


class MongoDBConncetor(Observer):
    def __init__(self, par, mongoConf = { 'host':'localhost','port': 27017 }):
        self.client = MongoClient(mongoConf.host, mongoConf.port)
        self.db = self.client['WDFTriggers'];
        self.param = par;

### write on disk in ordered way
    def update(self, Cev):
        self.CEV = Cev.__dict__
        eventParam = {"chan": self.param.chan,
                 "gpsStart": int(self.param.gpsStart),
                 "ARorder": self.param.ARorder,
                 "window": self.param.window,
                 "overlap":self.param.overlap,
                 "threshold": int(self.param.threshold)
                 }
        self.db.events.insert_one(dict( eventParam.items() +  self.CEV.items() ) )
