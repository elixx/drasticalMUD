from evennia import search_object
from evennia.utils.create import create_object

def findStatsMachine():
    results = search_object("a stats machine")
    if(len(results) == 0):
        home = search_object("#2")[0]
        obj = create_object("typeclasses.statsmachine.StatsMachine",
                            key="a stats machine",
                            home=home,
                            location=home)
        return(obj)
    else:
        for obj in results:
            if(obj.typename == "StatsMachine"):
                return(obj)
    return

def genPrompt(obj):
    if('caller' in dir(obj)):
        targ = obj.caller
    else:
        targ = obj

    if('name') in dir(targ):
        name = targ.name[:4].upper()
    elif('account') in dir(targ):
        name = str(targ.account)[:4].upper()
    else:
        name = "XXXX"

    prompt = "{x%s{r:~{Y>{n " % name

    return(prompt)