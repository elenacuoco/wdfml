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
import copy

class MongoDBConnector(Observer):
    def __init__(self, params, host='localhost',port= 27017 ):
        self.client = MongoClient(host, port)
        self.db = self.client['WDFTriggers']



### write on disk in ordered way
    def update(self, Cev):
        DBCev=Cev.__dict__.copy()
        self.db.events.insert_one(DBCev)
