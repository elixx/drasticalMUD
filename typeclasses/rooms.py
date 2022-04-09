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
from evennia.utils.utils import list_to_string

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

RE_FOOTER = re.compile(r"\|xIt is .*? .*? by .*?\|x\.", re.IGNORECASE)


class Room(ExtendedRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    def return_appearance(self, looker, **kwargs):
        """
        Main callback used by 'look' for the object to describe itself.
        This formats a description. By default, this looks for the `appearance_template`
        string set on this class and populates it with formatting keys
            'name', 'desc', 'exits', 'characters', 'things' as well as
            (currently empty) 'header'/'footer'.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call. This is passed into the helper
                methods and into `get_display_name` calls.

        Returns:
            str: The description of this entity. By default this includes
                the entity's name, description and any contents inside it.

        Notes:
            To simply change the layout of how the object displays itself (like
            adding some line decorations or change colors of different sections),
            you can simply edit `.appearance_template`. You only need to override
            this method (and/or its helpers) if you want to change what is passed
            into the template or want the most control over output.

        """

        if not looker:
            return ""

        # ourselves
        name = self.get_display_name(looker, **kwargs)
        desc = self.db.desc or "You see nothing special."

        # contents
        content_names_map = self.get_content_names(looker, **kwargs)

        # clickable exits
        exits = list_to_string(
            ["|lc%s|lt%s|le" % (re.sub('\(.*\)', '', exit), exit) for exit in content_names_map["exits"]])

        characters = list_to_string(content_names_map["characters"])

        # clickable things
        temp="|lc%s %s|lt%s|le"
        things = list_to_string([temp % ("get", obj,obj) if obj.access(looker, 'get') else temp % ("look", obj, obj) for obj in self.get_visible_contents(looker)['things'] ])

        # populate the appearance_template string. It's a good idea to strip it and
        # let the client add any extra spaces instead.

        return self.appearance_template.format(
            header="",
            name=name,
            desc=desc if not looker.db.OPTION_BRIEF else "",
             exits=f"|wExits:|n {exits}" if exits else "",
            #exits=f"|wExits:|n %s" % exits if exits else "",
            characters=f"\n|wCharacters:|n {characters}" if characters else "",
            things=f"\n|wYou see:|n {things}" if things else "",
            footer="",
        ).strip()


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
            season = "|" + cc(season) + season + "|x"

            daytime = "|" + cc(daytime) + daytime + "|x"

            if not self.db.owner:
                owner = "{Wnobody{x"
            else:
                owner = search_object('#' + str(self.db.owner))
                if len(owner) > 0:
                    owner = owner[0]
                    owner = '|W' + owner.name + '|x'
                else:
                    owner = "{Wnobody{x"

            if "ltclaimed" in self.db.desc:
                self.db.desc = RE_FOOTER.sub('', self.db.desc)
            if self.db.value:
                self.db.desc += "|xIt is %s %s. This room is worth |y%s gold|x and |lcclaim|ltclaimed|le by %s|x." % (
                season, daytime, self.db.value, owner)
            else:
                self.db.desc += "|xIt is %s %s. This room is |lcclaim|ltclaimed|le by %s|x." % (season, daytime, owner)

    def return_appearance(self, looker, **kwargs):
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
    Future will include trade of owned property between players.

    """
    key = "claim"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        location = self.caller.location
        area = capwords(location.tags.get(category='area'))
        balance = caller.db.stats['gold'] if caller.db.stats['gold'] else 0
        cost = location.db.value if location.db.value else 0
        claim = False
        caller_message = None
        if caller.id == location.db.owner:
            caller_message = "You already are the owner of |c%s|n." % location.name
        elif balance < cost:
            caller_message = "You don't have enough gold. %s costs |y%s gold|n to own." % (location.name, cost)
        elif not location.db.owner:
            ui = yield ("Are you sure you want to take |c%s|n for |Y%s gold|n? Type |c|lcyes|ltyes|le|n if sure." % (
                location.name, cost))
            if ui.strip().lower() in ['yes', 'y']:
                claim = True
                caller_message = "You now own {y%s{n." % location.name
                pub_message = "{w%s{n has taken over {y%s{n in {G%s{n!" % (caller.name, location.name, area)
        elif location.db.owner == caller.id:
            caller_message = "You already own %s." % location.name
        else:
            curr_owner = '#' + str(location.db.owner)
            curr_owner = search_object(curr_owner)
            if curr_owner is not None: curr_owner = curr_owner.first()

            ui = yield ("Are you sure you want to take |c%s|n from |R%s|n for |Y%s gold|n? Type {Cyes{n if sure." % (
                location.name, curr_owner.name, cost))
            if ui.strip().lower() in ['yes', 'y']:
                claim = True
                caller.db.stats['takeovers'] += 1
                caller_message = "You have taken over {y%s{n from {W%s{n!" % (location.name, curr_owner.name)
                pub_message = "{w%s{n has removed {W%s{n's control of {y%s{n in {G%s{n!" % (
                    caller.name, curr_owner.name, location.name, area)

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
                    location.db.value = int(location.db.value * 1.5)
                caller.db.stats['gold'] -= cost
            except Exception as e:
                utils.logger.log_err(str(e))
        caller.msg(caller_message)


def topClaimed():
    from evennia.utils.search import search_object_attribute
    owned = [str(x.db.owner) for x in search_object_attribute("owner")]
    counts = {}
    for o in owned:
        owner = search_object('#' + o).first().name
        if owner not in counts.keys():
            counts[owner] = 1
        else:
            counts[owner] += 1
    return (sorted(counts.items(), key=lambda x: x[1], reverse=True))
