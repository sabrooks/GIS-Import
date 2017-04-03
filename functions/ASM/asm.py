'''
MAKES ASM FROM GDB
'''
import csv
import fiona

POLENAME = lambda x: ('P_' + str(x['id']) if not x['properties']['FacilityID']
                      else 'P_' + x['properties']['FacilityID'])
POLEASS = lambda x: str(x['properties']['Height']) + '-' + str(x['properties']['Class'])

def make_structure(support):
    'From GDB Suport entry, make an ASM line'
    properties = support['properties']
    out = {}
    out['AssemblyName'] = str(properties['Height']) + '-' + str(properties['Class'])
    out['Quantity'] = 1
    out['SRIPOLEID'] = str(properties['GlobalID'])
    return out

def make_asm(gdb='GDB/Export_Feb01.gdb', export='ASM'):
    "From the GDB, read the layer, make the ASM FILE"
    asm = [[POLENAME(element), POLEASS(element), 1, None, None, None, None, None]
           for element in fiona.open(gdb, layer='SupportStructure')]
    with open(export + '.asm', 'w') as asm_file:
        writer = csv.writer(asm_file)
        writer.writerows(asm)
