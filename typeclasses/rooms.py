"""
Room

Rooms are simple containers that has no location of their own.

"""

import re
from django.conf import settings
from evennia import DefaultRoom
from evennia import search_object
from evennia import search_channel
from evennia.commands.cmdset import CmdSet
from evennia.utils import utils
from world.utils import get_time_and_season

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

RE_FOOTER = re.compile(r"\{xIt is .*?claimed by .*?\.\{n", re.IGNORECASE)

class Room(DefaultRoom):
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


class LegacyRoom(Room):
    """
    Rooms imported by area_importer. This is becoming the new base class.
    """

    def at_object_creation(self):
        #@py from typeclasses.objects import Heavy; [obj.at_object_creation() for obj in Heavy.objects.all()]
        super().at_object_creation()
        self.db.owner = -1
        self.db.last_owner = -1
        self.locks.add("ownable:true()")
        self.cmdset.add_default(LegacyRoomCmdSet, permanent=True)

    def at_init(self):
        super().at_init()

    def update_description(self):
        update=False
        (season, daytime) = get_time_and_season()
        if season != self.ndb.last_season:
            self.ndb.last_season = season
            update=True
        if daytime != self.ndb.last_timeslot:
            self.ndb.last_timeslot = daytime
            update=True
        if self.ndb.last_owner != self.db.owner:
            self.ndb.last_owner = self.db.owner
            update=True

        if self.db.desc and update==True:
            if season == "spring":
                color = "G"
            elif season == "autumn":
                color = "y"
            elif season == "summer":
                color = "Y"
            elif season == "winter":
                color = "C"
            else:
                color = "w"
            season = "{" + color + season + "{x"

            if daytime == "morning":
                color = "Y"
            elif daytime == "afternoon":
                color = "y"
            elif daytime == "night":
                color = "b"
            else:
                color = "w"
            daytime = "{" + color + daytime + "{x"

            if self.db.owner == -1:
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

class LegacyRoomCmdSet(CmdSet):
    key = "LegacyRoomCmdSet"
    def at_cmdset_creation(self):
        self.add(CmdClaimRoom)

class CmdClaimRoom(COMMAND_DEFAULT_CLASS):
    key = "claim"
    locks = "cmd:all()"
    def func(self):
        caller = self.caller
        location = self.caller.location
        if location.db.owner and location.db.owner != -1:
            owner = search_object('#' + str(location.db.owner))
            if len(owner) > 0:
                owner = owner[0]
        if location.db.last_owner and location.db.last_owner != -1:
            last_owner = search_object('#' + str(location.db.last_owner))
            if len(last_owner) > 0:
                last_owner = last_owner[0]
        if location.db.owner == caller.id:
            caller.msg("You already have claimed this property.")
        else:
            if location.access(caller, "ownable"):
                if caller.id == location.db.last_owner:
                    message = "{y%s{w has reclaimed{G %s{w from {Y%s{w!{x" % (caller.name, location.name, owner.name)
                else:
                    message = "{Y%s{w is now the owner of {G%s{n!" % (caller.name, location.name)
                location.db.last_owner = location.db.owner
                location.db.owner = caller.id
                self.caller.msg("You are now the owner of %s." % self.caller.location.name)
                search_channel("public")[0].msg(message)
                self.caller.location.update_description()