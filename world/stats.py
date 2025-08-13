from django.core.cache import cache
from evennia.utils import dbref_to_obj
from evennia.utils.search import search_tag_object, search_tag, object_search as search_object
from world.utils import findStatsMachine

# Cache helpers and leaderboards for web toplists
# TTLs:
# - toplist_stats_v1 (web/custom._toplist_stats): 60 seconds
# - topClaimed_v1 (typeclasses.rooms.topClaimed): 300 seconds (5 minutes)
# - topGold_v1 (world.stats.topGold): 300 seconds (5 minutes)
# - total_visited_v1:<id> (world.stats.total_visited): 600 seconds (10 minutes)
# Invalidation:
# - invalidate_toplist_context(): clears the web toplist context cache
# - invalidate_topGold_cache(): clears topGold and web toplist context caches
# - invalidate_topClaimed_cache(): clears topClaimed and web toplist context caches


def invalidate_toplist_context():
    """Invalidate only the toplist page context cache (60s TTL by default)."""
    cache.delete("toplist_stats_v1")


def invalidate_topGold_cache():
    """Invalidate the gold leaderboard and toplist context caches."""
    cache.delete("topGold_v1")
    cache.delete("toplist_stats_v1")


def invalidate_topClaimed_cache():
    """Invalidate the claimed-rooms leaderboard and toplist context caches."""
    cache.delete("topClaimed_v1")
    cache.delete("toplist_stats_v1")


def invalidate_total_visited_cache(char_id):
    """Invalidate cached total_visited for a specific character id.

    Args:
        char_id (int|str): Character id or string that can be cast to int.
    """
    try:
        oid = int(str(char_id).lstrip("#"))
    except Exception:
        return
    cache.delete(f"total_visited_v1:{oid}")


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
        return counts
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
        return stats.db.total_rooms_in_area[area]


def claimed_in_area(area, owner):
    if isinstance(owner, int):
        from typeclasses.characters import Character
        o = dbref_to_obj("#"+str(owner), Character)
    else:
        o = search_object(owner)
        if o is not None:
            o = o.first()

    results = search_tag(o.id, category='owner')
    results = results.filter(db_tags__db_key=area, db_tags__db_category='area')

    return results


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
    return matches


def total_visited(char):
    """Return total number of rooms visited by a character.

    Accepts a Character object, name, numeric id, or dbref string ("#<id>").
    Results are cached per character id for a short time to speed up toplists.
    TTL: 600 seconds. Invalidation currently relies on TTL.
    """
    # Resolve character object
    if hasattr(char, "db") and hasattr(char, "id"):
        o = char
    elif str(char).lstrip("#").isnumeric():
        # Numeric id or dbref; resolve via dbref_to_obj with Character class
        from typeclasses.characters import Character
        dbref = "#" + str(char).lstrip("#")
        o = dbref_to_obj(dbref, Character)
    else:
        o = search_object(char)
        if o is not None:
            o = o.first()
    if o is None:
        return 0

    # Try cache by object id
    try:
        oid = int(o.id)
    except Exception:
        oid = None
    if oid is not None:
        cache_key = f"total_visited_v1:{oid}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    stats = getattr(o.db, "stats", None) or {}
    visited = stats.get("visited") or {}
    totalvisited = 0
    for area in visited.keys():
        totalvisited += len(visited[area])

    if oid is not None:
        # Cache for 10 minutes
        cache.set(cache_key, totalvisited, timeout=600)
    return totalvisited


def topGold():
    """Return leaderboard of (name, gold) sorted by gold desc.

    This can be expensive since it scans objects with 'stats'. Cache the
    result for a short period to make /toplist responsive under load.
    TTL: 300 seconds. Invalidated when gold changes.
    """
    cache_key = "topGold_v1"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    from evennia.utils.search import search_object_attribute
    results = search_object_attribute('stats')
    output = sorted(
        [(v.name, round(v.db.stats['gold'], 2)) for v in results if 'gold' in v.db.stats.keys()],
        key=lambda x: x[1],
        reverse=True,
    )
    # Cache for 5 minutes; adjust if needed
    cache.set(cache_key, output, timeout=300)
    return output
