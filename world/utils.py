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
    caller = obj.caller
    ps1 = caller.name[:4].upper()
    prompt = "{x%s{r:~{Y>{n " % ps1
    return(prompt)