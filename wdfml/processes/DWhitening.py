"""Whitening

.. moduleauthor:: Elena Cuoco <elena.cuoco@ego-gw.it>

"""
__author__ = 'Elena Cuoco'
__project__ = 'pytsa'

from pytsa.tsa import *


class DWhitening(object):
    def __init__(self, LV, OutputSize, ExtraSize):
        self.DW = DoubleWhitening(LV, OutputSize, ExtraSize)

    def Process(self, data, dataw):
        self.DW.Input(data)
        try:
            self.DW.Output(dataw)
        except:
            print('no data available')

        return
