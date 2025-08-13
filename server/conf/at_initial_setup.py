from glob import glob
from random import randint

from django.conf import settings

from area_reader.evennia_import import AreaImporter
from core.utils import create_exit
from evennia.utils.create import create_object
from evennia.utils.logger import log_info
from evennia.utils.search import search_object
from typeclasses.movingroom import createTrainStops

TESTING = False


def at_initial_setup():
    user = search_object("#1")[0]
    user.permissions.add("admin")  # Used to show room id in prompt

    limbo = search_object("#2")[0]
    # limbo.tags.add("drastical", category='area')
    # limbo.tags.add("drastical", category="room")
    limbo.db.desc = "The center of the [partial] universe!"

    board = create_object("typeclasses.newsboard.NewsBoard",
                          key="a bulletin board",
                          home=limbo,
                          location=limbo,
                          aliases=['bulletin', 'board', 'news'],
                          locks=["get:false()"],
                          attributes=[
                              ("desc", "A billboard of sorts, for news and things. You can probably {yread{n it.")],
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
    entrypoints = importer.spawnRooms()
    # log_info("Creating mobs...")
    # starts = importer.spawnMobs()
    log_info("Creating objects...")
    importer.spawnObjects()
    log_info("Import complete.")

    if not TESTING:
        # Connect our Limbo to stock Limbo
        create_exit("up", "#2", "#8", exit_aliases="u")
        create_exit("down", "#8", "#2", exit_aliases="d")

        create_exit("east", "#7", "#7669", exit_aliases="e")
        create_exit("west", "#7669", "#7", exit_aliases="w")

        create_exit("west", "#7", "#8", exit_aliases="w")
        create_exit("east", "#8", "#7", exit_aliases="e")

        # Check that room IDs align as expected resulting from areafile data
        #temple_square = search_object("#1219").first()
        #assert temple_square.key == "The Temple Square"

        # Flag symbol for mapping
        #temple_square.db.sector_type = "important"

        # Create recycle bin
        #create_object("typeclasses.recycle_bin.RecycleBin",
        #              key="recycle bin",
        #              home=temple_square,
        #              location=temple_square,
        #              aliases=['bin'],
        #              locks=["get:false()"],
        #              attributes=[
        #                  ('desc', 'A recycle bin that you can |Yput|n junk into and be rewarded a small amount.')
        #              ],
        #              tags=[('drastical')])

    # Create center entrance to mines
    mines = []
    x=y=z=str(0)
    # first_mine  = create_object("typeclasses.mining.MiningRoom", key="Entrance to the mines",
    #                              tags=[(x, 'mining_x'),
    #                                    (y, 'mining_y'),
    #                                    (z, 'mining_z'),
    #                                    ('the drastical mines', 'area'),
    #                                    ('the drastical mines', 'room')])
    # first_mine.x = first_mine.y = first_mine.z = 0
    # first_mine.update_description()
    # create_exit("enter mine", "#"+str(temple_square.id), "#"+str(first_mine.id),    exit_aliases='enter')
    # create_exit("leave mine",   "#"+str(first_mine.id),  "#"+str(temple_square.id), exit_aliases='leave')
    entrypoints = list(entrypoints)
    first = True
    for entry in entrypoints:  # [20:]:
        if first == True:
            (x,y) = (0,0)
            allcoords = [(x, y)]
            first = False

        mine = create_object("typeclasses.mining.MiningRoom", key="Entrance to the mines",
                                 tags=[(str(x), 'mining_x'),
                                       (str(y), 'mining_y'),
                                       (str(z), 'mining_z'),

                                       ('the drastical mines', 'area'),
                                       ('the drastical mines', 'room'),
                                       ('mines_start', 'room')])

        allcoords.append((x, y))
        mine.x = x
        mine.y = y
        mine.z = z
        mine.update_description()
        create_exit("enter mine", entry, mine.dbref, exit_aliases='enter')
        create_exit("leave mine", mine.dbref, entry, exit_aliases='leave')
        while (x,y) in allcoords:
            x = randint(-64, 64)
            y = randint(-64, 64)

    allcoords = sorted(allcoords,key=lambda s: int(s[0]))
    mines = ""
    for (cx, cy) in allcoords:
        mines += "%s, %s\n" % (cx, cy)
    log_info(f"Mine entrances: {mines}")

    log_info("Train ID is #%s." % train.id)
    log_info("Bulletin board is #%s." % board.id)

    createTrainStops(entries=importer.entries, numstops=25)

    # Set up global ticker functions
    #th.add(300, ticker_5min)
    #th.add(86400, ticker_daily)

    #from world.utils import spawnJunk
    #log_info("Spawning junk...")
    #spawnJunk(TRASH_SPAWN_PERCENT=25)
