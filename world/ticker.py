from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object, search_tag


def global_tick():
    # log("-- start global_tick --")

    # Increment growth rooms
    growable = search_tag("growable", category='room')
    for obj in growable:
        if obj.db.fertility:
            fertility = obj.db.fertility
        else:
            fertility = 1
        if not obj.db.growth:
            pass
        else:
            obj.db.growth += (1 * fertility)

    # Spawn items
    spawnable = search_tag("spawnitems", category='room')
    for obj in spawnable:
        if not obj.db.age:
            obj.db.age = 1
        else:
            obj.db.age += 1

    # log("-- finish global_tick --")
