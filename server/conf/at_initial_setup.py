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



    #   {'limbo': [7],
    #   'tournament ground': [9],
    #   'plains': [43],
    #   'zoology': [87],
    #   'chaos-rift': [101],
    #   'new ofcol': [157],
    #   'olympus': [257],
    #   'in the air': [307],
    #   'shire': [347],
    #   'valhalla': [405],
    #   'high tower': [427],
    #   'north': [610, 621],
    #   "wyvern's tower": [611, 630, 664, 683],
    # 'island': [663, 681, 684],
    # 'little haven': [748],
    # 'newtown': [749],
    # 'catacombs': [865],
    # 'gangland': [919],
    # 'dragon tower': [989],
    # 'mahn-tor': [1033],
    # 'path': [1133],
    # 'partbody': [1148, 1154],
    # 'troll den': [1149],
    # 'tree': [1191],
    # 'midgaard': [1215],
    # 'chapel': [1358], "miden'nir": [1425],
    # 'drmscp': [1477],
    # 'mud school': [1511],
    # 'moria': [1570],
    # 'chessboard of midgaard': [1691],
    # 'fun house': [1758],
    # 'the circus': [1782],
    # 'arena': [1831],
    # 'dock': [1852, 1885, 1923],
    # 'sands of sorrow': [1853, 1908],
    # 'drow city': [1942],
    # 'thalos': [1993],
    # 'old thalos': [2074],
    # 'ofcol': [2160],
    # 'animaland': [2168],
    # 'firetop mountain': [2268],
    # 'haon dor': [2368],
    # 'arachnos': [2439],
    # 'dwarven kingdom': [2495],
    # 'day care': [2546], "quifael's": [2565],
    # 'blade dancers inn': [2571],
    # 'sewers': [2597],
    # 'great town of gerighelm': [2774],
    # 'astral plane': [2947],
    # 'valley of the elves': [3027],
    # 'east': [3111],
    # 'mega city one': [3136],
    # 'ghost town': [3164],
    # 'zoo of midgaard': [3264],
    # 'marsh': [3294],
    # 'machine dreams': [3312],
    # 'pyramid': [3348],
    # 'mirkwood': [3408],
    # 'holy grove': [3478],
    # 'nirvana': [3500], "dylan's area": [3560],
    # 'elemental canyon': [3648],
    # 'mob factory': [3703],
    # 'new thalos': [3728, 3814, 3824],
    # 'the plains of blood': [3778, 3815],
    # 'goblin nation': [3985],
    # 'the shielding': [4084],
    # 'hell': [4098],
    # 'haven lake': [4239],
    # 'white lotus': [4339],
    # 'pawmist': [4512],
    # 'darkness': [4669],
    # 'divided souls': [4697],
    # 'shadval45': [4838],
    # 'fragrant harbour': [4938],
    # 'the bazaar': [5108],
    # 'anonopolis': [5161],
    # 'dark continent': [5260],
    # 'the dungeon': [5359],
    # "king's castle": [5429],
    # "darathorn's pit": [5483],
    # 'chessbrd': [5562],
    # 'erealms': [5628, 5783],
    # 'under2': [5723, 5784],
    # 'warzone': [6214],
    # 'tisland': [6265],
    # 'heaven': [6316],
    # 'dawn': [6367],
    # 'valley of the titans': [6421],
    # 'newbie2': [6546],
    # 'talonvle': [6587],
    # 'mirror realm': [6659],
    # 'takshrin': [6829],
    # 'calinth': [6875, 7013],
    # 'shaolin temple': [6976],
    # 'camelot1': [7207],
    # 'avalonch': [7269],
    # 'steab': [7369],
    # 'enchice': [7469],
    # 'weaverei': [7569],
    # 'river of despair': [7623],
    # 'sesame street': [7672],
    # 'the abyss': [7733],
    # 'river': [7822],
    # 'amazon': [7855],
    # 'gstrong': [7906],
    # 'water': [7933],
    # 'sdearth': [7954],
    # 'cannabis': [8055],
    # 'caverns through time': [8085],
    # 'wdearth': [8161],
    # 'the walls of the city of anon': [8261],
    # 'edearth': [8381],
    # "gilligan's island": [8481]}

