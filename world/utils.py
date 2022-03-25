from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object, search_channel, search_tag
from evennia.utils.create import create_object
from evennia.utils.logger import log_err, log_info
from world.bookmarks import starts as start_rooms
from random import choice
import time

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
        caller.msg("You are warped to {y%s{n." % area.title())
        caller.location.msg_contents("{y%s{n is warped to somewhere in {g%s{n." % (caller.name, area.title()))
        caller.location = dest[0]


def claimRoom(owner, location):
    caller = owner
    area = location.tags.get(category='area')
    area = area.title()
    claim = False

    # Room is unclaimed
    if not location.db.owner:
        pub_message = "{y%s{w is now the owner of {y%s{n in {G%s{n!" % (caller.name, location.name, area)
        caller_message = "You are now the owner of {y%s{n!" % location.name
        claim = True
    # Room is already claimed by caller
    elif location.db.owner == caller.id:
        caller_message = "You already own  %s." % location.name
        pub_message = None
        claim = False
    # Room is already claimed by other
    elif location.db.owner:
        curr_owner = search_object('#' + str(location.db.owner))
        if len(curr_owner) > 0:
            curr_owner = curr_owner[0]
            if caller.permissions.get('guests'):
                claim = False
                caller_message = "%s is already claimed by %s. Guests can only claim unclaimed rooms." % (
                    location.name, curr_owner.name)
            # Allow reclaiming property from guests
            elif curr_owner.permissions.get('guests'):
                claim = True
                caller_message = "You have taken over {y%s{n from {W%s{n!" % (location.name, curr_owner.name)
                pub_message = "{w%s{n has removed {W%s{n's temporary control of {y%s{n in {G%s{n!" % (
                    caller.name, curr_owner.name, location.name, area)
            else:
                claim = True
                caller_message = "You have taken over {y%s{n from {W%s{n!" % (location.name, curr_owner.name)
                pub_message = "{W%s{n has taken over {y%s{n in {G%s{n from {w%s{n!" % (
                    caller.name, location.name, area, curr_owner.name)
                ## TODO: Conflict resolution to result in claim=True
                # caller_message = "%s is already owned by %s." % (location.name, curr_owner.name)
                # claim=False
                # if location.db.last_owner and location.db.last_owner != -1:
                #     last_owner = search_object('#' + str(location.db.last_owner))
                #     if len(last_owner) > 0:
                #         last_owner = last_owner[0]
                #     if caller.id == location.db.last_owner:
                #         caller_message = "You have reclaimed {y%s{n from {W%s{n!" % (location.name, curr_owner.name)
                #         pub_message = "{y%s{w has reclaimed{G %s{w from {Y%s{w!{x" % (caller.name, location.name, owner.name)
                #         claim=True
                #     else:
                #         caller_message = "You have taken over {y%s{n from {W%s{n!" % (location.name, curr_owner.name)
                #         pub_message = "%s has taken over {y%s{n from {W%s{n!" % (caller.name, location.name, curr_owner.name)
    else:
        # This should never happen
        log_err("No owner: typeclasses/rooms.py:132 Caller: %s Location: %s" % (caller.id, location.id))

    if location.access(caller, "ownable") and claim == True:
        location.db.last_owner = location.db.owner
        location.db.owner = caller.id
        if 'claims' in caller.db.stats.keys():
            caller.db.stats['claims'] += 1
        else:
            caller.db.stats['claims'] = 1
        if pub_message is not None:
            channel = search_channel("public")[0].msg(pub_message)
        try:
            caller.location.update_description()
        except Exception as e:
            log_err(str(e))
    caller.msg(caller_message)


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
    start = time.time() ##DEBUG
    from typeclasses.rooms import ImportedRoom
    counts = {}
    areas = search_tag_object(category='area')
    allrooms = ImportedRoom.objects.all()
    for area in areas:
        rooms = allrooms.filter(db_tags__db_key=area.db_key, db_tags__db_category="room")
        counts[area.db_key.title()] = rooms.count()
    end = time.time()  ##DEBUG
    log_err("area_count() took %ss" % (end-start)) ##DEBUG
    return (counts)


def rooms_in_area(area):
    results = search_tag(area,category="room")
    return(results.count())


def claimed_in_area(area, owner):
    results = search_tag(area, category='room')
    results = results.filter(db_attributes__db_key="owner", db_attributes__db_value=owner)
    return(results)


def visited_in_area(area, owner):
    matches = []
    if isinstance(owner, int):
        owner = "#" + str(owner)
    o = search_object(owner)
    if o is not None:
        o=o.first()
        if o.db.stats['visited']:
            if area in o.db.stats['visited'].keys():
                matches = o.db.stats['visited'][area]
    return(matches)


def exploreReport(user):
    summary = {}
    o = search_object(user)
    if o is not None:
        o = o.first()
        asset isinstance(o.db.stats['visited'], dict)
        seen = o.db.stats['visited']
        for area in seen.keys():
            total = rooms_in_area(area)
            claimed = claimed_in_area(area, o)
            visited = visited_in_area(area, o)
            summary[area] = {'total': total, 'visited': visited, 'claimed': claimed}
    return summary