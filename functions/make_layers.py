from make_elements import make_layer, make_init
from export import export_std
from conductor import CONDUCTOR
from points import POINTS
import fiona


GDB = 'GDB/Export_Feb01.gdb'
LAYERS = {**CONDUCTOR, **POINTS}
FIRST = [make_layer(GDB, layer, kwds=kwargs) for layer, kwargs in LAYERS.items()]
# Second pass looks up parent element

for layer_result in FIRST:
    for element in layer_result:
        print(export_std(element))