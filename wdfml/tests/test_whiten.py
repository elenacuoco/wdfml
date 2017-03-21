import unittest
from wdfml.config.parameters import Parameters
from wdfml.processes.whitening import  *
import numpy as np
from pytsa.tsa import SeqView_double_t as SV
class MyTestCase(unittest.TestCase):
    def test_something (self):
        n_est = 100000
        sampFreq=0.01
        ##Do whitening parameters estimation
        learn = SV(0.0, 1.0 / sampFreq, n_est)
        mu, sigma = 0, 0.1  # mean and standard deviation
        x= np.random.normal(mu, sigma, n_est)
        for i in range(n_est):
            learn.FillPoint(0, i, float(x[i]))
        par=Parameters()
        par.ARorder=100
        whiten=Whitening(par.ARorder)
        whiten.ParametersEstimate(learn)
        sigma=whiten.GetSigma()
        self.assertTrue(sigma>0)

if __name__ == '__main__':
    unittest.main()
