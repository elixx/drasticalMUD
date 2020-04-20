"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""
from evennia.utils.create import create_object
from evennia import search_object
from world.utils import findStatsMachine


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """

    if not findStatsMachine():
        home = search_object("#2")[0]
        obj = create_object("typeclasses.statsmachine.StatsMachine",
                                           key="a stats machine",
                                           home=home,
                                           location=home)
    pass


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    statsmachine = findStatsMachine()
    if not statsmachine:
        pass
    else:
        stats = statsmachine.db.stats
        stats['server_stop'] += 1
    pass


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    statsmachine = findStatsMachine()
    if not statsmachine:
        pass
    else:
        stats = statsmachine.db.stats
        stats['reload_start'] += 1
    pass


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    statsmachine = findStatsMachine()
    if not statsmachine:
        pass
    else:
        stats = statsmachine.db.stats
        stats['reload_stop'] += 1
    pass



def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    statsmachine = findStatsMachine()
    if not statsmachine:
        pass
    else:
        stats = statsmachine.db.stats
        stats['cold_start'] += 1

    pass


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    statsmachine = findStatsMachine()
    if not statsmachine:
        pass
    else:
        stats = statsmachine.db.stats
        stats['cold_stop'] += 1
    pass
