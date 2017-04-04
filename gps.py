'''
Makes GPS file from GDB
'''

import csv
import fiona

UGS = {1:'PullBox', 2:'PullBox', 3:'Surface Structure',
       **{num:'Surface Structure' for num in range(4, 17)}}
SWFAC = {1:'PullBox', 5: 'PullBox', 2: 'Junction Box', 3:'Vault', 4:'Vault'}
POLENAME = lambda x: ('P_' + str(x['id']) if not x['properties']['FacilityID']
                      else 'P_' + x['properties']['FacilityID'])
POLETYPE = lambda x: 'Pole' if x['properties']['Owner'] == 'PLC' else 'Foreign Structure'
MARKERYPE = lambda x: 'MARKER'
MARKERNAME = lambda x: 'M_' + x['id']
UGTYPE = lambda x: UGS.get(x['properties']['SubtypeCD'], None)
UGNAME = lambda x: 'UG_' + str(x['id']) if not x['properties']['FacilityID'] else 'UG_' + x['properties']['FacilityID']
SWITCHTYPE = lambda x: SWFAC.get(x['properties']['SubtypeCD'], None)
SWITCHNAME = UGNAME

GPS_LAYERS = {'SubMarker':{'f_type': MARKERYPE, 'f_name': MARKERNAME},
              'UndergroundStructure':{'f_type': UGTYPE, 'f_name': UGNAME},
              'SwitchingFacility':{'f_type':SWITCHTYPE, 'f_name': SWITCHNAME},
              'SupportStructure':{'f_type': POLETYPE, 'f_name': POLENAME}}

def make_element(element, f_type, f_name, funcs=None):
    'Computes properties for gps file'
    properties = element['properties']
    out = {}
    out['Type'] = f_type(element)
    out['oid'] = element['id']
    out['Guid'] = str(properties['GlobalID'])
    out['Name'] = f_name(element)
    out['Xcoord'], out['Ycoord'] = element['geometry']['coordinates']
    return out

def export_gps(element):
    'Takes gps object and creates list of attributes for export to csv file'
    fields = ['Name', 'Type', 'Xcoord', 'Ycoord', 'Guid']
    return [element.get(key, None) for key in fields]

def make_gps(gdb, export='GPS'):
    'Makes gps file from GDB'
    gps_elements = (make_element(element=element, f_type=k['f_type'], f_name=k['f_name'])
                    for layer, k in GPS_LAYERS.items()
                    for element in fiona.open(gdb, layer=layer))

    gps = [export_gps(element) for element in gps_elements]

    with open(export + '.gps', 'w') as gps_file:
        writer = csv.writer(gps_file)
        writer.writerows(gps)
