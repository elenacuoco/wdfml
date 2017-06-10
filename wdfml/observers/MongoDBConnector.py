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


class MongoDBConnector(Observer):
    def __init__(self, par, host='localhost',port= 27017 ):
        self.client = MongoClient(host, port)
        self.db = self.client['WDFTriggers'];
        self.param = par;

### write on disk in ordered way
    def update(self, Cev):
        self.CEV = Cev.__dict__
        self.db.events.insert_one(self.CEV)
