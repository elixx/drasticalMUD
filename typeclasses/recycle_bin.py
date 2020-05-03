from evennia import utils
from django.conf import settings
from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from evennia import search_channel
from datetime import datetime
from evennia.utils import wrap
import re

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)
_RE_ARGSPLIT = re.compile(r"\s(with|on|to|in|at)\s", re.I + re.U)

class RecycleBin(DefaultObject):

    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false()")
        if not self.db.stats:
            self.db.stats = {}
        self.cmdset.add(RecycleBinCmdSet)

    def at_init(self):
        super().at_init()
        for ob in self.contents:
            if 'recycled' not in self.db.stats.keys():
                self.db.stats['recycled'] = 1
            else:
                self.db.stats['recycled'] += 1
            ob.delete()

class CmdRecycleBinRead(COMMAND_DEFAULT_CLASS):
    key = "read"
    locks = "cmd:all()"
    def func(self):
        table = self.styled_table("{Y#","{YTime","{YAuthor", "{YPost                                ")
        cnt = 0
        for (stamp, author, post) in self.obj.db.posts:
            table.add_row(cnt,stamp.strftime("%m-%d{r@{n%H:%M"),'{G'+author,wrap(post, width=50))
            cnt += 1
        output = "You read %s.\n" % self.obj.name
        output += str(table)
        self.caller.msg(output)
        self.caller.location.msg_contents("%s reads %s." % (self.caller.name, self.obj.name), exclude=self.caller)

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
            self.obj1, self.arg1 = self.caller.search(parts[0], self.obj1_search)
        elif nparts == 3:
            obj1, self.prep, obj2 = parts
            self.obj1 = self.caller.search(obj1)
            self.obj2 = self.caller.search(obj2)

    def func(self):
        if (self.obj2 != self.obj) and self.obj1:
            self.caller.msg("You think about putting %s in %s." % (self.obj1.name, self.obj.name))
        elif self.obj1:
            ui = yield ("Are you sure you want to recycle %s?" % self.obj1.name)
            if ui.strip().lower() in ['yes', 'y']:
                self.caller.msg("You put %s into %s." % (self.obj1.name, self.obj.name))
                self.caller.location.msg_contents("%s whirrs to live and devours %s." % (self.obj.name, self.obj1.name))
                self.obj1.location = self.obj


class RecycleBinCmdSet(CmdSet):
    key = "RecycleBinCmdSet"
    def at_cmdset_creation(self):
        self.add(CmdRecycleBinPut)
