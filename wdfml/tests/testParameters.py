__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

from wdfml.config.parameters import Parameters


def main(window, overlap, threshold, sigma, sampling):
    par = Parameters(window=window, overlap=overlap, threshold=threshold, sigma=sigma, sampling=sampling)
    par.sampling=1.0
    par.dt = 2.0 * par.window / par.sampling
    par.factorF = par.sampling / (2.0 * par.window)
    par.window=3200
    par.dump("fileParameters.json")
    par2 = Parameters()
    par2.load("fileParameters.json")
    par2.dump("file2.json")

if __name__ == "__main__":
    main(1024, 900, 4, 0.1, 4096)
