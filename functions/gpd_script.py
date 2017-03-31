import geopandas as gpd

PRIOH = gpd.read_file('GDB/Export_Feb01.gdb', layer='PriOHElectricLineSegment')
PRIOH_MAT = gpd.read_file('GDB/Export_Feb01.gdb', layer='PRIOHCONDUCTORINFO')