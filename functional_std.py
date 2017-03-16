from multiprocessing.dummy import Pool as ThreadPool
import fiona
from functools import reduce
import layer_map
import logging
import std_defaults

#Set Up Logging
LOGGER = logging.getLogger('gis_import')
LOGFILE = logging.FileHandler('GIS.log')
LOGFILE.setLevel(logging.DEBUG)
LOGGER.addHandler(LOGFILE)

GDB = 'GDB/Export_Feb01.gdb'
STD_FUNCTIONS = std_defaults.STD_FUNCTIONS
LAYERS = std_defaults.LAYERS

def make_init(gdb, layer, func):
    "Return the initial dict of materials from the info database"
    features = fiona.open(gdb, layer=layer)
    materials = (func(feature) for feature in features)
    return {'materials':{key :value for key, value in materials}}

def process_feature(feature, funcs, init={}):
    return reduce(lambda prev, func: func(feature, prev),
                  (func for _, func in funcs.items()),
                  init)

def process_layer(gdb, layer_map):
    layer = layer_map['name']
    functions = layer_map['functions']
    init_dict = layer_map['init']
    init = make_init(gdb, init_dict['db'], init_dict['function'])
    return [process_feature(feature, {**STD_FUNCTIONS, **functions}, init)
            for feature in fiona.open(GDB, layer=layer)]


OUT = [process_layer(GDB, layer) for layer in LAYERS]


