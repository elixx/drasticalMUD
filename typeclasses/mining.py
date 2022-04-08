from django.conf import settings
from evennia import utils
from evennia.typeclasses.attributes import AttributeProperty
from evennia.commands.cmdset import CmdSet
from typeclasses.rooms import Room
from typeclasses.objects import Item
from random import randint
from evennia.utils.logger import log_err
from world.resource_types import SIZES, GEM

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class MiningRoom(Room):
    # quality is used as level for tool check
    quality              = AttributeProperty(default=1, autocreate=True)
    # how often stuff will drop when mining a wall
    drop_rate            = AttributeProperty(default=1, autocreate=True)
    # how long is left on given wall
    lifespan             = AttributeProperty(default={"north": 10,
                                                      "south": 10,
                                                      "west": 10,
                                                      "east": 10,
                                                      "down": 40}, autocreate=True)
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

    def at_object_creation(self):
        self.tags.add("minable", "room")
        self.x = 0
        self.y = 0
        self.z = 0

    def mining_callback(self, character, tool, direction):
        character.msg("You chip away to the %s with %s." % (direction, tool.name))


class MiningTool(Item):
    max_lifepan = AttributeProperty(default=10, autocreate=True)
    lifespan =    AttributeProperty(default=10, autocreate=True)
    strength =    AttributeProperty(default=1, autocreate=True)
    speed =       AttributeProperty(default=1, autocreate=True)
    quality =     AttributeProperty(default=10, autocreate=True)
    broken =      AttributeProperty(default=False, autocreate=True)

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
    rhs_split = ("with","using")

    def func(self):
        caller = self.caller
        location = caller.location
        log_err("%s %s" % (self.lhs, self.rhs))
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
            direction = self.lhs if self.lhs in ["north","south","east","west","down","up"] else False
            if direction is False:
                caller.msg("You can't dig in that direction!")
                return False
            if direction in [str(i) for i in location.contents]:
                caller.msg("There is already an exit to the %s." % direction)
                return False
            tool = caller.search(self.rhs, quiet=True)
            tool = tool[0]
            if tool is None:
                caller.msg("With which tool did you want to mine?")
                return False
            if 'MiningTool' not in tool.db_typeclass_path:
                caller.msg("That is not a mining tool!")
                return False
            if tool.quality < location.quality:
                caller.msg("Your %s is not of high enough quality to mine this room!" % tool.name)
                return False
            if direction == "up" and location.z >= 0:
                caller.msg("You are already at ground level!")
                return False

            caller.msg("You begin digging to the %s." % direction)
            utils.delay(randint(0+tool.speed,11-tool.speed), location.mining_callback, caller, tool, direction)


class MiningCmdSet(CmdSet):
    """
    CmdSet for mining tools

    """
    key = "MiningCmdSet"

    def at_cmdset_creation(self):
        self.duplicates = False
        self.add(CmdMine, allow_duplicates=False)
