from evennia import search_object

def findStatsMachine():
    results = search_object("a stats machine")
    if(len(results) == 0):
        return None
    else:
        for obj in results:
            if(obj.typename == "StatsMachine"):
                return(obj)
    return None
