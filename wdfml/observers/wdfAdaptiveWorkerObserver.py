__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

import multiprocessing as mp

from wdfml.processes.wdfAdaptiveWorker import *


# from numba import autojit
# @autojit

class wdfAdaptiveWorkerObserver(Observer, Observable):
    def __init__ ( self, parameters,fullPrint=0):
        """
        :type self.parameters: class self.parameters object
        """
        Observable.__init__(self)
        Observer.__init__(self)
        self.pool = mp.Pool(parameters.nproc)

        self.par = Parameters()
        self.par.copy(parameters)
        self.wdfAdaptiveWorker = wdfAdaptiveWorker(self.par, fullPrint)


    def wait_completion ( self ):
        """ Wait for completion of all the tasks in the queue """
        self.pool.close()
        self.pool.join()

    def update ( self, segment,last ):
        try:
            if last:
                logging.info("Last job launched")
                self.pool.map(self.wdfAdaptiveWorker.segmentProcess, segment)
                self.wait_completion()
            else:
                self.pool.apply_async(self.wdfAdaptiveWorker.segmentProcess, segment)
        except KeyboardInterrupt:
            self.pool.terminate()
