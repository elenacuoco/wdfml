import unittest
from wdfml.config.parameters import Parameters
import pytest
class MyTestCase(unittest.TestCase):
    def test_something(self):
        window=1024
        overlap=900
        threshold=4
        sigma=0.1
        sampling=4096
        par = Parameters(window=window, overlap=overlap, threshold=threshold, sigma=sigma, sampling=sampling)
        par.dump("fileParameters.json")
        par2 = Parameters()
        par2.load("fileParameters.json")
        par2.dump("file2.json")

        self.assertEqual(par.window, par2.window)


if __name__ == '__main__':
    unittest.main()
