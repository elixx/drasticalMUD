import datetime
from django.conf import settings
from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object, search_tag
from evennia.utils.create import create_object
from evennia.utils.logger import log_info as log
from django.conf import settings

from matterhook import Webhook

MONTHS_PER_YEAR = settings.MONTHS_PER_YEAR
SEASONAL_BOUNDARIES = settings.SEASONAL_BOUNDARIES
HOURS_PER_DAY = settings.HOURS_PER_DAY
DAY_BOUNDARIES = settings.DAY_BOUNDARIES

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


def get_time_and_season():
    from evennia import gametime
    """
    Calculate the current time and season ids.
    """
    # get the current time as parts of year and parts of day.
    # we assume a standard calendar here and use 24h format.
    timestamp = gametime.gametime(absolute=True)
    # note that fromtimestamp includes the effects of server time zone!
    datestamp = datetime.datetime.fromtimestamp(timestamp)
    season = float(datestamp.month) / MONTHS_PER_YEAR
    timeslot = float(datestamp.hour) / HOURS_PER_DAY

    # figure out which slots these represent
    if SEASONAL_BOUNDARIES[0] <= season < SEASONAL_BOUNDARIES[1]:
        curr_season = "spring"
    elif SEASONAL_BOUNDARIES[1] <= season < SEASONAL_BOUNDARIES[2]:
        curr_season = "summer"
    elif SEASONAL_BOUNDARIES[2] <= season < 1.0 + SEASONAL_BOUNDARIES[0]:
        curr_season = "autumn"
    else:
        curr_season = "winter"

    if DAY_BOUNDARIES[0] <= timeslot < DAY_BOUNDARIES[1]:
        curr_timeslot = "night"
    elif DAY_BOUNDARIES[1] <= timeslot < DAY_BOUNDARIES[2]:
        curr_timeslot = "morning"
    elif DAY_BOUNDARIES[2] <= timeslot < DAY_BOUNDARIES[3]:
        curr_timeslot = "afternoon"
    else:
        curr_timeslot = "evening"

    return curr_season, curr_timeslot

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

def global_ticker():
    #log("-- start global_tick --")

    # Increment growth room age
    growable = search_tag("growable")
    for obj in growable:
        if not obj.db.age:
            obj.db.age = 1
        else:
            obj.db.age += 1

    # Gather earnings
    #owned = search_object()

    #log("-- finish global_tick --")


def area_count():
    areas = []

    x = search_tag_object(category='area')
    for n in x:
        areas.append(n.db_key)

    counts = {}
    for area in areas:
        c = search_tag(area, category="area")
        x = c.filter(db_typeclass_path__contains="room")
        counts[area.title()] = len(x)
    return (counts)
