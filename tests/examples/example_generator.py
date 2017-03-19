'''Generates a dict of example elements (one from each layer in the GDB)'''
import pickle
import fiona


LAYERS = ['PriOHElectricLineSegment', 'PriUGElectricLineSegment', 'SecOHElectricLineSegment',
          'BusBar', 'SecUGElectricLineSegment', 'PFCorrectingEquipment', 'Fuse', 'ServicePoint',
          'Streetlight', 'Switch', 'Transformer', 'VoltageRegulator', 'DynamicProtectiveDevice',
          'ElectricStation']

GDB = 'GDB/Export_Feb01.gdb'

def get_example(gdb, layer):
    '''Return an example feature from each layer'''
    features = fiona.open(gdb, layer=layer)
    return next(features)

EXAMPLES = {layer: get_example(GDB, layer) for layer in LAYERS}
with open('tests/examples/example_elements.p', 'wb') as f:
    pickle.dump(EXAMPLES, f)
