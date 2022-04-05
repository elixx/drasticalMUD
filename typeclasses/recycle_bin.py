from evennia import utils
from django.conf import settings
from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from world.resource_types import BASE_VALUE
import re

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)
_RE_ARGSPLIT = re.compile(r"\s(with|on|to|in|at)\s", re.I + re.U)


class RecycleBin(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false()")
        self.db.auto_purge = False
        self.db.destructive = False
        if not self.db.stats:
            self.db.stats = {}
        self.cmdset.add_default(RecycleBinCmdSet, persistent=True)

    def at_init(self):
        super().at_init()
        if self.db.auto_purge:
            self.purge_contents()

    def purge_contents(self):
        for ob in self.contents:
            self.location.msg_contents("%s makes a granding noise as %s is eliminated." % (self.name, ob.name))
            if 'recycled' not in self.db.stats.keys():
                self.db.stats['recycled'] = 1
            else:
                self.db.stats['recycled'] += 1
            if self.db.destructive:
                ob.delete()
            else:
                ob.location = None
                ob.db.ephemeral = True


class CmdRecycleBinPut(COMMAND_DEFAULT_CLASS):
    key = "put"
    locks = "cmd:all()"
    arg_regex = r"(/\w+?(\s|$))|\s|$"

    def parse(self):
        caller = self.caller
        self.args = self.args.strip()

        # splits to either ['obj'] or e.g. ['obj', 'on', 'obj']
        parts = [part.strip() for part in _RE_ARGSPLIT.split(" " + self.args, 1)]
        nparts = len(parts)
        self.obj1 = None
        self.arg1 = None
        self.prep = None
        self.obj2 = None
        self.arg2 = None
        if nparts == 1:
            self.obj1 = self.caller.search(parts[0])
        elif nparts == 3:
            obj1, self.prep, obj2 = parts
            self.obj1 = self.caller.search(obj1)
            self.obj2 = self.caller.search(obj2)

    def func(self):
        if (self.obj2 != self.obj) and self.obj1:
            self.caller.msg("You think about putting %s in %s." % (self.obj1.name, self.obj.name))
        elif self.obj1:

            factor = 1
            if self.obj1.db.quality:
                if self.obj1.db.quality > 0:
                    factor = 1 - int(self.obj1.db.quality) / 100  # quality bonus

            val = 0
            if self.obj1.db.resources:
                for k in self.obj1.db.resources.keys():
                    if k in BASE_VALUE.keys():
                        val += BASE_VALUE[k] * self.obj1.db.resources[k]

            val += (val * factor)  # quality bonus

            val = round(val,2)

            ui = yield ("Are you sure you want to recycle %s for |Y%s gold|x? Type {Cyes{n if sure." % (self.obj1.name, val))
            if ui.strip().lower() in ['yes', 'y']:
                self.caller.msg("You put %s into %s." % (self.obj1.name, self.obj.name))
                self.caller.location.msg_contents("%s whirrs to life and devours %s." % (self.obj.name, self.obj1.name))

                if 'gold' in self.caller.db.stats.keys():
                    self.caller.db.stats['gold'] += val
                else:
                    self.caller.db.stats['gold'] = val

                self.caller.msg("{nYou receive {y%s gold{n for cleaning up." % val)
                self.obj1.location = self.obj


class CmdRecycleBinEmpty(COMMAND_DEFAULT_CLASS):
    key = "empty"
    locks = "cmd:superuser()"

    def func(self):
        self.caller.msg("You activate the compactor on %s." % self.obj.name)
        self.caller.location.msg_contents("%s activates %s." % (self.caller.name, self.obj.name), exclude=self.caller)
        self.obj.purge_contents()


class RecycleBinCmdSet(CmdSet):
    key = "RecycleBinCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdRecycleBinPut)
        self.add(CmdRecycleBinEmpty)
