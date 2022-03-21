from django.conf import settings
from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object, search_tag, search_channel
from evennia.utils.create import create_object
from evennia.utils.logger import log_err
from world.bookmarks import starts as start_rooms
from area_reader.evennia_import import AREA_TRANSLATIONS
from random import choice

from matterhook import Webhook

EXITS_REV = {"up": "down",
             "down": "up",
             "east": "west",
             "west": "east",
             "north": "south",
             "south": "north",
             "in": "out",
             "out": "in"}

EXIT_ALIAS = {"up": "u",
              "down": "d",
              "east": "e",
              "west": "w",
              "north": "n",
              "south": "s"}


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
        train.start_service()


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


def genPrompt(obj):
    if ('caller' in dir(obj)):
        targ = obj.caller
    else:
        targ = obj

    if ('name') in dir(targ):
        name = targ.name[:4].upper()
    elif ('account') in dir(targ):
        name = str(targ.account)[:4].upper()
    else:
        name = "XXXX"

    prompt = "{x%s{r:~{Y>{n " % name

    return (prompt)


def sendWebHook(text):
    if (settings.DRASTICAL_SEND_WEBHOOK):
        mwh = Webhook(settings.DRASTICAL_NOTIFY_URL, settings.DRASTICAL_NOTIFY_HOOK)
        prefix = ":turkey: **" + settings.SERVERNAME + "** - "
        message = prefix + "`" + text + "`"
        mwh.send(message)
        pass


def color_percent(pct):
    if pct == 100:
        pct = "|w100|n"
    elif pct > 95:
        pct = "|r" + str(pct) + '|n'
    elif pct > 80:
        pct = "|R" + str(pct) + '|n'
    elif pct > 50:
        pct = "|y" + str(pct) + "|n"
    elif pct > 30:
        pct = "|Y" + str(pct) + "|n"
    elif pct > 10:
        pct = "|g" + str(pct) + "|n"
    elif pct > 1:
        pct = "|b" + str(pct) + "|n"
    else:
        pct = "|W" + str(pct) + "|n"
    return pct


def color_time(arg):
    if arg == "spring":
        color = "G"
    elif arg == "autumn":
        color = "y"
    elif arg == "summer":
        color = "Y"
    elif arg == "winter":
        color = "C"

    elif arg == "morning":
        color = "Y"
    elif arg == "afternoon":
        color = "y"
    elif arg == "night":
        color = "b"
    else:
        color = "w"
    return color


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
        rooms = allrooms.filter(db_tags__db_key=area.db_key, db_tags__db_category="room")
        counts[area.db_key.title()] = rooms.count()
    return (counts)


def create_exit(exit_name, location, destination, exit_aliases=None, typeclass=None, bidirectional=False):
    """
    Helper function to avoid code duplication.
    At this point we know destination is a valid location
    TODO: Bidirectional doesn't work yet
    """

    location = search_object(location)
    if location is not None:
        location = location[0]
    else:
        return None
    destination = search_object(destination)
    if destination is not None:
        destination = destination[0]
    else:
        return None

    print("create_exit: %s: %s - %s" % (exit_name, location, destination))

    exit_obj = location.search(exit_name, quiet=True, exact=True)
    if len(exit_obj) > 1:
        return None
    elif exit_obj:
        return None
    else:
        ## exit does not exist before. Create a new one.
        # lockstring = self.new_obj_lockstring.format(id=.id)
        if exit_aliases is None:
            exit_aliases = [EXITS_REV[exit_name]]
        if not typeclass:
            typeclass = settings.BASE_EXIT_TYPECLASS
        exit_obj = create_object(
            typeclass,
            key=exit_name,
            location=location,
            aliases=exit_aliases,
            # locks=lockstring,
            # report_to=caller,
        )
        if exit_obj:
            # storing a destination is what makes it an exit!
            exit_obj.destination = destination
            string = (
                ""
                if not exit_aliases
                else " (aliases: %s)" % (", ".join([str(e) for e in exit_aliases]))
            )
            string = "Created new Exit '%s' from %s to %s%s." % (
                exit_name,
                location.name,
                destination.name,
                string,
            )
        else:
            return None

    if not bidirectional:
        return exit_obj

    if exit_obj and bidirectional:
        if exit_name not in EXITS_REV:
            rev_exit_obj = None
        else:
            reverse = EXITS_REV[exit_name]
            rev_alias = EXIT_ALIAS[reverse]
            rev_exit_obj = create_exit(reverse, exit_obj.destination, exit_obj.location, exit_aliases=rev_alias,
                                       typeclass=typeclass)

        return ([exit_obj, rev_exit_obj])


def rename_tag(old_tag_name, old_category, new_name, new_category=None):
    from evennia.utils.search import search_tag
    objs = search_tag(old_tag_name, category=old_category)
    for obj in objs:
        obj.tags.add(new_name, category=new_category)
        obj.tags.remove(old_tag_name, category=old_category)


def fixtags():
    for area in AREA_TRANSLATIONS.keys():
        for a in ['area', 'room']:
            rename_tag(area, a, AREA_TRANSLATIONS[area], a)


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


def combineNames(name1, name2):
    newname = name1[:round(len(name1) / 2)] + name2[1 - len(name2):]
    return newname.strip()


def startContExplorers():
    for area in start_rooms.keys():
        startLocation = '#' + str(choice(list(start_rooms[area])))
        continentExplorer = create_object("typeclasses.mob_explorer.ContinentExplorer", key=area,
                                          location=startLocation, home=startLocation)
