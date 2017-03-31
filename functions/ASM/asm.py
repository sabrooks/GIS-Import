import fiona


def make_structure(support):
    properties = support['properties']
    out = {}
    out['AssemblyName'] = str(properties['Height']) + '-' + str(properties['Class'])
    out['Quantity'] = 1
    out['SRIPOLEID'] = str(properties['GlobalID'])
    return out

STRUCTURE_LAYER = 'SupportStructure'
GDB = 'GDB/Export_Feb01.gdb'

STRUCTURES = (make_structure(structure)
              for structure in fiona.open(GDB, layer=STRUCTURE_LAYER))
