from django.conf import settings
from evennia.utils.create import create_object
from evennia.utils.search import search_object
from core import EXITS_REV, EXIT_ALIAS
from area_reader.evennia_import import AREA_TRANSLATIONS
from random import choice

create = create_object
search = search_object


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


def combineNames(name1, name2):
    newname = name1[:round(len(name1) / 2)] + name2[1 - len(name2):]
    return newname.strip()


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


def createTrain(key="a cosmic train", aliases=['train']):
    train = create_object("typeclasses.movingroom.MovingRoom",
                  key=key,
                  home=None,
                  location=None,
                  aliases=aliases,
                  attributes=[("desc", "A curious train wiggles through spacetime.")],
                          tags=[('drastical','area'),
                                ('drastical', 'room')]
                  )

def fingerPlayer(character):
    start = time.time()  ##DEBUG
    character = self.caller
    if character.db.title:
        title = character.db.title
    else:
        title = ""
    name = title + " " + character.name
    table = self.styled_table()
    logincount = character.db.stats['logins']
    try:
        gold = character.db.stats['gold']
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
    table.add_row("{yName:", name)
    table.add_row("{yTimes Connected:", logincount)
    table.add_row("{yTime Online:", totaltime)
    if pct > -1:
        pct = str(pct) + '%'
    else:
        pct = "???"
    table.add_row("{yPercent Explored:", pct)
    table.add_row("{yGold:", gold)
    output = str(table) + '\n'
    end = time.time()  ##DEBUG
    utils.logger.log_err("CmdScore.func() took %ss" % (end - start))  ##DEBUG
    return(output)