from conductor_general import conductor_init, LINES, SIZE_MATERIAL

BUSBAR = {'BusBar':
          {'prefix':'UGB_', 'section_type':1, 'funcs':LINES,
            'init': lambda gdb: None}}
