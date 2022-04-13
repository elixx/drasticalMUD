from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object, search_channel, search_tag
from evennia.utils.create import create_object
from evennia.utils.logger import log_err, log_info
from world.bookmarks import starts as start_rooms
from random import choice, randint
from core.utils import rainbow
from string import capwords
from evennia.utils import dbref_to_obj
from evennia.utils.utils import variable_from_module

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


def fixContExplorers():
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
        if quality == 0:
            return "|111trash|n"
        elif quality > 95:
            return rainbow("legendary|n")
        elif quality > 85:
            return "|441exceptional|n"
        elif quality > 80:
            return "|Rimpressive|n"
        elif quality > 70:
            return "|ggreat|n"
        elif quality > 60:
            return "|Ggood|n"
        elif quality > 45:
            return "|Yaverage|n"
        elif quality <= 45:
            return "|xpoor|n"
    else:
        return "standard"


def area_count(refresh=False):
    stats = findStatsMachine()
    if refresh==False and not stats.db.area_counts:
        refresh = True
    if refresh:
        from typeclasses.rooms import ImportedRoom
        counts = {}
        areas = search_tag_object(category='area')
        allrooms = ImportedRoom.objects.all()
        for area in areas:
            counts[area.db_key] = allrooms.filter(db_tags__db_key=area.db_key, db_tags__db_category="room").count()
        stats.db.area_counts = counts
        return (counts)
    else:
        return stats.db.area_counts


def total_rooms_in_area(area, refresh=False):
    if area.lower() == "the drastical mines":
        refresh = True
    stats = findStatsMachine()
    if refresh==False and not stats.db.total_rooms_in_area:
        stats.db.total_rooms_in_area = {}
        refresh = True
    if refresh or area not in stats.db.total_rooms_in_area.keys():
        results = search_tag(area, category="room").count()
        stats.db.total_rooms_in_area[area] = results
        return results
    else:
        return(stats.db.total_rooms_in_area[area])


def claimed_in_area(area, owner):
    if isinstance(owner, int):
        from typeclasses.characters import Character
        o = dbref_to_obj("#"+str(owner), Character)
    else:
        o = search_object(owner)
        if o is not None:
            o = o.first()

    # results = search_tag(area, category='room')
    # results = results.filter(db_attributes__db_key="owner", db_attributes__db_value=o.id)

    results = search_tag(o.id, category='owner')
    results = results.filter(db_tags__db_key=area, db_tags__db_category='area')

    return (results)


def visited_in_area(area, owner):
    matches = []
    if isinstance(owner, int):
        from typeclasses.characters import Character
        o = dbref_to_obj("#"+str(owner), Character)
    else:
        o = search_object(owner)
        if o is not None:
            o = o.first()
    if o.db.stats['visited']:
        if area in o.db.stats['visited'].keys():
            matches = o.db.stats['visited'][area]
    return (matches)


def total_visited(char):
    if str(char).isnumeric():
        char = "#" + str(char)
        o = dbref_to_obj(char)
    else:
        o = search_object(char)
        if o is not None:
            o = o.first()
    if o is None:
        return 0
    totalvisited = 0
    for area in o.db.stats['visited'].keys():
        totalvisited += len(o.db.stats['visited'][area])
    return (totalvisited)


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
    output = sorted([(v.name, round(v.db.stats['gold'], 2)) for v in results if 'gold' in v.db.stats.keys()],
                    key=lambda x: x[1],
                    reverse=True)
    return (output)


def spawnJunk(TRASH_SPAWN_PERCENT=10, BUNDLE_SPAWN_PERCENT=5):
    from world.resource_types import trash
    results = search_tag("random_spawn", category='room')
    ob = None

    for n in range(0, int(results.count() * (TRASH_SPAWN_PERCENT / 100))):
        loc = choice(results)
        create_object(key=trash(), typeclass="typeclasses.resources.Resource", home=loc, location=loc)

    for n in range(0, int(results.count() * (BUNDLE_SPAWN_PERCENT / 100))):
        loc = choice(results)
        create_object(key='resource bundle', typeclass="typeclasses.resources.Resource", home=loc, location=loc,
                      attributes=[('resources', {'wood': randint(0, 10), 'stone': randint(0, 10)})])
