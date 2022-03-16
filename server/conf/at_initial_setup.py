from django.conf import settings
from evennia.utils.logger import log_info
from evennia import create_object
from glob import glob


"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""


def at_initial_setup():
    from area_reader.evennia_import import AreaImporter
    importer = AreaImporter()
    imports = glob(settings.AREA_IMPORT_PATH)
    for areafile in imports:
        log_info("Loading %s" % areafile)
        importer.load(areafile)
    log_info("Creating rooms...")
    importer.spawnRooms()
    log_info("Enumerating objects...")
    importer.enumerateObjectLocations()
    log_info("Creating objects...")
    importer.spawnObjects()
    log_info("Import complete.")

    train = create_object("typeclasses.movingroom.MovingRoom",
                  key="a cosmic train",
                  home=None,
                  location=None,
                  aliases=["train"],
                  attributes=[("desc", "A curious train wiggles through spacetime.")]
                  )
    for d in ['#3', # edearth
        '#971', #shaolin temple
        '#770', #bazaar
        '#1464', #zooology
        '#2262', #sands of sorrow
        '#5792', #nirvana
        '#5520', #new thalos
        ]:
        train.add_destination(d)

    log_info("Train ID is %s" % train.id)
    pass
