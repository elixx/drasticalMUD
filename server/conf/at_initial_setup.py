from django.conf import settings
from area_reader.evennia_import import AreaImporter
from evennia.utils.logger import log_info, log_err
from evennia import create_object
from evennia import search_object
from world.utils import create_exit
from random import choice, randint
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

    limbo = search_object("#2")[0] # 6=void, =u/d->7
    limbo.tags.add("drastical", category='area')
    limbo.db.desc = "The center of the [partial] universe!"

    board = create_object("typeclasses.newsboard.NewsBoard",
                          key="a bulletin board",
                          home=limbo,
                          location=limbo,
                          aliases=['bulletin','board','news'],
                          attributes=[("desc", "A billboard of sorts, for news and things. You can probably {yread{n it.")])
    board.tags.add("drastical", category="object")

    # Set up first transportation room
    train = create_object("typeclasses.movingroom.MovingRoom",
                  key="a cosmic train",
                  home=None,
                  location=None,
                  aliases=["train"],
                  attributes=[("desc", "A curious train wiggles through spacetime.")]
                  )
    train.tags.add("drastical", category='room')

    #train.db.route = ['#2', 6, "#8", 4, "#320",4,"#490",4,'#1633',4,'#2668',2,'#3563',6,'#5691',2]
    #train.db.route = ['#2', 6, '#9', 4, '#320', 4, '#490', 4, '#1633', 4, '#2668', 2, '#3563', 6, '#5691', 2, '#7270', 10, '#8118', 10, '#5786', 10, '#812', 10]
    train.db.route = ['#2', 6]

    log_err("Train ID is %s" % train.id)

    print("FOOOOOOOOOOOOOOOOO")

    importer = AreaImporter()
    imports = glob(settings.AREA_IMPORT_PATH)
    for areafile in imports:
        log_info("Loading %s" % areafile)
        importer.load(areafile)
    log_info("Creating rooms...")
    entries = importer.spawnRooms()
    log_info("Enumerating objects...")
    importer.enumerateObjectLocations()
    log_info("Creating objects...")
    importer.spawnObjects()
    log_info("Import complete.")

    create_exit("up", "#2", "#8", exit_aliases="u")
    create_exit("down", "#8", "#2", exit_aliases="d")

    # # Choose 20 random areas and create transit stops
    for n in range(0,19):
        area = choice(list(entries.keys()))
        dest = entries[area][0]
        train.add_destination(dest, randint(3,10))
        log_info("Train stop added for %s" % area)



