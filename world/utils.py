from django.conf import settings
from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object
from evennia.utils.create import create_object
from evennia.utils.logger import log_err
from evennia import search_channel

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
    counts = {}
    areas = search_tag_object(category='area')
    for area in areas:
        counts[area.db_key.title()] = area.objectdb_set.count()
    return (counts)

def create_exit(exit_name, location, destination, exit_aliases=None, typeclass=None, bidirectional=False):
    """
    Helper function to avoid code duplication.
    At this point we know destination is a valid location

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
            #locks=lockstring,
            #report_to=caller,
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
            rev_exit_obj = create_exit(reverse, exit_obj.destination, exit_obj.location, exit_aliases=rev_alias, typeclass=typeclass)

        return([exit_obj, rev_exit_obj])

def rename_tag(old_tag_name, old_category, new_name, new_category=None):
    from evennia.utils.search import search_tag
    objs = search_tag(old_tag_name, category=old_category)
    for obj in objs:
        obj.tags.add(new_name, category=new_category)
        obj.tags.remove(old_tag_name, category=old_category)

def fixtags():
    areas = { "pawmist": "twilight city of pawmist",
              "erealms": "elven realms",
              "shadval150": "kandahar shadow valley",
              "sdearth": "south dearthwood",
              "edearth": "east dearthwood",
             "avalonch": "avalon",
             "talonvle": "gilda and the dragon",
             "takshrin": "shrine of tahkien",
            "dawn": "city of dawn",
             "tisland": "treasure island",
            "amazon":"the amazon jungle",
            "partbody": "body parts castle",
            "north": "northern road",
            'river': 'durgas river',
            'island': 'island of illusion',
            'east': 'eastern road',
            'demise': 'death room',
            'path': 'the hidden path',
            'gstrong': 'goblin stronghold',
            'plains': 'plains of the north',
            'pyramid': 'the great pyramid',
              'weaverei': 'the dreamweaver\'s path',
            'marsh': 'generic old marsh',
            'tree': 'yggdrasil',
            'zoology': 'mudschool fieldtrip',
            'dock': 'calinth docks',
            'water': 'blizzard water nymphs',
            'chessbrd': 'chessboard'}

    for area in areas.keys():
        for a in ['area','room']:
            rename_tag(area, a, areas[area], a)


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
            search_channel("public")[0].msg(pub_message)
        try:
            caller.location.update_description()
        except Exception as e:
            log_err(str(e))
    caller.msg(caller_message)

