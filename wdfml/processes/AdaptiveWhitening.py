"""Whitening

.. moduleauthor:: Elena Cuoco <elena.cuoco@ego-gw.it>

"""
__author__ = 'Elena Cuoco'
__project__ = 'pytsa'

from pytsa.tsa import *

# @TODO write the code
class AdaptiveWhitening(object):
    def __init__ (self, ARorder):
        """

        :type ARorder: int
         
        """
        self.ARorder = ARorder
        self.ADE = ArBurgEstimator(self.ARorder)
        self.LV = LatticeView(self.ARorder)
        self.LF = LatticeFilter(self.LV)

    def ParametersEstimate (self, data):
        """

        :type data: pytsa.SeqViewDouble
        """
        self.ADE(data)
        self.ADE.GetLatticeView(self.LV)
        self.LF.init(self.LV)
        return

    def GetSigma ( self ):
        return self.ADE.GetAR(0)

    def Process(self, data,dataw):
        self.LF(data, dataw)
        return

    def ParametersSave (self, ARfile, LVfile):
        """
        :param ARfile: file for AutoRegressive parameters
        :type ARfile: basestring
        :param LVfile: file for Lattice View parameters
        :type LVfile: basestring

        """
        self.ADE.Save(ARfile, "txt")
        self.LV.Save(LVfile, "txt")
        return

    def ParametersLoad (self, ARfile, LVfile):
        """
        :param ARfile: file for AutoRegressive parameters
        :type ARfile: basestring
        :param LVfile: file for Lattice View parameters
        :type LVfile: basestring
        :return: Autoregressive and Lattice View
        :rtype: eternity format
        """
        self.ADE.Load(ARfile, "txt")
        self.LV.Load(LVfile, "txt")
        self.LF.init(self.LV)
        self.ADE.GetLatticeView(self.LV)
        return
