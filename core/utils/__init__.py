from django.conf import settings
from evennia.utils.create import create_object
from evennia.utils.search import search_object, search_account
from core import EXITS_REV, EXIT_ALIAS
from area_reader.evennia_import import AREA_TRANSLATIONS
from random import choice, randint
from evennia.utils.evtable import EvTable as styled_table
from evennia.utils.logger import log_err, log_info
from datetime import datetime

EXIT_TYPECLASS = "typeclasses.exits.LegacyExit"

create = create_object
search = search_object


def color_percent(pct):
    if pct == 100:
        pct = "|W|*100|n"
    elif pct > 95:
        pct = "|551" + str(pct) + '|n'
    elif pct > 80:
        pct = "|440" + str(pct) + '|n'
    elif pct > 50:
        pct = "|330" + str(pct) + "|n"
    elif pct > 30:
        pct = "|220" + str(pct) + "|n"
    elif pct > 10:
        pct = "|121" + str(pct) + "|n"
    elif pct > 1:
        pct = "|011" + str(pct) + "|n"
    else:
        pct = "|x" + str(pct) + "|n"
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


def combineNames(name1, name2):
    newname = name1[:round(len(name1) / 2)] + name2[1 - len(name2):]
    return newname.strip()


def create_exit(exit_name, location, destination, exit_aliases=None, typeclass=EXIT_TYPECLASS, bidirectional=False):
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

    #print("create_exit: %s: %s - %s" % (exit_name, location, destination))

    exit_obj = location.search(exit_name, quiet=True, exact=True)
    if len(exit_obj) > 1:
        return None
    elif exit_obj:
        return None
    else:
        ## exit does not exist before. Create a new one.
        if exit_aliases is None:
            exit_aliases = [EXITS_REV[exit_name]]

        exit_obj = create_object(
            typeclass,
            key=exit_name,
            location=location,
            aliases=exit_aliases,
            locks=['puppet:false()', 'get:false()'],
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


def createTrain(key="a cosmic train", aliases=['train']):
    train = create_object("typeclasses.movingroom.MovingRoom",
                          key=key,
                          home=None,
                          location=None,
                          aliases=aliases,
                          attributes=[("desc", "A curious train wiggles through spacetime.")],
                          tags=[('drastical', 'area'),
                                ('drastical', 'room')]
                          )


def fingerPlayer(character, privileged=False):
    character = search_object(character)
    if character is not None:
        character = character[0]
    else:
        return False
    if character.db.title:
        title = character.db.title
    else:
        title = ""
    name = title + " " + character.name
    table = styled_table(border="none")
    logincount = character.db.stats['logins']
    try:
        gold = round(character.db.stats['gold'],2)
    except KeyError:
        gold = 0
        character.db.stats['gold'] = gold
    if 'conn_time' in character.db.stats.keys():
        totaltime = character.db.stats['conn_time']
        m, s = divmod(totaltime.seconds, 60)
        h, m = divmod(m, 60)
        totaltime = "%dh %02dm %02ds" % (h, m, s)
    else:
        totaltime = '-'
    if 'explored' in character.db.stats.keys():
        pct = character.db.stats['explored']
    else:
        pct = -1
    #######################################################################
    table.add_row(ff("Target name:"), fade(name,rmin=1,bmin=1,gmin=1))
    table.add_row(ff("Times Connected:"), logincount)
    table.add_row(ff("Time Online:"), totaltime)
    if pct > -1:
        pct = str(pct) + '%'
    else:
        pct = "???"
    table.add_row(ff("Percent Explored:"), pct)
    table.add_row(ff("Gold:"), gold)
    if privileged:
        log = character.db.lastsite
        if log is None:
            ac = search_account(character)[0]
            log = ac.db.lastsite
            if log is None:
                raise("NoLoginHistory")
        table.add_row()
        table.add_row(fade("  Timestamp",rmin=1), fade("{yConnecting IP",rmin=1))
        count = 0
        for (ip, time) in log:
            count += 1
            table.add_row("  " + str(datetime.fromtimestamp(time)), ip)

    output = str(table) + '\n'
    return (output)

def fade(s, rmin=0, rmax=5, gmin=0, gmax=5, bmin=0, bmax=5, ascending=True):
    r = rmin if ascending else rmax
    g = gmin if ascending else gmax
    b = bmin if ascending else bmax
    r1 = g1 = b1 = True
    o = ""
    skip = False
    for (i, c) in enumerate(s):
        if c in ['{', '|']:
            skip = True
            continue
        elif skip == True:
            skip = False
            continue
        o += '|%s%s%s%s' % (r, g, b, c)
        r1 = False if r >= rmax else True if r <= rmin else r1
        g1 = False if g >= gmax else True if g <= gmin else g1
        b1 = False if b >= bmax else True if b <= bmin else b1
        r += 1 if r1 else -1
        g += 1 if g1 else -1
        b += 1 if b1 else -1
    return o+'|n'

def rainbow(s, r1=None, rmin=1, rmax=5, g1=None, gmin=1, gmax=5, b1=None, bmin=1, bmax=5):
    r=g=b=1
    o = ""
    skip = False
    for (i, c) in enumerate(s):
        if c in ['{', '|']:
            skip = True
            continue
        elif skip == True:
            skip = False
            continue
        r = randint(rmin,rmax) if r1 is None else r1
        g = randint(gmin,gmax) if g1 is None else g1
        b = randint(bmin,bmax) if b1 is None else b1
        o += '|%s%s%s%s' % (r, g, b, c)
    return o+'|n'

def ff(s, r=1, rx=3, b=1, bx=3, g=0, gx=5):
    return fade(s,rmin=r,rmax=rx,bmin=b,bmax=bx,gmin=g,gmax=gx)