__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class wdfHandler(PatternMatchingEventHandler):
    patterns = ["*/lastfile.ffl"]

    def __init__(self,worker):
        Observable.__init__(self)
        self.worker=worker

    def process ( self, event ):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        print(event.src_path, event.event_type)
        self.worker.Process()



    def on_modified ( self, event ):
        self.process(event)

    def on_created ( self, event ):
        self.process(event)

    def on_deleted ( self, event ):
        self.process(event)

    def on_moved ( self, event ):
        self.process(event)
