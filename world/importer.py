from glob import glob
from evennia.utils.logger import log_info, log_err
from area_reader.evennia_import import AreaImporter
import os

def globPath(path="C:\\_SRC\\drasticalMUD\\area_reader\\areas\\*.are"):
    areas = glob(path)
    return areas

def importAreas(areas,do_rooms=True,do_objects=True,do_mobs=True):
    log_info("*** beginning importer...")
    for area in areas:
        try:
            x.load(area)
            log_info("*** Loaded " + area)
        except Exception as e:
            log_err("! %s - %s" % (area, e))
            os.rename("C:\\_SRC\\drasticalMUD\\area_reader\\areas\\"+area.split('\\')[-1], "C:\\_SRC\\drasticalMUD\\area_reader\\areas\\bad\\"+area.split('\\')[-1])

    if do_rooms:
        log_info("*** begin Rooms()")
        x.spawnRooms()
        x.enumerateObjectLocations()
    if do_objects:
        log_info("*** begin Objects()")
        log_info("*** begin spawnObjects()")
        x.spawnObjects()
    if do_mobs:
        log_info("*** begin spawnMobs")
        x.spawnMobs()
    log_info("*** Import Done!")

x = AreaImporter()
areas = globPath()
importAreas(areas)