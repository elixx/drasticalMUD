from django.conf import settings
from area_reader.evennia_import import AreaImporter
from evennia.utils.logger import log_info, log_err
from evennia.utils.create import create_object
from evennia.utils.search import search_object
from core.utils import create_exit
from typeclasses.movingroom import createTrainStops
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
    user = search_object("#2")[0] # 6=void, =u/d->7
    user.permissions.add("admin")

    limbo = search_object("#2")[0] # 6=void, =u/d->7
    limbo.tags.add("drastical", category='area')
    limbo.tags.add("drastical", category="room")
    limbo.db.desc = "The center of the [partial] universe!"

    board = create_object("typeclasses.newsboard.NewsBoard",
                          key="a bulletin board",
                          home=limbo,
                          location=limbo,
                          aliases=['bulletin','board','news'],
                          locks=["get:false()"],
                          attributes=[("desc", "A billboard of sorts, for news and things. You can probably {yread{n it.")],
                          tags=[('drastical','object')])

    # Set up first transportation room
    train = create_object("typeclasses.movingroom.MovingRoom",
                  key="a cosmic train",
                  home=None,
                  location=None,
                  aliases=["train"],
                  attributes=[("desc", "A curious train wiggles through spacetime.")],
                          tags=[('drastical','area'),
                                ('drastical', 'room')]
                  )

    print("FOOOOOOOOOOOOOOOOO")

    importer = AreaImporter()
    imports = glob(settings.AREA_IMPORT_PATH)
    for areafile in imports:
        importer.load(areafile)
    log_info("Creating rooms...")
    starts = importer.spawnRooms()
    log_info("Creating objects...")
    importer.spawnObjects()
    log_info("Import complete.")

    create_exit("up", "#2", "#8", exit_aliases="u")
    create_exit("down", "#8", "#2", exit_aliases="d")


    log_info("Train ID is #%s." % train.id)
    log_info("Bulletin board is #%s." % board.id)

    createTrainStops(entries=starts)
