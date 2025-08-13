from evennia.utils.search import search_tag
from evennia.utils.search import search_tag
from world.utils import spawnJunk


def ticker_5min():
    log("-- start world.ticker.ticker_5min --")
    #
    # # Increment growth rooms
    log("growth")
    growable = search_tag("growable",category="object")
    for obj in growable:
        if obj.db.age >= 0 and obj.db.planted:
            obj.grow()


    log("-- finish world.ticker.ticker_5min --")
    pass


def ticker_daily():
    log("-- start world.ticker.daily --")
    spawnJunk()

    from typeclasses.shop import Merchant
    merchants = Merchant.objects.all()
    for m in merchants:
        m.new_stock(new_items=6)
    log("-- finish world.ticker.daily --")