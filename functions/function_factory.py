SECTION_PHASE = {1:'C', 2:'B', 3:'BC', 4:'A', 5:'AC', 6:'AB', 7:'ABC'}

def make_basic_feature(feature):
    '''Common feature processing'''
    f50 = feature['properties']['GlobalID']
    phase = feature['properties']
    section_phase_config = SECTION_PHASE[phase]
    geo = feature['geometry']
    coordinates = geo['coordinates']
    x, y = coordinates if geo['type'] == 'Point' else coordinates[0][-1]
    return {'F50': f50,
            'SectionPhaseConfig': section_phase_config,
            'geometry': geo,
            'Xcoord': x,
            'Ycoord': y}
