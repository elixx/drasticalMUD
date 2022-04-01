"""
Room

Rooms are simple containers that has no location of their own.

"""

import re
from django.conf import settings
from evennia import search_object
from evennia.commands.cmdset import CmdSet
from evennia.utils import utils
from core.extended_room import ExtendedRoom
from core.gametime import get_time_and_season
from core.utils import color_time as cc
from world.map import Map
from string import capwords
from evennia.utils.search import search_channel

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
        self.cmdset.add_default(ImportedRoomCmdSet, persistent=True)

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


def topClaimed():
    from evennia.utils.search import search_object_attribute
    owned = [str(x.db.owner) for x in search_object_attribute("owner")]
    counts = {}
    for o in owned:
        owner = search_object('#'+o).first().name
        if owner not in counts.keys():
            counts[owner] = 1
        else:
            counts[owner] += 1
    return(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def claimRoom(owner, location):
    caller = owner
    area = location.tags.get(category='area')
    area = capwords(area)
    claim = False

    # Room is unclaimed
    if not location.db.owner:
        pub_message = "{y%s{w is now the owner of {y%s{n in {G%s{n!" % (caller.name, location.name, area)
        caller_message = "You are now the owner of {y%s{n!" % location.name
        claim = True
    # Room is already claimed by caller
    elif location.db.owner == caller.id:
        caller_message = "You already own  %s." % location.name
        pub_message = None
        claim = False
    # Room is already claimed by other
    elif location.db.owner:
        curr_owner = search_object('#' + str(location.db.owner))
        if len(curr_owner) > 0:
            curr_owner = curr_owner[0]
            # Guests can't takeover
            if caller.permissions.get('guests'):
                claim = False
                caller_message = "%s is already claimed by %s. Guests can only claim unclaimed rooms." % (
                    location.name, curr_owner.name)
            # Allow reclaiming property from guests
            elif curr_owner.permissions.get('guests'):
                claim = True
                caller_message = "You have taken over {y%s{n from {W%s{n!" % (location.name, curr_owner.name)
                pub_message = "{w%s{n has removed {W%s{n's temporary control of {y%s{n in {G%s{n!" % (
                    caller.name, curr_owner.name, location.name, area)
            else:
                # TODO: Conflict / Takeover resolution
                claim = True
                caller_message = "You have taken over {y%s{n from {W%s{n!" % (location.name, curr_owner.name)
                pub_message = "{W%s{n has taken over {y%s{n in {G%s{n from {w%s{n!" % (
                    caller.name, location.name, area, curr_owner.name)
                ## TODO: Conflict resolution to result in claim=True
                caller_message = "%s is already owned by %s." % (location.name, curr_owner.name)
                # claim=False
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

    if location.access(caller, "ownable") and claim == True:
        location.db.last_owner = location.db.owner
        location.db.owner = caller.id
        if 'claims' in caller.db.stats.keys():
            caller.db.stats['claims'] += 1
        else:
            caller.db.stats['claims'] = 1
        if pub_message is not None:
            channel = search_channel("public")[0].msg(pub_message)
        try:
            location.update_description()
            if location.db.value:
                location.db.value = location.db.value * 1.25
        except Exception as e:
            log_err(str(e))
    caller.msg(caller_message)