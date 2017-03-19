properties = lambda f: f['properties']
facility_id = lambda f: properties(f)['FacilityID'] # Accesses 'FacilityID'
section_name = lambda f, s, pre: {**s, 'SectionName':pre + str(f['id'])}
sectiontype = lambda s, t: {**s, 'SectionType': t}

def conductor_material(feature, fkey, fvalue):
     key, value = fkey(properties(feature)), fvalue(properties(feature))
     return key, value

def section_phase_config(feature, std):
    'Function returns updated std object with section phase config added'
    phase = feature['properties']['PhaseDesignation']
    return {**std, 'SectionPhaseConfig':SECTION_PHASE[phase]}

def phase_spread(feature, std, func, keys):
    std = section_phase_config(feature, std)
    phasing = std['SectionPhaseConfig']
    try:
        mat = func(feature, std)
    except:
        logging.debug(feature['id'] + ' material not found')
        mat = None
    phase_dict = {key:mat
                  for phase, key in zip(['A', 'B', 'C'], keys) if phase in phasing}
    del std['materials']
    return {**std, **phase_dict} 
