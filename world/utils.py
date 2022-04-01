from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object, search_channel, search_tag
from evennia.utils.create import create_object
from evennia.utils.logger import log_err, log_info
from world.bookmarks import starts as start_rooms
from random import choice
from string import capwords

def findStatsMachine():
    results = search_object("a stats machine")
    if (len(results) == 0):
        home = search_object("#2")[0]
        obj = create_object("typeclasses.statsmachine.StatsMachine",
                            key="a stats machine",
                            home=home,
                            location=home)
        return (obj)
    else:
        for obj in results:
            if obj.typename == "StatsMachine":
                return (obj)
    return


def startTransit():
    from typeclasses.movingroom import MovingRoom
    for train in MovingRoom.objects.all():
        train.at_object_creation()


def warpArea(caller, area=None):
    if area != None:
        dest = choice(start_rooms[area])
    else:
        area = choice(list(start_rooms.keys()))
        dest = choice(list(start_rooms[area]))
    dest = search_object("#" + str(dest))
    if len(dest) != 1:
        caller.msg("beep boop " + "brrzap" * len(dest))
        log_err("warpArea(): " + str(dest))
    else:
        caller.msg("You are warped to |Y%s|n." % capwords(area))
        caller.location.msg_contents("|Y%s|n is warped to somewhere in |g%s|n." % (caller.name, capwords(area)))
        caller.location = dest[0]



def startContExplorers():
    def work(area, loc):
        create_object("typeclasses.mob_explorer.ContinentExplorer", key=area,
                      location=loc, home=loc,
                      attributes=[('patrolling_pace', 1)])

    for area in start_rooms.keys():
        startLocation = '#' + str(choice(list(start_rooms[area])))
        work(area, startLocation)


def restartExplorers(location=None):
    from typeclasses.mob_explorer import ExplorerMob
    for mob in ExplorerMob.objects.all():
        if location is not None:
            mob.location = location
        mob.at_object_creation()


def fixContinentExplorers():
    from typeclasses.mob_explorer import ContinentExplorer
    for bot in ContinentExplorer.objects.all():
        if bot.db.seen == None:
            bot.at_object_creation()
        if not bot.db.patrolling:
            bot.db.patrolling = True
            bot.at_init()
        if bot.db.is_dead:
            bot.db.is_dead = False


def qual(obj):
    if obj.db.quality:
        quality = obj.db.quality
        if quality > 95:
            return "legendary"
        elif quality > 75:
            return "exceptional"
        elif quality > 50:
            return "good"
        elif quality > 20:
            return "average"
        elif quality > 0:
            return "poor"
        elif quality == 0:
            return "trash"
    else:
        return "standard"


def area_count():
    from typeclasses.rooms import ImportedRoom
    counts = {}
    areas = search_tag_object(category='area')
    allrooms = ImportedRoom.objects.all()
    for area in areas:
        counts[area.db_key] = allrooms.filter(db_tags__db_key=area.db_key, db_tags__db_category="room").count()
    return (counts)


def total_rooms_in_area(area):
    results = search_tag(area, category="room")
    return (results.count())


def claimed_in_area(area, owner):
    if isinstance(owner, int):
        owner = "#" + str(owner)
    o = search_object(owner)
    if o is not None:
        o = o.first()
        results = search_tag(area, category='room')
        results = results.filter(db_attributes__db_key="owner", db_attributes__db_value=o.id)
        return (results)


def visited_in_area(area, owner):
    matches = []
    if isinstance(owner, int):
        owner = "#" + str(owner)
    o = search_object(owner)
    if o is not None:
        o = o.first()
        if o.db.stats['visited']:
            if area in o.db.stats['visited'].keys():
                matches = o.db.stats['visited'][area]
        return (matches)


def exploreReport(user):
    summary = {}
    o = search_object(user)
    if o is not None:
        o = o.first()
        stats = o.db.stats
        seen = stats['visited']
        for area in seen.keys():
            total = total_rooms_in_area(area)
            claimed = len(claimed_in_area(area, o))
            visited = len(visited_in_area(area, o))
            summary[area] = {'total': total, 'visited': visited, 'claimed': claimed}
    return summary

def topGold():
    from evennia.utils.search import search_object_attribute
    results = search_object_attribute('stats')
    output = sorted([(v.name, v.db.stats['gold']) for v in results if 'gold' in v.db.stats.keys()],key=lambda x: x[1],
                    reverse=True)
    return(output)

def spawnJunk(TRASH_SPAWN_PERCENT=10, BUNDLE_SPAWN_PERCENT=5):
    from world.resource_types import trash
    results = search_tag("random_spawn", category='room')
    ob = None

    for n in range(0, int(results.count() * (TRASH_SPAWN_PERCENT / 100))):
        loc = choice(results)
        ob = create_object(key=trash(), typeclass="typeclasses.resources.Resource", home=loc, location=loc)

    for n in range(0, int(results.count() * (BUNDLE_SPAWN_PERCENT / 100))):
        loc = choice(results)
        ob = create_object(key=trash(), typeclass="typeclasses.resources.Resource", home=loc, location=loc)