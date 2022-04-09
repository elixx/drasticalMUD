from django.conf import settings
from area_reader.evennia_import import AreaImporter
from evennia.utils.logger import log_info, log_err
from evennia.utils.create import create_object
from evennia.utils.search import search_object
from core.utils import create_exit
from typeclasses.movingroom import createTrainStops
from glob import glob

from evennia import TICKER_HANDLER as th
from world.ticker import ticker_5min, ticker_daily

TESTING=False

def at_initial_setup():
    user = search_object("#1")[0]
    user.permissions.add("admin")   # Used to show room id in prompt

    limbo = search_object("#2")[0]
    #limbo.tags.add("drastical", category='area')
    #limbo.tags.add("drastical", category="room")
    limbo.db.desc = "The center of the [partial] universe!"

    board = create_object("typeclasses.newsboard.NewsBoard",
                          key="a bulletin board",
                          home=limbo,
                          location=limbo,
                          aliases=['bulletin','board','news'],
                          locks=["get:false()"],
                          attributes=[("desc", "A billboard of sorts, for news and things. You can probably {yread{n it.")],
                          tags=[('drastical')])

    # Set up first transportation room
    train = create_object("typeclasses.movingroom.MovingRoom",
                  key="a cosmic train",
                  home=None,
                  location=None,
                  aliases=["train"],
                  attributes=[("desc", "A curious train wiggles through spacetime.")],
                  tags=[('drastical')])
    #                            ('drastical', 'room')]

    print("FOOOOOOOOOOOOOOOOO")

    # Behold, creator of worlds
    importer = AreaImporter()
    imports = glob(settings.AREA_IMPORT_PATH)

    if TESTING: imports = imports[:25]

    for areafile in imports:
        importer.load(areafile)
    log_info("Creating rooms...")
    importer.spawnRooms()
    # log_info("Creating mobs...")
    # starts = importer.spawnMobs()
    log_info("Creating objects...")
    importer.spawnObjects()
    log_info("Import complete.")

    if not TESTING:
        # Connect Limbo to Limbo
        create_exit("up", "#2", "#8", exit_aliases="u")
        create_exit("down", "#8", "#2", exit_aliases="d")

        create_exit("east", "#7", "#7669", exit_aliases="e")
        create_exit("west", "#7669", "#7", exit_aliases="w")

        create_exit("west", "#7", "#8", exit_aliases="w")
        create_exit("east", "#8", "#7", exit_aliases="e")


        # Check that room IDs align as expected"
        temple_square = search_object("#1219").first()
        temple_square.db.sector_type = "important"

        assert temple_square.key == "The Temple Square"

        # Create recycle bin
        create_object("typeclasses.recycle_bin.RecycleBin",
                      key="recycle bin",
                      home=temple_square,
                      location=temple_square,
                      aliases=['bin'],
                      locks=["get:false()"],
                      attributes=[
                          ('desc', 'A recycle bin that you can |Yput|n junk into and be rewarded a small amount.')
                      ],
                      tags=[('drastical')])

    log_info("Train ID is #%s." % train.id)
    log_info("Bulletin board is #%s." % board.id)

    createTrainStops(entries=importer.entries)

    # Set up global ticker functions
    th.add(300, ticker_5min)
    th.add(86400, ticker_daily)

    from world.utils import spawnJunk
    spawnJunk(TRASH_SPAWN_PERCENT=25)