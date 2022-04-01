from matterhook import Webhook
from django.conf import settings

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


def sendWebHook(text):
    if (settings.DRASTICAL_SEND_WEBHOOK):
        mwh = Webhook(settings.DRASTICAL_NOTIFY_URL, settings.DRASTICAL_NOTIFY_HOOK)
        prefix = ":turkey: **" + settings.SERVERNAME + "** - "
        message = prefix + "`" + text + "`"
        mwh.send(message)
        pass


def genPrompt(obj):
    if ('caller' in dir(obj)):
        targ = obj.caller
    else:
        targ = obj
    if ('name') in dir(targ):
        name = targ.name[:4].upper()
    elif ('account') in dir(targ):
        name = str(targ.account)[:4].upper().replace('I','i')
    else:
        name = "XXXX"

    loc = "~"
    perms = targ.permissions.all()
    permitted = ("builder" in perms) or ("admin" in perms)
    if permitted and targ.location:
        loc = "#%s" % targ.location.id

    prompt = "{x%s{r:%s{Y>{n " % (name, loc)

    return (prompt)


