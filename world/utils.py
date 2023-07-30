from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag
from evennia.utils.create import create_object
from evennia.utils.logger import log_err
from world.bookmarks import starts as start_rooms
from random import choice, randint
from core.utils import rainbow
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
        q= ""
        if quality < 10:
            q= "|111trash|n"
        if quality <= 45:
            q= "terrible"
        if quality > 45:
            q= "poor"
        if quality > 70:
            q= "average"
        if quality > 90:
            q= "|ggood|n"
        if quality > 100:
            q= "|rimpressive|n"
        if quality > 110:
            q= "|441exceptional|n"
        if quality > 115:
            q= rainbow("legendary|n")
        return q
    else:
        return "standard"


def exploreReport(user):
    summary = {}
    o = search_object(user)
    if o is not None:
        o = o.first()
        stats = o.db.stats
        seen = stats['visited']
        from world.stats import total_rooms_in_area, claimed_in_area, visited_in_area
        for area in seen.keys():
            total = total_rooms_in_area(area)
            claimed = len(claimed_in_area(area, o))
            visited = len(visited_in_area(area, o))
            summary[area] = {'total': total, 'visited': visited, 'claimed': claimed}
    return summary


def spawnJunk(TRASH_SPAWN_PERCENT=5, BUNDLE_SPAWN_PERCENT=1):
    from world.resource_types import trash
    results = search_tag("random_spawn", category='room')
    ob = None

    for n in range(0, int(results.count() * (TRASH_SPAWN_PERCENT / 100))):
        loc = choice(results)
        create_object(key=trash(), typeclass="typeclasses.resources.Resource", home=loc, location=loc,
                      attributes=[('resources', {'trash': randint(1,10)}),
                                  ('quality', randint(1,60))],
                      tags=[('random_spawn','object')])

    from items.mining import PRO_AXE, REPAIR_KIT
    from evennia.prototypes.spawner import spawn
    for n in range(0, int(results.count() * (BUNDLE_SPAWN_PERCENT / 100))):
        loc = choice(results)
        ob = choice([PRO_AXE, REPAIR_KIT, 0, 0])
        if ob == 0:
            create_object(key='resource bundle', typeclass="typeclasses.resources.Resource", home=loc, location=loc,
                      attributes=[('resources', {'wood': randint(0, 10), 'stone': randint(0, 10)})],
                          tags=[('random_spawn','object')])
        else:
            ob['location'] = loc
            spawn(ob)