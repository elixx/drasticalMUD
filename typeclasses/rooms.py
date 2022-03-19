"""
Room

Rooms are simple containers that has no location of their own.

"""

import re
from django.conf import settings
from evennia import search_object
from evennia.commands.cmdset import CmdSet
from evennia.utils import utils
from evennia.contrib.extended_room import ExtendedRoom
from world.gametime import get_time_and_season
from world.utils import color_time as cc, claimRoom
from world.map import Map

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

RE_FOOTER = re.compile(r"\{xIt is .*?claimed by .*?\.\{n", re.IGNORECASE)


class Room(ExtendedRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    def at_init(self):
        pass
        super().at_init()


class ImportedRoom(Room):
    """
    Rooms imported by area_importer.
    """

    def at_object_creation(self):
        # @py from typeclasses.rooms import ImportedRoom; [obj.at_object_creation() for obj in ImportedRoom.objects.all()]
        super().at_object_creation()
        self.locks.add("ownable:true()")
        self.tags.add('growable', category='room')  # default to able to grow stuff
        self.tags.add('random_spawn', category='room')  # default to possible random loot gen
        self.cmdset.add_default(ImportedRoomCmdSet, permanent=True)

    def at_init(self):
        super().at_init()
        self.update_description()

    def update_description(self):
        update = False
        (season, daytime) = get_time_and_season()
        if season != self.ndb.last_season:
            self.ndb.last_season = season
            update = True
        if daytime != self.ndb.last_timeslot:
            self.ndb.last_timeslot = daytime
            update = True
        if self.ndb.last_owner != self.db.owner:
            self.ndb.last_owner = self.db.owner
            update = True

        if self.db.desc and update == True:
            season = "{" + cc(season) + season + "{x"

            daytime = "{" + cc(daytime) + daytime + "{x"

            if not self.db.owner:
                owner = "{Wnobody{x"
            else:
                owner = search_object('#' + str(self.db.owner))
                if len(owner) > 0:
                    owner = owner[0]
                    owner = '{W' + owner.name + '{x'
                else:
                    owner = "{cnobody{x"

            if "This room is claimed by" in self.db.desc:
                self.db.desc = RE_FOOTER.sub('', self.db.desc)

            self.db.desc += "{xIt is %s %s. This room is claimed by %s.{n" % (season, daytime, owner)

    def return_appearance(self, looker):
        self.update_description()

        string = "%s\n" % Map(looker).show_map()
        # Add all the normal stuff like room description,
        # contents, exits etc.
        string += super().return_appearance(looker)
        return string


class ImportedRoomCmdSet(CmdSet):
    key = "ImportedRoomCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdClaimRoom)


class CmdClaimRoom(COMMAND_DEFAULT_CLASS):
    """
    Claim a room to allow building and resource production.
    Guests may claim unclaimed rooms, but regular players may reclaim from them.
    Future: conflict resolution / trade to allow players reclaiming from players
    """
    key = "claim"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        location = self.caller.location
        claimRoom(caller, location)

