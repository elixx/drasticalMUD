from django.conf import settings
from evennia import utils
log_err = utils.logger.log_err
from typeclasses.objects import Item
from world.resource_types import *

from evennia.commands.cmdset import CmdSet
COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class Resource(Item):
    def at_object_creation(self):
        if not self.db.resources:
            self.db.resources = {}
        keys = self.db.resources.keys()
        if len(keys) == 1 and 'trash' in keys:
            self.key = trash()
        self.cmdset.add(ResourceCmdSet, persistent=True)
        super().at_object_creation()

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
            self.key = "resource bundle"
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
    """
    Usage: join <item1> with <item2>
    Combine two different items to create a resource bundle.
    Both objects will be consumed. The bundle will contain all of both items' resources.
    The bundle will have the quality of item1.

    """
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
                self.caller.msg("You can't join that with itself!")
                return
            elif obj1 is None or obj2 is None:
                self.caller.msg("Can't find that!")
                return
            oldname = obj1.name
            oldname2 = obj2.name
            result = obj1.join( obj2 )
            if result is False:
                self.caller.msg("You can't do that!")
            else:
                self.caller.msg("You create %s out of %s and %s." % (obj1.name, oldname, oldname2))
                self.caller.location.msg_contents("%s combines %s with %s." % (self.caller.name, oldname, obj2.name))

class ResourceCmdSet(CmdSet):
    key = "ResourceCmdSet"

    def at_cmdset_creation(self):
        self.duplicates = False
        self.add(CmdResourceJoin,allow_duplicates=False)
