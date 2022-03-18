from django.conf import settings
from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object
from evennia.utils.create import create_object

from matterhook import Webhook

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
        pct = "|wCOMPLETE|n"
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
    elif pct > 5:
        pct = "|b" + str(pct) + "|n"
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

