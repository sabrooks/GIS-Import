'Main Function, Exports STD, ASM, GPS, MPT '
import datetime
from std import make_std_mpt
from std import ELEMENTS
from asm import make_asm
from gps import make_gps

if __name__ == "__main__":
    NOW = datetime.datetime.now()
    EXPORT = NOW.strftime('%y%m%d%H%M%S')
    GDB = 'GDB/Export_Feb01.gdb'
    make_std_mpt(gdb=GDB, elements=ELEMENTS, export=EXPORT)
    make_asm(GDB, export=EXPORT)
    make_gps(GDB, export=EXPORT)

