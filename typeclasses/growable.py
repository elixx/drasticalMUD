
from evennia import DefaultObject


class GrowableObject(DefaultObject):
    def at_object_creation(self):
        self.db.age = 0
        self.tag.add("growable")
        super().at_object_creation()
        if not self.db.growth_phases:
            self.db.growth_phases = {     0: ("a seedling", "You recognize the mound of dirt to be a recently-buried seedling."),
                                         30: ("a tiny sprout", "A barely visible barely emerges from under the ground."),
                                        100: ("a small shoot", "A light greenish shoot protrudes from the soil here."),
                                        200: ("a young sapling", "Flexible young branches spread from a still-flimsy trunk."),
                                        500: ("a firmly-rooted tree", "A healthy tree grows here."),
                                        750: ("a giant old tree" , "Giant branches loom over you, this tree is of formidable size.")}

    def check_growth(self):
        if self.db.age in self.db.growth_phases.keys():
            self.key = self.db.growth_phases[self.db.age][0]
            self.db.desc = self.db.growth_phases[self.db.age][1]
