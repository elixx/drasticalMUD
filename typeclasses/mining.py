from django.conf import settings
from evennia import utils
from evennia.typeclasses.attributes import AttributeProperty
from evennia.commands.cmdset import CmdSet
from typeclasses.rooms import Room
from typeclasses.objects import Item
from random import randint
from world.resource_types import SIZES, GEM

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class MiningRoom(Room):
    # level in depth, ground level is 0
    depth                = AttributeProperty(default=0, autocreate=True)
    # quality is used as level for tool check
    quality              = AttributeProperty(default=1, autocreate=True)
    # how often stuff will drop when mining a wall
    drop_rate            = AttributeProperty(default=10, autocreate=True)
    # how long is left on given wall
    lifespan             = AttributeProperty(default={"north": 10,
                                                      "south": 10,
                                                      "west": 10,
                                                      "east": 10,
                                                      "down": 40}, autocreate=True)
    def at_object_creation(self):
        self.tags.add("minable", "room")

    def mining_callback(self, character, tool):
        pass


class MiningTool(Item):
    max_lifepan = AttributeProperty(default=10, autocreate=True)
    lifespan =    AttributeProperty(default=10, autocreate=True)
    strength =    AttributeProperty(default=1, autocreate=True)
    speed =       AttributeProperty(default=1, autocreate=True)
    quality =     AttributeProperty(default=10, autocreate=True)
    broken =      AttributeProperty(default=False, autocreate=True)

    def at_object_creation(self):
        self.cmdset.add()


class MiningCmdSet(CmdSet):
    """
    CmdSet for mining tools

    """
    key = "MiningCmdSet"
    duplicates = False

    def at_cmdset_creation(self):
        self.add(CmdMine())
        super().at_cmdset_creation()

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
    aliases = ["dig"]
    arg_regex = r"\s|$"
    rhs_split = ("with")

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
            direction = self.lhs if self.lhs in ["north","south","east","west","down"] else False
            if direction is False:
                caller.msg("You can't dig in that direction!")
                return False
            if direction in [str(i) for i in location.contents]:
                caller.msg("There is already an exit to the %s." % direction)
                return False
            tool = caller.search(self.rhs)
            if tool is None:
                caller.msg("Which tool did you want to mine with?")
                return False
            if 'MiningTool' not in tool.db_typeclass_path:
                caller.msg("That is not a mining tool!")
                return False
            if tool.quality < location.quality:
                caller.msg("Your %s is not of high enough quality for this room!" % tool.name)
                return False

            # When all checks passed then we can mine.
            gem = GEM(location.drop.rate/100 * tool.strength)





