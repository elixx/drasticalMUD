from django.conf import settings
from evennia import utils
from evennia.typeclasses.attributes import AttributeProperty
from evennia.commands.cmdset import CmdSet
from typeclasses.rooms import Room
from typeclasses.objects import Item
from random import randint, choice, random
from evennia.utils.create import create_object
from evennia.utils.logger import log_info
from evennia.utils import list_to_string
from world.map import Map
from world.utils import qual
from core import EXITS_REV, EXIT_ALIAS
from core.utils import rainbow
from world.resource_types import SIZES
import re
from core.utils import create_exit

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

class MiningRoom(Room):
    RE_FOOTER = re.compile(r"Coordinates: \(.*\) Mining Level: [0-9]+", re.IGNORECASE)

    # quality is used as level for tool check
    mining_level = AttributeProperty(default=1, autocreate=True)
    # how often stuff will drop when mining a wall
    drop_rate = AttributeProperty(default=-1, autocreate=True)
    # depth from entry
    depth = AttributeProperty(default=0, autocreate=True)
    # how long is left on given wall
    lifespan = AttributeProperty(default={"north": 10,
                                          "south": 10,
                                          "west": 10,
                                          "east": 10,
                                          "down": 40,
                                          "up": 40}, autocreate=True)

    @property
    def x(self):
        """Return the X coordinate or None."""
        x = self.tags.get(category="mining_x")
        return int(x) if isinstance(x, str) else None

    @x.setter
    def x(self, x):
        """Change the X coordinate."""
        old = self.tags.get(category="mining_x")
        if old is not None:
            self.tags.remove(old, category="mining_x")
        if x is not None:
            self.tags.add(str(x), category="mining_x")

    @property
    def y(self):
        """Return the Y coordinate or None."""
        y = self.tags.get(category="mining_y")
        return int(y) if isinstance(y, str) else None

    @y.setter
    def y(self, y):
        """Change the Y coordinate."""
        old = self.tags.get(category="mining_y")
        if old is not None:
            self.tags.remove(old, category="mining_y")
        if y is not None:
            self.tags.add(str(y), category="mining_y")

    @property
    def z(self):
        """Return the Z coordinate or None."""
        z = self.tags.get(category="mining_z")
        return int(z) if isinstance(z, str) else None

    @z.setter
    def z(self, z):
        """Change the Z coordinate."""
        old = self.tags.get(category="mining_z")
        if old is not None:
            self.tags.remove(old, category="mining_z")
        if z is not None:
            self.tags.add(str(z), category="mining_z")

    @classmethod
    def get_room_at(cls, x, y, z):
        """
        Return the room at the given location or None if not found.

        Args:
            x (int): the X coord.
            y (int): the Y coord.
            z (int): the Z coord.

        Return:
            The room at this location (Room) or None if not found.

        """
        rooms = cls.objects.filter(
            db_tags__db_key=str(x), db_tags__db_category="mining_x").filter(
            db_tags__db_key=str(y), db_tags__db_category="mining_y").filter(
            db_tags__db_key=str(z), db_tags__db_category="mining_z")
        if rooms:
            return rooms[0]

        return None

    def return_appearance(self, looker, **kwargs):
        string = "%s\n" % Map(looker).show_map()
        # Add all the normal stuff like room description,
        # contents, exits etc.
        string += super().return_appearance(looker)
        return string

    def update_description(self):
        shortdesc = "Coordinates: (%s, %s, %s) Mining Level: %s" % (self.x, self.y, self.z, self.mining_level)
        self.ndb.shortdesc = shortdesc
        if "Coordinates" in self.db.desc:
            self.db.desc = self.RE_FOOTER.sub('', self.db.desc)
        self.db.desc += '\n' + shortdesc

    def at_object_creation(self):
        if not self.db.desc:
            self.db.desc = "This looks like a good place for mining."
        self.tags.add("minable", "room")
        if self.x is None:
            self.x = 0
        if self.y is None:
            self.y = 0
        if self.z is None:
            self.z = 0

        for key in self.lifespan.keys():
            self.lifespan[key] += int( self.lifespan[key] * self.depth * 1.65 )

        lifespan = self.lifespan

    def at_init(self):
        coordstring = "Coordinates: (%s, %s, %s) Mining Level: %s" % (self.x, self.y, self.z, self.mining_level)
        self.ndb.shortdesc = coordstring
        if self.db.desc:
            if "Coordinates" not in self.db.desc:
                self.update_description()
        mining_level = self.mining_level
        lifespan = self.lifespan

    def mining_callback(self, character, tool, direction):
        character.msg("You chip away %s with %s." % (direction, tool.name))

        # Clear Busy
        from evennia.scripts.taskhandler import TaskHandler
        th = TaskHandler()
        task = th.get_deferred(character.db.busy_handler)
        if task is not None:
            task.cancel()
        character.db.is_busy = False
        character.db.busy_doing = None

        # Get resource bundle
        resources = {'trash': choice([0, 0, 0, randint(0, 10)]),
                     'stone': randint(1+int(self.mining_level + self.depth / 2), int(10 * self.mining_level / 2) + self.depth)}
        result = ["|Y%s|n: |w%s|n" % (k.title(), v) for k, v in resources.items()]
        agg = sum(resources.values())
        bundlename = "%s resource bundle" % SIZES(agg)
        bundle = create_object(key=bundlename, typeclass="typeclasses.resources.Resource", home=character,
                               location=character, attributes=[('resources', resources)])
        character.msg("You get %s of %s quality, containing: %s" % (bundlename, qual(bundle), list_to_string(result)))
        character.location.msg_contents("%s collects %s." % (character.name, bundlename), exclude=character)

        if (1-random()*10)+self.drop_rate > 0:
            # TODO: random loot get
            character.msg("You get %s!" % rainbow("BONUS THING"))

        # Subtract wall life
        self.lifespan[direction] -= tool.strength
        if self.lifespan[direction] <= 0:
            # Success at mining!
            character.msg("You break through the wall %s!" % direction)
            revdir = EXITS_REV[direction]

            # Assign new coordinates
            target_x = self.x + 1 if direction == 'east' else self.x - 1 if direction == 'west' else self.x
            target_y = self.y + 1 if direction == 'north' else self.y - 1 if direction == 'south' else self.y
            target_z = self.z + 1 if direction == 'up' else self.z - 1 if direction == 'down' else self.z
            target_level = choice([self.mining_level, self.mining_level, self.mining_level, self.mining_level, self.mining_level+1])

            exists = self.get_room_at(target_x, target_y, target_z)
            if exists:
                create_exit(revdir, "#" + str(exists.id), "#" + str(character.location.id),
                            exit_aliases=EXIT_ALIAS[revdir])
                create_exit(direction, "#" + str(character.location.id), "#" + str(exists.id),
                            exit_aliases=EXIT_ALIAS[direction])
                log_info("Connected to existing mining room %s" % exists.id)
                character.msg("You break through the %s wall to an existing part of the mine!" % direction)
                character.location.msg_contents("%s breaks through the wall to the %s!" % (character.name, direction),
                                                exclude=character)
            else:
                target_depth = self.depth + 1
                target_droprate = self.depth * 0.1
                newroom = create_object("typeclasses.mining.MiningRoom", key="Part of the mine",
                                        nohome=True, location=None,
                                        attributes=[('depth', target_depth),
                                                    ('mining_level', target_level),
                                                    ('drop_rate', target_droprate)],
                                        tags=[('the drastical mines', 'area'),
                                             ('the drastical mines', 'room')])

                newroom.x = target_x
                newroom.y = target_y
                newroom.z = target_z
                newroom.update_description()

                log_info("New MiningRoom created: %s %s (%s, %s, %s)" % (newroom.id, newroom, target_x,
                                                                        target_y, target_z))

                revdir = EXITS_REV[direction]
                create_exit(revdir, "#" + str(newroom.id), "#" + str(character.location.id),
                            exit_aliases=EXIT_ALIAS[revdir])
                create_exit(direction, "#" + str(character.location.id), "#" + str(newroom.id),
                            exit_aliases=EXIT_ALIAS[direction])

            if 'times_mined' in character.db.stats.keys():
                character.db.stats['times_mined'] += 1
            else:
                character.db.stats['times_mined'] = 1

        tool.lifespan -= 1


class MiningTool(Item):
    max_lifepan = AttributeProperty(default=50, autocreate=True)
    lifespan = AttributeProperty(default=50, autocreate=True)
    strength = AttributeProperty(default=1, autocreate=True)
    speed = AttributeProperty(default=1, autocreate=True)
    mining_level = AttributeProperty(default=1, autocreate=True)
    broken = AttributeProperty(default=False, autocreate=True)

    def at_object_creation(self):
        self.cmdset.add(MiningCmdSet, persistent=True)


class CmdMine(COMMAND_DEFAULT_CLASS):
    """
    mine <direction>> with <object>>
    Use a mining tool on a minable room.

    If the tool is of higher quality than the room, then a new exit can be mined.
    Mining isn't easy! The walls are of varying thicknesses. Better tools can make
    the job easier.
    Different rooms have different drop rates for gems, as well.

    """

    key = "mine"
    arg_regex = r"\s|$"
    rhs_split = ("with", "using")

    def func(self):
        caller = self.caller
        location = caller.location
        if not self.args:
            caller.msg("Mine which direction with what tool?")
            return False
        else:
            if "minable" not in location.tags.get(category="room"):
                caller.msg("This room is not minable.")
                return False
            if self.rhs is None:
                caller.msg("With which tool did you want to mine?")
                return False
            direction = self.lhs if self.lhs in ["north", "south", "east", "west", "down", "up"] else False
            if direction is False:
                caller.msg("You can't dig in that direction!")
                return False
            if direction in [str(i) for i in location.contents]:
                caller.msg("There is already an exit %s." % direction)
                return False
            if (location.depth <= 1 or location.z == 0) and direction == "up":
                caller.msg("You cannot mine in that direction!")
                return False
            tool = caller.search(self.rhs)
            if tool is None:
                caller.msg("With which tool did you want to mine?")
                return False
            elif not tool.db:
                tool = tool.first()
            if 'MiningTool' not in tool.db_typeclass_path:
                caller.msg("That is not a mining tool!")
                return False
            if tool.mining_level < location.mining_level:
                caller.msg("Your %s is not of high enough level to mine this room!" % tool.name)
                return False
            if tool.lifespan <= 0:
                caller.msg("The %s is worn out and needs of repair." % tool.name)
                return False
            if direction == "up" and location.z >= 0:
                caller.msg("You are already at ground level!")
                return False
            if caller.db.is_busy and caller.db.busy_doing:
                doing = caller.db.busy_doing
                caller.msg("You are too busy %s! See if you can |y|lcstop %s|ltstop %s|le|n." % (doing, doing, doing))
                return False
            if caller.db.is_busy:
                caller.msg("You are too busy!")
                return False

            caller.msg("You begin digging %s." % direction)
            caller.location.msg_contents("%s begins digging %s." % (caller.name, direction), exclude=caller)
            caller.db.is_busy = True
            caller.db.busy_doing = 'mining'
            busy_handler = utils.delay(randint(15 - tool.speed, 20 - tool.speed),
                                       location.mining_callback, caller, tool, direction)
            caller.db.busy_handler = busy_handler.task_id


class CmdStopMining(COMMAND_DEFAULT_CLASS):
    """
    stop mining - Stop any mining you presently are doing.

    """

    key = "stop mining"

    def func(self):
        caller = self.caller
        if caller.db.is_busy and caller.db.busy_handler and caller.db.busy_doing == 'mining':
            from evennia.scripts.taskhandler import TaskHandler
            th = TaskHandler()
            task = th.get_deferred(caller.db.busy_handler)
            if task is not None:
                task.cancel()
            caller.db.is_busy = False
            caller.db.busy_doing = None
            caller.msg("You stop mining.")
        else:
            caller.msg("But you are not mining!")


class MiningCmdSet(CmdSet):
    """
    CmdSet for mining tools

    """
    key = "MiningCmdSet"

    def at_cmdset_creation(self):
        self.duplicates = False
        self.add(CmdMine, allow_duplicates=False)
        self.add(CmdStopMining, allow_duplicates=False)
