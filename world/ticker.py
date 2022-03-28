from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object, search_tag
from evennia.utils.logger import log_info as log

def global_tick():
    log("-- start global_tick --")
    #
    # # Increment growth rooms
    log("growth")
    growable = search_tag("growable",category="object")
    for obj in growable:
        if obj.db.age >= 0 and obj.db.planted:
            obj.grow()
    #
    # log("spawnage")
    # # Spawn items
    # spawnable = search_tag("spawnitems", category='room')
    # for obj in spawnable:
    #     obj.db.age += 1
    #
    log("-- finish global_tick --")
    pass