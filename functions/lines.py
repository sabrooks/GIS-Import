import fiona
from elements import make_element

GDB = 'GDB/Export_Feb01.gdb'

def make_lines(gdb, layer, prefix, detail, detail_accessor, section_type):
    def get_line_details(line):
        'Catches cases without Conductor Size'
        line_props = line['properties']
        try:
            value = line_props['ConductorSize'] + line_props['ConductorMaterial']
        except:
            try:
                value = line_props['ConductorSize'] + line_props['WireType']
            except:
                value = None
        return value

    def make_line(line, details, prefix, section_type):
        made_element = make_element(line, section_type)
        out = {'F34':1}
        out['SectionName'] = prefix + str(line['id'])
        try:
            material = details[int(line['id'])]
            out['F12'] = material
            for cell, phase in zip(['F' + str(i) for i in range(9, 12)], ['A', 'B', 'C']):
                if phase in made_element['SectionPhaseConfig']:
                    out[cell] = material
        except:
            print(str(line['id']) + ' material not found.')

        try:
            out['F14'] = line['properties']['ConductorConfiguration']
        except:
            pass

        return {**made_element, **out}

    details = fiona.open(gdb, layer=detail)
    line_details = {line['properties'][detail_accessor]: get_line_details(line)
                    for line in details}
    return [make_line(line, line_details, prefix, section_type)
            for line in fiona.open(gdb, layer=layer)]

def make_buses(gdb, layer, prefix, section_type):
    def make_bus(bus, prefix, section_type):
        made_element = make_element(bus, section_type)
        out = {'F34':1}
        out['SectionName'] = prefix + str(bus['id'])
        material = 'BUS'
        try:
            out['F12'] = material
            for cell, phase in zip(['F' + str(i) for i in range(9, 12)], ['A', 'B', 'C']):
                if phase in made_element['SectionPhaseConfig']:
                    out[cell] = material
        except:
            print(str(bus['id']) + ' material not found.')

        out['F14'] = 'HOR'

        return {**made_element, **out}

    return [make_bus(bus, prefix, section_type)
            for bus in fiona.open(gdb, layer=layer)]



MAKE_PRIOH = lambda gdb: make_lines(gdb, layer='PriOHElectricLineSegment',
                                    prefix='OH_', detail='PRIOHCONDUCTORINFO',
                                    detail_accessor='PriOHConductorObjectID',
                                    section_type=1)

MAKE_PRIUG = lambda gdb: make_lines(gdb, layer='PriUGElectricLineSegment',
                                    prefix='UG_', detail='PRIUGCONDUCTORINFO',
                                    detail_accessor='PriUGConductorObjectID',
                                    section_type=3)

MAKE_SECOH = lambda gdb: make_lines(gdb, layer='SECOHElectricLineSegment',
                                    prefix='OHSec__', detail='SECOHCONDUCTORINFO',
                                    detail_accessor='SecOHConductorObjectID',
                                    section_type=1)

MAKE_SECUG = lambda gdb: make_lines(gdb, layer='SECUGElectricLineSegment',
                                    prefix='UGSec__', detail='SECUGCONDUCTORINFO',
                                    detail_accessor='SecUGConductorObjectID',
                                    section_type=3)

MAKE_BUS = lambda gdb: make_buses(gdb, layer='BusBar',
                                  prefix='UGB__',
                                  section_type=3)
