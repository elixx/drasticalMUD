from evennia.utils import dbref_to_obj
from evennia.utils.search import search_tag_object, search_tag, object_search as search_object
from utils import findStatsMachine


def area_count(unclaimed=False, refresh=False):
    stats = findStatsMachine()
    if (refresh==False and not stats.db.area_counts) or \
       (refresh==False and unclaimed and not stats.db.area_counts_unclaimed):
        refresh = True
    if refresh:
        from typeclasses.rooms import ImportedRoom
        counts = {}
        areas = search_tag_object(category='area')
        allrooms = ImportedRoom.objects.all()
        for area in areas:
            if unclaimed:
                totaltemp = allrooms.filter(db_tags__db_key=area.db_key, db_tags__db_category="room").count()
                totalclaimed = allrooms.filter(db_tags__db_key=area.db_key,
                                               db_tags__db_category="room").filter(db_tags__db_category="owner").count()
                if totaltemp == 0:
                    continue
                if totaltemp > 0 and totalclaimed > 0:
                    counts[area.db_key] = 100-round(totalclaimed / totaltemp * 100,2)
            else:
                counts[area.db_key] = allrooms.filter(db_tags__db_key=area.db_key, db_tags__db_category="room").count()
        if unclaimed:
            stats.db.area_counts_unclaimed = counts
        else:
            stats.db.area_counts = counts
        return (counts)
    else:
        if unclaimed:
            return stats.db.area_counts_unclaimed
        else:
            return stats.db.area_counts


def total_rooms_in_area(area, refresh=False):
    if area.lower() == "the drastical mines":
        refresh = True
    stats = findStatsMachine()
    if refresh==False and not stats.db.total_rooms_in_area:
        stats.db.total_rooms_in_area = {}
        refresh = True
    if refresh or area not in stats.db.total_rooms_in_area.keys():
        results = search_tag(area, category="room").count()
        stats.db.total_rooms_in_area[area] = results
        return results
    else:
        return(stats.db.total_rooms_in_area[area])


def claimed_in_area(area, owner):
    if isinstance(owner, int):
        from typeclasses.characters import Character
        o = dbref_to_obj("#"+str(owner), Character)
    else:
        o = search_object(owner)
        if o is not None:
            o = o.first()

    # results = search_tag(area, category='room')
    # results = results.filter(db_attributes__db_key="owner", db_attributes__db_value=o.id)

    results = search_tag(o.id, category='owner')
    results = results.filter(db_tags__db_key=area, db_tags__db_category='area')

    return (results)


def visited_in_area(area, owner):
    matches = []
    if isinstance(owner, int):
        from typeclasses.characters import Character
        o = dbref_to_obj("#"+str(owner), Character)
    else:
        o = search_object(owner)
        if o is not None:
            o = o.first()
    if o.db.stats['visited']:
        if area in o.db.stats['visited'].keys():
            matches = o.db.stats['visited'][area]
    return (matches)


def total_visited(char):
    if str(char).isnumeric():
        char = "#" + str(char)
        o = dbref_to_obj(char)
    else:
        o = search_object(char)
        if o is not None:
            o = o.first()
    if o is None:
        return 0
    totalvisited = 0
    for area in o.db.stats['visited'].keys():
        totalvisited += len(o.db.stats['visited'][area])
    return (totalvisited)


def topGold():
    from evennia.utils.search import search_object_attribute
    results = search_object_attribute('stats')
    output = sorted([(v.name, round(v.db.stats['gold'], 2)) for v in results if 'gold' in v.db.stats.keys()],
                    key=lambda x: x[1],
                    reverse=True)
    return (output)