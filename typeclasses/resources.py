from typeclasses.objects import Object
from random import randint
from world.resource_types import *

def spawnJunk(caller=None):
    from evennia.utils.search import search_tag
    from evennia.utils.create import create_object
    results = search_tag("random_spawn", category='room')
    ob = None
    for n in range(0 , int(results.count() * (TRASH_SPAWN_PERCENT/100))):
        loc = choice(results)
        ob = create_object(key='trash', typeclass="typeclasses.resources.Resource", home=loc, location=loc, attributes=[('ephemeral', True)])
    for n in range(0, int(results.count() * (GEM_SPAWN_PERCENT / 100))):
        loc = choice(results)
        ob = create_object(key='a gem', typeclass="typeclasses.resources.Resource", home=loc, location=loc, attributes=[('resources',{'gem': 1})])


class Resource(Object):
    def at_object_creation(self):

        if not self.db.resources:
            self.db.resources = {'trash':1}
            self.db.qual = randint(0, 5)
        elif 'gem' in self.db.resources.keys():
            self.key = "a %s gem" % gem()
            self.db.qual = randint(40, 100)
        if not self.db.qual:
            self.db.qual = randint(0,100)

        super().at_object_creation()

    def at_init(self):
        if 'trash' in self.db.resources.keys():
            self.key = trash()
            self.aliases.add('trash')

