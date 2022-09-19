import sys
import random
from subprocess import call

tripInfoFile = "my_intersection.trips.xml"
statsFile = "my_intersection.stats.xml"		# statistics file results (output)

retcode = call(["python","networkStatistics.py","-t", tripInfoFile,"-o", statsFile])

