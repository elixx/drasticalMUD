from glob import glob
from evennia.utils.logger import log_info, log_err
from area_reader.evennia_import import AreaImporter
import os

def globPath(path="C:\\_SRC\\drasticalMUD\\area_reader\\areas\\*.are"):
    areas = glob(path)
    return areas

def importAreas(areas):
    log_info("*** beginning importer...")
    for area in areas:
        try:
            x.load(area)
            log_info("*** Loaded " + area)
        except Exception as e:
            log_err("! %s - %s" % (area, e))
            os.rename("C:\\_SRC\\drasticalMUD\\area_reader\\areas\\"+area.split('\\')[-1], "C:\\_SRC\\drasticalMUD\\area_reader\\areas\\bad\\"+area.split('\\')[-1])

    log_info("*** begin spawnRooms()")
    x.spawnRooms()
    log_info("*** begin spawnRooms()")
    x.enumerateObjectLocations()
    log_info("*** begin spawnObjects()")
    x.spawnObjects()
    log_info("*** Import Done!")

x = AreaImporter()
areas = globPath()
importAreas(areas)