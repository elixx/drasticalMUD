from django.conf import settings
from evennia import utils
from evennia.typeclasses.attributes import AttributeProperty
from evennia.commands.cmdset import CmdSet
from typeclasses.rooms import Room
from typeclasses.objects import Item
from random import randint, choice
from evennia.utils.create import create_object
from evennia.utils.logger import log_err
from evennia.utils import list_to_string
from world.utils import qual
from core import EXITS_REV, EXIT_ALIAS
from world.resource_types import SIZES, GEM
from core.utils import create_exit

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class MiningRoom(Room):
    # quality is used as level for tool check
    quality = AttributeProperty(default=1, autocreate=True)
    # how often stuff will drop when mining a wall
    drop_rate = AttributeProperty(default=1, autocreate=True)
    # how long is left on given wall
    lifespan = AttributeProperty(default={"north": 10,
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
        resources = {'trash': randint(0,10),
                     'wood': choice(['0', '0', '0', randint(0, 10)]),
                     'stone': randint(10+self.quality/2, 10+self.quality)}

        bundle = create_object(key='resource bundle', typeclass="typeclasses.resources.Resource", home=character, location=character,
                      attributes=[('resources', resources)])
        result = ["|Y%s|n: |w%s|n" % (k.title(), v) for k, v in bundle.db.resources.items()]
        self.caller.msg("You get a bundle containing: %s - %s" % (qual(bundle), list_to_string(result)))


        # Assign new coordinates
        target_x = self.x+1 if direction == 'east' else self.x-1 if direction == 'west' else self.x
        target_y = self.y+1 if direction == 'north' else self.y-1 if direction == 'south' else self.y
        target_z = self.z+1 if direction == 'up' else self.z-1 if direction == 'down' else self.z

        ## TODO: Search for existing coordinate overlap

        # Subtract wall life
        self.db.lifespan[direction] -= tool.strength
        if self.lifespan[direction] <= 0:
            character.msg("You break through the wall %s!" % direction)
            # Success at mining!
            newroom = create_object("typeclasses.mining.MiningRoom", key="part of a mine",
                                    nohome=True, location=None,
                                 attributes=[('desc', 'A good place for mining.'),
                                             ('x', target_x),
                                             ('y', target_y),
                                             ('z', target_z)],
                                    tags=[(target_x, 'mining_x'),
                                          (target_y, 'mining_y'),
                                          (target_z, 'mining_z')])
            newroom.db.lifespan = newroom.lifespan
            log_err("New MiningRoom created: %s %s" % (newroom.id, newroom))
            revdir = EXITS_REV[direction]
            create_exit(revdir, "#"+str(newroom.id), "#"+str(character.location.id), exit_aliases=EXIT_ALIAS[revdir])
            create_exit(direction, "#"+str(character.location.id), "#"+str(newroom.id), exit_aliases=EXIT_ALIAS[direction])

            if 'times_mined' in character.db.stats.keys():
                character.db.stats['times_mined'] += 1
            else:
                character.db.stats['times_mined'] = 1




class MiningTool(Item):
    max_lifepan = AttributeProperty(default=10, autocreate=True)
    lifespan = AttributeProperty(default=10, autocreate=True)
    strength = AttributeProperty(default=1, autocreate=True)
    speed = AttributeProperty(default=1, autocreate=True)
    quality = AttributeProperty(default=10, autocreate=True)
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
            if caller.db.is_busy and caller.db.busy_doing:
                doing = caller.db.busy_doing
                caller.msg("You are too busy %s! See if you can |ystop %s|n." % (doing, doing))
                return False
            if caller.db.is_busy:
                caller.msg("You are too busy!")
                return False

            caller.msg("You begin digging %s." % direction)
            caller.db.is_busy = True
            caller.db.busy_doing = 'mining'
            busy_handler = utils.delay(randint(6 - tool.speed, 16 - tool.speed),
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
