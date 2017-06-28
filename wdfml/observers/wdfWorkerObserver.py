__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

from wdfml.config.parameters import *
from multiprocessing import Process
from wdfml.observers.observer import Observer
from wdfml.observers.observable import Observable
import multiprocessing as mp
from wdfml.processes.wdfWorker import *


# from numba import autojit
# @autojit

class wdfWorkerObserver(Observer, Observable):
    def __init__ ( self, parameters,fullPrint=0):
        """
        :type self.parameters: class self.parameters object
        """
        Observable.__init__(self)
        Observer.__init__(self)
        self.pool = mp.Pool(parameters.nproc)

        self.par = Parameters()
        self.par.copy(parameters)
        self.wdfworker = wdfWorker(self.par, fullPrint)

    def wait_completion ( self ):
        """ Wait for completion of all the tasks in the queue """
        self.pool.close()
        self.pool.join()

    def update ( self, segment,last ):
        try:
            self.pool.map_async(self.wdfworker.segmentProcess, segment)
            if last==1:
                self.wait_completion()
        except KeyboardInterrupt:
            self.pool.terminate()
