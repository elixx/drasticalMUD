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
from evennia.utils.logger import log_err
from world.gametime import get_time_and_season

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
        #@py from typeclasses.rooms import LegacyRoom; [obj.at_object_creation() for obj in LegacyRoom.objects.all()]
        super().at_object_creation()
        self.locks.add("ownable:true()")
        self.tags.add('growable',category='room')
        self.tags.add('random_spawn',category='room')
        self.cmdset.add_default(LegacyRoomCmdSet, permanent=True)

    def at_init(self):
        super().at_init()
        self.update_description()

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

class LegacyRoomCmdSet(CmdSet):
    key = "LegacyRoomCmdSet"
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
        claim=False

        # Room is unclaimed
        if not location.db.owner:
            pub_message = "{Y%s{w is now the owner of {G%s{n!" % (caller.name, location.name)
            caller_message = "You are now the owner of {G%s{n!" % location.name
            claim=True
        # Room is already claimed by caller
        elif location.db.owner == caller.id:
                caller_message = "You already own  %s." % location.name
                pub_message = None
                claim=False
        # Room is already claimed by other
        elif location.db.owner:
            curr_owner = search_object('#' + str(location.db.owner))
            if len(curr_owner) > 0:
                curr_owner = curr_owner[0]
                if caller.permissions.get('guests'):
                    claim=False
                    caller_message = "%s is already claimed by %s. Guests can only claim unclaimed rooms." % (location.name, curr_owner.name)
                # Allow reclaiming property from guests
                elif curr_owner.permissions.get('guests'):
                    claim=True
                    caller_message = "You have taken over {y%s{n from {W%s{n!" % (location.name, curr_owner.name)
                    pub_message = "%s has taken over {y%s{n from {W%s{n!" % (caller.name, location.name, curr_owner.name)
                else:
                    caller_message = "%s is already owned by %s." % (location.name, curr_owner.name)
                    claim=False
                    ## TODO: Conflict resolution to result in claim=True
                    # if location.db.last_owner and location.db.last_owner != -1:
                    #     last_owner = search_object('#' + str(location.db.last_owner))
                    #     if len(last_owner) > 0:
                    #         last_owner = last_owner[0]
                    #     if caller.id == location.db.last_owner:
                    #         caller_message = "You have reclaimed {y%s{n from {W%s{n!" % (location.name, curr_owner.name)
                    #         pub_message = "{y%s{w has reclaimed{G %s{w from {Y%s{w!{x" % (caller.name, location.name, owner.name)
                    #         claim=True
                    #     else:
                    #         caller_message = "You have taken over {y%s{n from {W%s{n!" % (location.name, curr_owner.name)
                    #         pub_message = "%s has taken over {y%s{n from {W%s{n!" % (caller.name, location.name, curr_owner.name)
        else:
            # This should never happen
            log_err("No owner: typeclasses/rooms.py:132 Caller: %s Location: %s" % (caller.id, location.id))

        if location.access(caller, "ownable") and claim==True:
            location.db.last_owner = location.db.owner
            location.db.owner = caller.id
            if pub_message is not None:
                search_channel("public")[0].msg(pub_message)
            try:
                self.caller.location.update_description()
            except:
                pass
        self.caller.msg(caller_message)

