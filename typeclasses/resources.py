from django.conf import settings

from evennia import utils

log_err = utils.logger.log_err
from typeclasses.objects import Item
from evennia.utils import list_to_string
from world.resource_types import *
from world.utils import qual

from evennia.commands.cmdset import CmdSet

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class Resource(Item):
    @property
    def gold(self):
        return self.db.resources['gold'] if 'gold' in self.db.resources.keys() else 0

    @gold.setter
    def gold(self, value):
        if self.db.resources:
            self.db.resources['gold'] = value
        else:
            self.db.resources = {'gold': value}

    def at_object_creation(self):
        if not self.db.resources:
            self.db.resources = {}
        for (k, v) in self.db.resources.items():
            if int(v) == 0 or v is None:
                del self.db.resources[k]
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
            self.db.quality = (self.db.quality + obj.db.quality) / 2
            # Combine values
            if k in self.db.resources.keys():
                self.db.resources[k] += obj.db.resources[k]
            else:
                self.db.resources[k] = obj.db.resources[k]

        agg = sum(self.db.resources.values())
        self.key = "%s resource bundle" % SIZES(agg)
        self.aliases.add(['bundle'])

        obj.db.resources = {}
        obj.delete()
        return


class CmdResourceJoin(COMMAND_DEFAULT_CLASS):
    """
    Usage: join/combine <item1> with <item2>
           join all bundles
    Combine two different items to create a resource bundle.
    Both objects will be consumed. The bundle will contain all of both items' resources.
    The bundle will have an average quality of the two items.
    "join all bundles" will combine all Resource bundles into one.

    """
    key = "join"
    aliases = ["combine"]
    # locks = "cmd:superuser()"
    #arg_regex = r"\s|$"
    #rhs_split = ("with", "and")  # Prefer 'with' delimiter, but allow " and " usage.

    def func(self):
        log_err(self.args)
        if not self.args:
            self.caller.msg("Join what with what?")
            return
        elif "all bundles" in self.args:
            bundles = [o for o in self.caller.contents if "Resource" in o.db_typeclass_path]
            b = bundles.pop()
            for bundle in bundles:
                b.join(bundle)
            result = ["|w%s |Y%s|n" % (v, k) for k, v in b.db.resources.items() if v != 0]
            self.caller.msg(f'Joined all resources in inventory to create {b.key} of {qual(b)} quality containing {list_to_string(result)}.')
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
            if "join" not in dir(obj1):
                if "join" not in dir(obj2):
                    self.caller.msg("You can't use %s or %s to make a resource bundle." % (obj1.name, obj2.name))
                    return
                else:
                    join = obj2.join
                    target = obj1
            else:
                join = obj1.join
                target = obj2
            #            result = obj1.join(obj2)
            result = join(target)
            if result is False:
                self.caller.msg("You can't do that!")
            else:
                # result = ["|Y%s|n: |w%s|n"% (k.title(),v) for k,v in obj1.db.resources.items() ]
                result = ["|w%s |Y%s|n" % (v, k) for k, v in obj1.db.resources.items() if v != 0]

                self.caller.msg("You create %s %s out of %s and %s, containing %s." % (
                    qual(obj1), obj1.name, oldname, oldname2, list_to_string(result)))
                self.caller.location.msg_contents("%s combines %s with %s." % (self.caller.name, oldname, obj2.name),
                                                  exclude=self.caller)


class ResourceCmdSet(CmdSet):
    key = "ResourceCmdSet"

    def at_cmdset_creation(self):
        self.duplicates = False
        self.add(CmdResourceJoin, allow_duplicates=False)
