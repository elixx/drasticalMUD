from django.conf import settings
from evennia import utils
from typeclasses.objects import Item
from evennia.commands.cmdset import CmdSet
from evennia.utils.utils import list_to_string
from world.resource_types import SIZES, BASE_VALUE


COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class GrowableObject(Item):
    def at_object_creation(self):
        self.cmdset.add_default(GrowableCmdSet, persistent=True)
        self.db.age = -1
        self.db.planted = False
        self.tags.add("growable", category='object')
        self.tags.add("trash", category="growth")
        self.db.resources={'trash': 1, 'wood': 1}

        if not self.db.growth_phases:
            self.db.growth_phases = {
                0: ("mold spore", "A greenish tinge is barely visible."),
                30: ("small spot", "A greenish blip grows lightly over the surface."),
                50: ("mold spot", "A green-brown growth begins to creep over the surface."),
                80: ("mushroom", "A section of the surface is covered in mushrooms."),
                100: ("small mushroom patch", "A small gathering of mushrooms has started here."),
                150: ("mushroom patch", "A gathering of mushrooms has made its home here."),
                250: ("large mushroom patch", "Mushrooms have begun to spread all over."),
                9000: ("large mold blob", "A large, green and white mass. It makes you feel uncomfortable."),
                10000: ("giant mold growth", "This thing is huge! You worry a bit about your health.")}
        super().at_object_creation()

    def grow(self):
        self.db.age += 1
        if self.db.age in self.db.growth_phases.keys() and self.db.planted == True:
            self.location.msg_contents("%s transforms into %s." % (self.name, self.db.growth_phases[self.db.age][0]))
            self.key = self.db.growth_phases[self.db.age][0]
            self.db.desc = self.db.growth_phases[self.db.age][1]
            growths = self.tags.get(category="growth")
            levels = self.db.growth_phases.keys()
            factor = self.db.growth_factor if self.db.growth_factor else 1
            for level in levels:
                if self.db.age > level:
                    factor += 0.06                  # bonus production per growth level
            if isinstance(growths, str): growths = [growths]
            growth_factor = self.db.growth_factor if self.db.growth_factor else 1
            for growth in growths:
                if growth not in self.db.resources.keys():
                    self.db.resources[growth] = 1 * growth_factor
                else:
                    self.db.resources[growth] += 1 * growth_factor


    def at_access(self, result, accessing_obj, access_type):
        if access_type == "get" and result == False:
            if self.db.planted:
                accessing_obj.msg("It is planted firmly in the ground.")


class CmdPlant(COMMAND_DEFAULT_CLASS):
    """
    Plant a growable object

    """

    key = "plant"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("You plant yourself right where you are.")
            self.caller.location.msg_contents("%s plants themselves firmly on the ground." % self.caller,
                                              exclude=self.caller)
        else:
            target = self.args.strip()
            obj = self.caller.search(target)
            if not obj:
                self.caller.msg("You can't find it!")
            else:
                if "growable" in obj.db_typeclass_path:
                    if self.caller.id == self.caller.location.db.owner:
                        if obj.db.planted == False:
                            for growing in self.caller.location.contents:
                                if "growable" in growing.db_typeclass_path and growing.db.planted:
                                    self.caller.msg("There is already something growing here!")
                                    return
                            self.caller.msg("You plant %s in %s." % (obj.name, self.caller.location.name))
                            self.caller.location.msg_contents("%s plants %s." % (self.caller.name, obj.name),
                                                              exclude=self.caller)
                            obj.home = self.caller.location
                            obj.location = self.caller.location
                            obj.db.planted = True
                            obj.locks.add("get:false()")
                            obj.grow()
                    else:
                        self.caller.msg("You must own a room in order to plant things in it.")
                        return
                else:
                    self.caller.msg("You cannot plant anything here.")
                    return


class CmdHarvest(COMMAND_DEFAULT_CLASS):
    """
    Collect resources from a growable object

    """

    key = "harvest"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Harvest what?")
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
                            factor = 1
                            if obj.db.quality:
                                factor += (1-obj.db.quality/100)    # quality to percent
                            amounts = {}
                            amount_strs = []
                            for r, v in obj.db.resources.items():
                                amounts[r] = int( v * ((1+factor) + (obj.db.age/12)) )
                            for r, v in amounts.items():
                                amount_strs.append("%s %s" % (v , r))
                            if not self.db.harvest_spawn:
                                self.caller.msg("%s will be consumed." % obj.name)
                            ui = yield ("You will receive |y%s|n from harvesting %s. Continue? (Yes/No)" % (
                                list_to_string(amount_strs), obj.name))
                            if ui.strip().lower() in ['yes', 'y']:
                                from evennia.utils.create import create_object
                                agg = sum(amounts.values())
                                harvest_name = "%s resource bundle" % SIZES(agg)
                                bundle = create_object(key=harvest_name, typeclass="typeclasses.resources.Resource",
                                                       home=self.caller, location=self.caller,
                                                       attributes=[('resources', amounts)])
                                if not self.db.harvest_spawn:
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
        self.add(CmdPlant())
        self.add(CmdHarvest())
        super().at_cmdset_creation()


class Tree(GrowableObject):
    def at_object_creation(self):
        super().at_object_creation()
        if not self.db.tree_type:
            from world.resource_types import tree_type
            self.db.tree_type = tree_type()
            self.tags.add("wood",category="growth")
            self.tags.remove("trash",category="growth")

        if not self.db.growth_phases:
            self.db.growth_phases = {
                0: ("a seedling", "You recognize the mound of dirt to be a recently-buried seedling."),
                30: ("a tiny sprout", "A barely visible growth emerges from under the ground."),
                90: ("a small shoot", "A light greenish shoot protrudes from the soil here."),
                150: ("a young %s sapling" % self.db.tree_type,
                      "Flexible young branches spread from a still-flimsy %s trunk." % self.db.tree_type),
                300: (
                "a firmly-rooted %s tree" % self.db.tree_type, "A healthy %s tree grows here." % self.db.tree_type),
                500: ("a giant old %s tree" % self.db.tree_type,
                      "Giant branches loom over you, this %s tree is of formidable size." % self.db.tree_type)}



class FruitTree(GrowableObject):
    def at_object_creation(self):
        if not self.db.tree_type:
            from resource_types import fruit_tree_type
            self.db.tree_type = fruit_tree_type()
        self.db.harvest_spawn = True
        self.tags.add("wood",category="growth")
        self.tags.add("fruit",category="growth")
        self.tags.remove("trash",category="growth")

        if not self.db.growth_phases:
            self.db.growth_phases = {
                0: ("a seedling", "You recognize the mound of dirt to be a recently-buried seedling."),
                30: ("a tiny sprout", "A barely visible growth emerges from under the ground."),
                90: ("a small shoot", "A light greenish shoot protrudes from the soil here."),
                150: ("a young %s sapling" % self.db.tree_type,
                      "Flexible young branches spread from a still-flimsy %s trunk." % self.db.tree_type),
                300: (
                "a firmly-rooted %s tree" % self.db.tree_type, "A healthy %s tree grows here." % self.db.tree_type),
                500: ("a giant old %s tree" % self.db.tree_type,
                      "Giant branches loom over you, this %s tree is of formidable size." % self.db.tree_type)}
        super().at_object_creation()


class Plant(GrowableObject):
    def at_object_creation(self):
        self.tags.add("wood", category="growth")
        self.tags.add("trash", category="growth")

        if not self.db.growth_phases:
            self.db.growth_phases = {
                0: ("a seedling", "You recognize the mound of dirt to be a recently-buried seedling."),
                30: ("a tiny sprout", "A barely visible barely emerges from under the ground."),
                90: ("a small shoot", "A light greenish shoot protrudes from the soil here."),
                150: ("a small weed", "A little fern stands here weakly."),
                300: ("a firmly-rooted weed", "These are starting to pop up all over the place!"),
                500: ("a giant weed",
                      "Huge, fertile stalks lean in every direction. You can barely make out where it starts or ends.")}
        super().at_object_creation()