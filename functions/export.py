import csv

def export_std(elements):
    "Writes std elements to an std file "
    export_fields = ['SectionName', 'SectionType', 'SectionPhaseConfig', 'PriorSection',
                     'MapNumber', 'Xcoord', 'Ycoord', 'UserTag',
                     *['F' + str(num) for num in range(9, 53)]]
    std = [[element.get(field, None) for field in export_fields]
           for element in elements]
    with open('Mar17.std', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(std)
