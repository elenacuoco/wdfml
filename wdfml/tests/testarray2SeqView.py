import unittest
from wdfml.structures.array2SeqView import *
import pytest
import numpy as np
class MyTestCase(unittest.TestCase):
    def test_something(self):
        N=1000
        vec=np.ones(N)
        sampling=100
        start=0.1
        v=array2SeqView(start,sampling,N)
        v.Fill(start,vec)

        self.assertEqual(start, v.GetStart())


if __name__ == '__main__':
    unittest.main()
