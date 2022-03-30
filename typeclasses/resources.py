from django.conf import settings
from evennia import utils
log_err = utils.logger.log_err
from typeclasses.objects import Item
from world.resource_types import *

from evennia.commands.cmdset import CmdSet
COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class Resource(Item):
    def at_object_creation(self):
        super().at_object_creation()
        keys = self.db.resources.keys()
        if len(keys) == 1 and 'trash' in keys:
            self.key = trash()
        self.cmdset.add_default(ResourceCmdSet, persistent=True)

    def at_desc(self, looker=None, **kwargs):
        resources = " ".join(["|C%s|n: %s" % (k, v) for (k, v) in self.db.resources.items()])
        looker.msg("It deconstructs to: %s" % resources)
        super().at_desc(looker, **kwargs)


    def join(self, obj):
        if obj is None:
            return False
        if "Resource" not in obj.db_typeclass_path:
            return False
        if not obj.db.resources:
            return False

        for k in obj.db.resources.keys():
            # Both items are similar
            if (self.db.resources.keys() == obj.db.resources.keys()):
                if len(self.db.resources.keys()) == 1:
                    if k == 'trash':
                        self.key = "pile of trash"
                        self.aliases.add(['trash', 'pile'])
                    if k == 'wood':
                        self.key = "bundle of wood"
                        self.aliases.add(['bundle','wood'])
                    if k == 'stone':
                        self.key = "pile of stone"
                        self.aliases.adD(['stone','pile'])
                else:
                    self.key = "bundle of resources"
                    self.aliases.add(['bundle'])
            else:
                self.key = "bundle of resources"
                self.aliases.add(['bundle'])

            # Combine values
            if k in self.db.resources.keys():
                self.db.resources[k] += obj.db.resources[k]
            else:
                self.db.resources[k] = obj.db.resources[k]

        obj.db.resources = {}
        obj.delete()
        return

class CmdResourceJoin(COMMAND_DEFAULT_CLASS):

    key = "join"
    #locks = "cmd:superuser()"
    arg_regex = r"\s|$"
    rhs_split = ("with", " and ")  # Prefer = delimiter, but allow " to " usage.

    def func(self):
        if not self.args:
            self.caller.msg("Join what with what?")
            return
        else:
            caller = self.caller
            obj1 = caller.search(self.lhs)
            obj2 = caller.search(self.rhs)
            if obj1 == obj2:
                return
            result = obj1.join( obj2 )
            if result is False:
                self.caller.msg("You can't do that!")
            else:
                self.caller.msg("You create %s." % (obj1.name))
                self.caller.location.msg_contents("%s combines %s with %s." % (self.caller.name, obj1.name, obj2.name))

class ResourceCmdSet(CmdSet):
    key = "ResourceCmdSet"

    def at_cmdset_creation(self):
        self.duplicates = False
        self.add(CmdResourceJoin,allow_duplicates=False)
