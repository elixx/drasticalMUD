from evennia.utils.search import search_tag
from django.conf import settings
#from world.utils import spawnJunk


def ticker_5min():
    #log("-- start world.ticker.ticker_5min --")
    #
    # # Increment growth rooms
    #log("growth")
    growable = search_tag("growable", category="object")

    # Iterate using queryset.iterator to avoid caching large result sets
    grow_chunk = getattr(settings, "GROWABLE_ITERATOR_CHUNK", 100)
    if hasattr(growable, "iterator"):
        iterator = growable.iterator(chunk_size=grow_chunk)
    else:
        iterator = growable  # fallback if not a queryset

    for obj in iterator:
        # Safeguard against missing attrs
        try:
            if obj.db.age >= 0 and obj.db.planted:
                obj.grow()
        except Exception:
            # If any unexpected object lacks expected attributes, skip
            continue

    # # Junk cleanup
    objs_qs = search_tag("random_spawn", category="object")
    # Only fetch minimal fields to reduce memory; keep instances to preserve delete hooks
    # Must include db_sessid since Evennia's delete() accesses sessions -> db_sessid
    # Also include db_account_id since delete() checks self.account which reads the local FK field.
    if hasattr(objs_qs, "only"):
        objs_qs = objs_qs.only("id", "db_sessid", "db_account_id", "db_location_id", "db_home_id")

    # Configurable limits with safe defaults for constrained systems
    max_delete = getattr(settings, "RANDOM_SPAWN_CLEANUP_MAX_PER_TICK", 500)
    del_chunk = getattr(settings, "RANDOM_SPAWN_CLEANUP_CHUNK_SIZE", 50)

    deleted = 0
    if hasattr(objs_qs, "iterator"):
        for obj in objs_qs.iterator(chunk_size=del_chunk):
            obj.delete()  # use per-object delete to preserve Evennia cleanup hooks
            deleted += 1
            if deleted >= max_delete:
                break
    else:
        # Fallback: handle plain list defensively without loading too many at once
        for obj in objs_qs[:max_delete]:
            obj.delete()

    #log("-- finish world.ticker.ticker_5min --")
    pass


def ticker_daily():
    #log("-- start world.ticker.daily --")
    from world.utils import spawnJunk
    #spawnJunk()

    from typeclasses.shop import Merchant
    merchants = Merchant.objects.all()
    for m in merchants:
        m.new_stock(new_items=6)
    #log("-- finish world.ticker.daily --")
