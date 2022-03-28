from django.conf import settings
from evennia import utils
from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class GrowableObject(DefaultObject):
    def at_object_creation(self):
        self.cmdset.add_default(GrowableCmdSet, persistent=True)
        self.db.age = -1
        self.db.planted = False
        self.tags.add("growable", category='object')
        if not self.db.growth_phases:
            self.db.growth_phases = {     0: ("a seedling", "You recognize the mound of dirt to be a recently-buried seedling."),
                                         30: ("a tiny sprout", "A barely visible barely emerges from under the ground."),
                                        100: ("a small shoot", "A light greenish shoot protrudes from the soil here."),
                                        200: ("a young sapling", "Flexible young branches spread from a still-flimsy trunk."),
                                        500: ("a firmly-rooted tree", "A healthy tree grows here."),
                                        750: ("a giant old tree" , "Giant branches loom over you, this tree is of formidable size.")}
            super().at_object_creation()

    def grow(self):
        self.db.age += 1
        if self.db.age in self.db.growth_phases.keys() and self.db.planted == True:
            self.key = self.db.growth_phases[self.db.age][0]
            self.db.desc = self.db.growth_phases[self.db.age][1]

    def at_access(self, result, accessing_obj, access_type):
        if access_type == "get" and result == False:
            if self.db.planted:
                accessing_obj.msg("It is already planted firmly in the ground.")

class CmdPlant(COMMAND_DEFAULT_CLASS):
    """
    Plant a growable object

    """

    key = "plant"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("You plant yourself right where you are.")
            self.caller.location.msg_contents("%s plants themselves firmly on the ground." % self.caller, exclude=self.caller)
        else:
            target = self.args.strip()
            obj = self.caller.search(target)
            if not obj:
                self.caller.msg("You can't find it!")
            else:
                if "growable" in obj.db_typeclass_path:
                    if obj.db.planted == False:
                        obj.location = self.caller.location
                        obj.db.planted = True
                        obj.locks.add("get:false()")
                        obj.grow()


class GrowableCmdSet(CmdSet):
    """
    CmdSet for the seed

    """

    key = "GrowableCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdPlant())
        super().at_cmdset_creation()
