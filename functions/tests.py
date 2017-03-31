import conductors
from make_elements import make_function_stack
import fiona

def make_elme(gdb, layer, configs, details):
    functions = make_functions_stack(configs)
    return fiona.open(gdb, layer=layer)

GDB = 'GDB/Export_Feb01.gdb'

INIT = ((layer, configs, configs['init'](GDB))
        for layer, configs in conductors.conductors.CONDUCTORS.items())

LAYERS = (make_element(GDB, layer, configs, details)
          for layer, configs, details in INIT)
