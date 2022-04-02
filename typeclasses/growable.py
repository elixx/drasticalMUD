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
                                         90: ("a small shoot", "A light greenish shoot protrudes from the soil here."),
                                        150: ("a young sapling", "Flexible young branches spread from a still-flimsy trunk."),
                                        300: ("a firmly-rooted tree", "A healthy tree grows here."),
                                        500: ("a giant old tree" , "Giant branches loom over you, this tree is of formidable size.")}
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
                    if self.caller.id == self.caller.location.db.owner:
                        if obj.db.planted == False:
                            self.caller.msg("You plant %s in %s." % (obj.name, self.caller.location.name))
                            self.caller.location.msg_contents("%s plants %s." % (self.caller.name, obj.name), exclude=self.caller)
                            obj.home = self.caller.location
                            obj.move_to(self.caller.location)
                            obj.db.planted = True
                            obj.locks.add("get:false()")
                            obj.grow()
                    else:
                        self.caller.msg("You must own a room in order to plant things in it.")
                else:
                    self.caller.msg("You cannot plant anything here.")


class CmdHarvest(COMMAND_DEFAULT_CLASS):
    """
    Collect resources from a growable object

    """

    key = "harvest"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("You daydream about having a good harvest.")
            self.caller.location.msg_contents("%s daydreams about a good harvest." % self.caller, exclude=self.caller)
        else:
            target = self.args.strip()
            obj = self.caller.search(target)
            if not obj:
                self.caller.msg("You can't find it!")
            else:
                if "growable" in obj.db_typeclass_path:
                    if self.caller.id == self.caller.location.db.owner:
                        if obj.db.planted == True and obj.db.age > 1:
                            levels = obj.db.growth_phases.keys()
                            factor = 0.5
                            for level in levels:
                                if obj.db.age > level:
                                    factor += 0.5
                            wood = obj.db.age * factor
                            ui = yield ("You will receive |y%s wood|n from harvesting %s. Continue? (Yes/No)" % (wood, obj.name))
                            if ui.strip().lower() in ['yes', 'y']:
                                from evennia.utils.create import create_object
                                from world.resource_types import wood as wood_name
                                bundle = create_object(key=wood_name, typeclass="typeclasses.resources.Resource",
                                                       home=self.caller, location=self.caller,
                                                       attributes=[('resources', {'wood': wood})])
                                obj.delete()
                    else:
                        self.caller.msg("You must own a room in order to harvest from things in it.")


class GrowableCmdSet(CmdSet):
    """
    CmdSet for the seed

    """

    key = "GrowableCmdSet"
    duplicates = False

    def at_cmdset_creation(self):
        self.add(CmdPlant(), allow_duplicates=False)
        self.add(CmdHarvest(), allow_duplicates=False)
        super().at_cmdset_creation()
