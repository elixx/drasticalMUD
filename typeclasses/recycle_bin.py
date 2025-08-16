import re

from django.conf import settings

from evennia import DefaultObject
from evennia import utils
from evennia.commands.cmdset import CmdSet
from world.resource_types import BASE_VALUE

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
        self.all_mode = False
        # detect 'all' usage
        if parts[0].lower() == 'all':
            self.all_mode = True
        else:
            self.obj1 = self.caller.search(parts[0])
        if nparts == 3:
            obj1, self.prep, obj2 = parts
            if obj1.lower() == 'all':
                self.all_mode = True
            else:
                self.obj1 = self.caller.search(obj1)
            self.obj2 = self.caller.search(obj2)

    def func(self):
        # handle 'all' recycling mode
        if getattr(self, 'all_mode', False):
            # if explicitly targeting another container, show think message
            if self.obj2 and (self.obj2 != self.obj):
                self.caller.msg("You think about putting all in %s." % (self.obj.name))
                return
            # collect all inventory items tagged 'random_spawn'
            items = [ob for ob in self.caller.contents if getattr(ob, 'tags', None) and ob.tags.get('random_spawn', category='object')]
            self.caller.msg("You clear %s trash from your inventory." % len(items))
            if not items:
                self.caller.msg("You have nothing suitable to recycle.")
                return
            # compute total value
            total_val = 0
            for it in items:
                factor = 1
                if getattr(it.db, 'quality', None):
                    if it.db.quality > 0:
                        factor = 1 - int(it.db.quality) / 100  # quality bonus
                val = 0
                if getattr(it.db, 'resources', None):
                    for k in it.db.resources.keys():
                        if k in BASE_VALUE.keys():
                            val += BASE_VALUE[k] * it.db.resources[k]
                if getattr(it.db, 'value', None):
                    for k in it.db.value.keys():
                        if k == 'gold':
                            val += it.db.value['gold'] / 8
                val += (val * factor)  # quality bonus
                total_val += val
            total_val = round(total_val, 2)
            ui = yield ("Recycle all random loot (%s item%s) for |Y%s gold|x? Type {Cyes{x if sure." % (len(items), '' if len(items)==1 else 's', total_val))
            if ui.strip().lower() in ['yes', 'y']:
                # add gold once
                if not getattr(self.caller, 'db', None):
                    self.caller.db = {}
                if not getattr(self.caller.db, 'stats', None):
                    self.caller.db.stats = {}
                if 'gold' in self.caller.db.stats.keys():
                    self.caller.db.stats['gold'] += total_val
                else:
                    self.caller.db.stats['gold'] = total_val
                # Invalidate gold-based leaderboards and toplist context
                try:
                    from world.stats import invalidate_topGold_cache
                    invalidate_topGold_cache()
                except Exception:
                    pass
                # move items into the bin and message
                for it in items:
                    self.caller.msg("You put %s into %s." % (it.name, self.obj.name))
                    if self.caller.location:
                        self.caller.location.msg_contents("%s whirrs to life and devours %s." % (self.obj.name, it.name))
                    it.location = self.obj
                self.caller.msg("{nYou receive {y%s gold{n for cleaning up." % total_val)
            return
        # default single-object behavior
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

            if self.obj1.db.value:
                for k in self.obj1.db.value.keys():
                    if k == 'gold':
                        val += self.obj1.db.value['gold'] / 8

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

                # Invalidate gold-based leaderboards and toplist context
                try:
                    from world.stats import invalidate_topGold_cache
                    invalidate_topGold_cache()
                except Exception:
                    pass

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
