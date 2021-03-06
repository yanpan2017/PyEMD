#!/usr/bin/python
# Coding: UTF-8

from __future__ import print_function

import numpy as np
from PyEMD import CEEMDAN
import unittest

class CEEMDANTest(unittest.TestCase):

    @staticmethod
    def cmp_msg(a, b):
        return "Expected {}, Returned {}".format(a,b)

    @staticmethod
    def test_default_call_CEEMDAN():
        T = np.arange(50)
        S = np.cos(T*0.1)
        max_imf = 2

        ceemdan = CEEMDAN(trials=5)
        ceemdan(S, T, max_imf)

    @staticmethod
    def test_ceemdan_simpleRun():
        T = np.linspace(0, 1, 100)
        S = np.sin(2*np.pi*T)

        ceemdan = CEEMDAN(trials=10, max_imf=1)
        ceemdan.EMD.FIXE_H = 5
        ceemdan.ceemdan(S)

    def test_ceemdan_completeRun(self):
        S = np.random.random(200)

        ceemdan = CEEMDAN()
        cIMFs = ceemdan(S)

        self.assertTrue(cIMFs.shape[0]>1)
        self.assertTrue(cIMFs.shape[1]==S.size)

    def test_ceemdan_passingArgumentsViaDict(self):
        trials = 10
        noise_kind = 'uniform'
        spline_kind = 'linear'

        # Making sure that we are not testing default options
        ceemdan = CEEMDAN()

        self.assertFalse(ceemdan.trials==trials,
                self.cmp_msg(ceemdan.trials, trials))

        self.assertFalse(ceemdan.noise_kind==noise_kind,
                self.cmp_msg(ceemdan.noise_kind, noise_kind))

        self.assertFalse(ceemdan.EMD.spline_kind==spline_kind,
                self.cmp_msg(ceemdan.EMD.spline_kind, spline_kind))

        # Testing for passing attributes via params
        params = {"trials": trials, "noise_kind": noise_kind,
                  "spline_kind": spline_kind}
        ceemdan = CEEMDAN(**params)

        self.assertTrue(ceemdan.trials==trials,
                self.cmp_msg(ceemdan.trials, trials))

        self.assertTrue(ceemdan.noise_kind==noise_kind,
                self.cmp_msg(ceemdan.noise_kind, noise_kind))

        self.assertTrue(ceemdan.EMD.spline_kind==spline_kind,
                self.cmp_msg(ceemdan.EMD.spline_kind, spline_kind))

    def test_ceemdan_testMaxImf(self):
        S = np.random.random(100)

        ceemdan = CEEMDAN(trials=10)

        max_imf = 1
        cIMFs = ceemdan(S, max_imf=max_imf)
        self.assertTrue(cIMFs.shape[0]==max_imf+1)

        max_imf = 3
        cIMFs = ceemdan(S, max_imf=max_imf)
        self.assertTrue(cIMFs.shape[0]==max_imf+1)

    @staticmethod
    def test_ceemdan_constantEpsilon():
        S = np.random.random(100)

        ceemdan = CEEMDAN(trials=10, max_imf=2)
        ceemdan.beta_progress = False
        ceemdan(S)

    @staticmethod
    def test_ceemdan_noiseKind_uniform():
        ceemdan = CEEMDAN()
        ceemdan.noise_kind = "uniform"
        ceemdan.generate_noise(1., 100)

    def test_ceemdan_noiseKind_unknown(self):
        ceemdan = CEEMDAN()
        ceemdan.noise_kind = "bernoulli"
        with self.assertRaises(ValueError):
            ceemdan.generate_noise(1., 100)

    def test_ceemdan_passingCustomEMD(self):

        spline_kind = "linear"
        params = {"spline_kind": spline_kind}

        ceemdan = CEEMDAN()
        self.assertFalse(ceemdan.EMD.spline_kind==spline_kind,
                "Not"+self.cmp_msg(ceemdan.EMD.spline_kind, spline_kind))

        from PyEMD import EMD

        emd = EMD(**params)

        ceemdan = CEEMDAN(ext_EMD=emd)
        self.assertTrue(ceemdan.EMD.spline_kind==spline_kind,
                self.cmp_msg(ceemdan.EMD.spline_kind, spline_kind))

    def test_ceemdan_noiseSeed(self):
        T = np.linspace(0, 1, 100)
        S = np.sin(2*np.pi*T+ 4**T) + np.cos( (T-0.4)**2)

        # Compare up to machine epsilon
        cmpMachEps = lambda x, y: np.abs(x-y)<=2*np.finfo(x.dtype).eps

        ceemdan = CEEMDAN(trials=10)

        # First run random seed
        cIMF1 = ceemdan(S)

        # Second run with defined seed, diff than first
        ceemdan.noise_seed(12345)
        cIMF2 = ceemdan(S)

        # Extremly unlikely to have same seed, thus different results
        msg_false = "Different seeds, expected different outcomes"
        if cIMF1.shape == cIMF2.shape:
            self.assertFalse(np.all(cmpMachEps(cIMF1,cIMF2)), msg_false)

        # Third run with same seed as with 2nd
        ceemdan.noise_seed(12345)
        cIMF3 = ceemdan(S)

        # Using same seeds, thus expecting same results
        msg_true = "Used same seed, expected same results"
        self.assertTrue(np.all(cmpMachEps(cIMF2,cIMF3)), msg_true)

if __name__ == "__main__":
    unittest.main()
