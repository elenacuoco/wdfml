__author__ = "Elena Cuoco"
__copyright__ = "Copyright 2017, Elena Cuoco"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Elena Cuoco"
__email__ = "elena.cuoco@ego-gw.it"
__status__ = "Development"

from wdfml.interface import parameters

from pprint import pprint

def main(window, overlap, threshold, sigma, sampling):
    par = parameters(window, overlap, threshold, sigma, sampling)
    par.dict_param["sampling"]=1.0
    par.dict_param["dt"] = 2.0 * par.dict_param["window"] / par.dict_param["sampling"]
    par.dict_param["factorF"] = par.dict_param["sampling"] / (2.0 * par.dict_param["window"])
    par.dump("filejson.json")
    par2=parameters()
    par2.load("filejson.json")
    par2.dump("filetest.json")


if __name__ == "__main__":
    main(1024, 900, 4, 0.1, 4096)
