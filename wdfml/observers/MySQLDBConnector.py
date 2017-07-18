_author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

import logging
import sys

import MySQLdb

from wdfml.observers.observer import Observer


class MySQLDBConnector(Observer):
    def __init__ ( self, params, host='localhost', port=27017 ):
        # Open database connection

        try:
            self.db = MySQLdb.connect(host="localhost", user="cuoco",
                                      passwd="xxx", db="WDF")
            self.cur = self.db.cursor()
            self.cur.execute("SELECT VERSION()")
            ver = self.cur.fetchone()
            logging.info("Database version : %s " % ver)

        except MySQLdb.Error:
            logging.error("Error %d: %s" % (MySQLdb.Error.args[0], MySQLdb.Error.args[1]))
            sys.exit(1)
        self.table=params.chan+""
        ##put here the code to create the table if not exists per params.chan
        params.table=self.table
    ### write on disk in ordered way
    def update ( self, Cev ):

        DBCev = Cev.__dict__.copy()
        cols = DBCev.keys()
        vals = DBCev.values()

        sql = "INSERT INTO %s (%s) VALUES(%s)" % (
            self.table, ",".join(cols), ",".join(vals))
        self.cur.execute(sql)
