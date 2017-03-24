from make_elements import make_layer
from export import export_std
from elements.conductor import CONDUCTOR
from elements.points import POINTS
import fiona


GDB = 'GDB/Export_Feb01.gdb'
LAYERS = {**CONDUCTOR, **POINTS}
INIT = (make_init(GDB, layer, kwargs) for layer, kwargs in LAYERS.items())
FIRST = [make_layer(GDB, layer, kwds=kwargs) for layer, (kwargs) in INIT]


def xfmr_phase(raw, out, kwds):
    phasing = out['SectionPhaseConfig']
    tx_type = TRANSFORMER[raw['properties']['SubtypeCD']]
    phasing = {cell: str(tag) +  ' ' + tx_type
               for phase, cell in zip(['A', 'B', 'C'], ['F9', 'F10', 'F11'])
               if phase in out['SectionPhaseConfig']}
    return {**out, **phasing}


PROCESSED = [make_layer(GDB, layer, kwds=kwargs) for layer, kwargs in LAYERS.items()]

for element in PROCESSED[0]:
    print(export_std(element))
