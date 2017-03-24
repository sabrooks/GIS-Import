def export_std(feature):
    "Translates a "
    export_fields = ['SectionName', 'SectionType', 'SectionPhaseConfig', 'PriorSection',
                     'MapNumber', 'Xcoord', 'Ycoord', 'UserTag',
                     *['F' + str(num) for num in range(9, 53)]]
    sep = ','
    return sep.join([str(feature.get(field, '')) for field in export_fields])
