# Area Reader
A Python Library to parse MUD area files and create objects in Evennia

This project originally reads area files from old MUDs and presents them as Python objects.
The returned objects all use the [Attrs](https://pypi.python.org/pypi/attrs) package so it is very easy to do stuff like render out the entire tree of objects as JSON or similar.

There are a number of improvements possible: https://github.com/elixx/area_reader/wiki/TODO

## Example Usage (within Evennia):
```
    !
    importer = AreaImporter()
    importer.load('/path/to/file.are')
    importer.spawnRooms()
    importer.spawnMobs()
    importer.spawnObjects()
```


I presently use this to preconstruct the world at first run of a new Evennia setup. In `at_initial_setup()` for the server:
```
    from area_reader.evennia_import import AreaImporter

    log_info("Loading area files...")
    importer = AreaImporter()
    imports = glob(settings.AREA_IMPORT_PATH)
    for areafile in imports:
        print(">>>LOADING: " + areafile)
        importer.load(areafile)
    print("*************** Creating rooms... *************")
    entrypoints = importer.spawnRooms()
    log_info("Creating mobs...")
    starts = importer.spawnMobs()
    log_info("Creating objects...")
    importer.spawnObjects()
    log_info("Import complete.")    
```

## Example truncated output
```
2022-03-23 20:50:49 [..] enumerateRooms(): 56 rooms
2022-03-23 20:50:49 [..] enumerateRooms(): 80 rooms
2022-03-23 20:50:49 [..] enumerateRooms(): 51 rooms
2022-03-23 20:50:49 [..] enumerateRooms(): 100 rooms
2022-03-23 20:50:49 [..] enumerateRooms(): 53 rooms
2022-03-23 20:50:49 [..] enumerateRooms(): 21 rooms
2022-03-23 20:50:51 [..] Creating rooms...
2022-03-23T20:51:02-0400 [..] 8525 rooms created.
2022-03-23T20:59:34-0400 [..] Spawning mobs...
2022-03-23T21:08:13-0400 [..] Creating objects...
```


Make sure you create or redefine `typeclasses.exits.LegacyExit`, `typeclasses.objects.LegacyObject` and `typeclasses.objects.LegacyRoom` in the code.
These are used as bases for objects that the importer created.

Rooms, objects, and exits from each area are tagged and given an attribute 'area' with the area name, to make DB maintenance easier.

You will want to pull in additional attributes on mobs to adapt to fit your game system.
Make sure to first create rooms, then mobs, then objects, as each can depend on the latter for its location. You don't have to import everything, but you do need to import where something goes.

It should log any exits that don't have a valid source or destination, whether it's because the original VNum wasn't found (probably something weird with the area file or the parser) or because the "EVId" (the Evennia object id) wasn't found (perhaps not created yet).

The load and enumerate functions will load the ROM area files and parse them into memory. The spawn functions will try to display info about the first room of each area (candidates for entry points), and any exits that don't link up (candidates for exits / manual stitching). So, if loading multiple area files, exits with matching `vnum`s that cross areas should link up properly.

Some old area files don't work at all. I think it may have to do with the original area_reader and handling of ROM area reset commands.
 
I've tested a bunch from https://github.com/vedicveko/Mud-Areas and a list of working ones is available
[here](working_areas.md). 
