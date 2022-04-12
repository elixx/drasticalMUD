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
    Combine two different items to create a resource bundle.
    Both objects will be consumed. The bundle will contain all of both items' resources.
    The bundle will have an average quality of the two items.

    """
    key = "join"
    aliases = ["combine"]
    # locks = "cmd:superuser()"
    arg_regex = r"\s|$"
    rhs_split = ("with", "and")  # Prefer 'with' delimiter, but allow " and " usage.

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


class CmdResourceSplit(COMMAND_DEFAULT_CLASS):
    """
    Usage: split <amount> <resources> from <bundle>
           split <amount> gold

    Create a new resource bundle from an existing one.

    Also used to create a resource bundle containing some of your gold.

    """
    key = "split"
    # arg_regex = r".* from .*|$"
    rhs_split = (" from ")

    def func(self):
        if not self.args:
            self.caller.msg("Split what?")
            return False
        else:
            caller = self.caller
            if not self.rhs:
                self.msg("Split how many resources from what bundle?")
                return False
        if " from " not in self.args and "gold" in self.args:
            obj = caller
            resource = 'gold'
            if not self.lhs.isnumeric():
                caller.msg("Split how much?")
                return False
            amount = float(self.lhs) if '.' in self.lhs else int(self.lhs)
            if caller.gold < amount:
                caller.msg("You do not have enough gold!")
            caller.gold -= amount
        else:
            amount = int(self.lhs.strip())
            args = self.rhs.split(" from ")
            resource = args[0].strip()
            obj = caller.search(args[1].strip())
            if obj is None:
                caller.msg(f"Could not find {args[0].strip()}!")
                return False
            if resource not in obj.db.resources.keys():
                caller.msg(f"There is no {resource} in {obj.name}!")
                return False
            if obj.db.resources[resource] < amount:
                caller.msg(f"{obj.name} does not have enough {resource} to do that.")
                return False
            obj.db.resources[resource] -= amount

        bundlename = f"{SIZES(amount)} bundle of {resource}"
        resources = {resource: amount}
        from evennia.utils.create import create_object
        bundle = create_object(key=bundlename, typeclass="typeclasses.resources.Resource",
                               home=caller, location=caller,
                               attributes=[('resources', resources)])
        caller.msg(f"You take {bundle.name} out of {obj.name if obj.name != caller.name else 'your pocket.'}.")
        caller.location.msg_contents(
            f"{caller.name} removes {bundle.name} from {obj.name if obj.name != caller.name else 'their pocket'}.",
            exclude=caller)


class ResourceCmdSet(CmdSet):
    key = "ResourceCmdSet"

    def at_cmdset_creation(self):
        self.duplicates = False
        self.add(CmdResourceJoin, allow_duplicates=False)
        self.add(CmdResourceSplit, allow_duplicates=False)
