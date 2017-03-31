import fiona
import csv

UGS = {1:'PullBox', 2:'PullBox', 3:'Surface Structure',
          **{num:'Surface Structure' for num in range(4, 17)}}
SWFAC = {1:'PullBox', 5: 'PullBox', 2: 'Junction Box', 3:'Vault', 4:'Vault'}

MARKERYPE = lambda x: 'MARKER'
MARKERNAME = lambda x: 'M_' + x['id']
UGTYPE = lambda x: UGS.get(x['properties']['SubtypeCD'], None)
UGNAME = lambda x: 'UG_' + str(x['id']) if not x['properties']['FacilityID'] else 'UG_' + x['properties']['FacilityID']
SWITCHTYPE = lambda x: SWFAC.get(x['properties']['SubtypeCD'], None)
SWITCHNAME = UGNAME
POLETYPE = lambda x: 'Pole' if x['properties']['Owner'] == 'PLC' else 'Foreign Structure'
POLENAME = lambda x: 'P_' + str(x['id']) if not x['properties']['FacilityID'] else 'P_' + x['properties']['FacilityID']
POLEASS = lambda x: str(x['properties']['Height']) + '-' + str(x['properties']['Class'])

def make_element(element, f_type, f_name, funcs=None):
    properties = element['properties']
    out = {}
    out['Type'] = f_type(element)
    out['oid'] = element['id']
    out['Guid'] = str(properties['GlobalID'])
    out['Name'] = f_name(element)
    out['Xcoord'], out['Ycoord'] = element['geometry']['coordinates']
    return out

def export_gps(element):
    fields = ['Name', 'Type', 'Xcoord', 'Ycoord', 'Guid']
    return [element.get(key, None) for key in fields]

def export_asm(element):
    fields = ['Name', 'Assemby']

GPS_LAYERS = {'SubMarker':{'f_type': MARKERYPE, 'f_name': MARKERNAME},
              'UndergroundStructure':{'f_type': UGTYPE, 'f_name': UGNAME},
              'SwitchingFacility':{'f_type':SWITCHTYPE, 'f_name': SWITCHNAME},
              'SupportStructure':{'f_type': POLETYPE, 'f_name': POLENAME}}

GDB = 'GDB/Export_Feb01.gdb'

GPS_ELEMENTS = (make_element(element=element, f_type=k['f_type'], f_name=k['f_name'])
                for layer, k in GPS_LAYERS.items()
                for element in fiona.open(GDB, layer=layer))

GPS = [export_gps(element) for element in GPS_ELEMENTS]
ASM = [[POLENAME(element), POLEASS(element), 1, None, None, None, None, None]
       for element in fiona.open(GDB, layer='SupportStructure')]

with open('Mar17.gps', 'w') as f:
    WRITER = csv.writer(f)
    WRITER.writerows(GPS)

with open('Mar17.asm', 'w') as f:
    WRITER = csv.writer(f)
    WRITER.writerows(ASM)
