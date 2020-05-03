from evennia import utils
from django.conf import settings
from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from datetime import datetime

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

class NewsBoard(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false()")
        if not self.db.posts:
            self.db.posts = []
        self.cmdset.add(NewsBoardCmdSet)

class CmdNewsBoardRead(COMMAND_DEFAULT_CLASS):
    key = "read"
    locks = "cmd:all()"
    def func(self):
        table = self.styled_table("{Y#","{YTime","{YAuthor", "{YPost                                ")
        cnt = 0
        for (stamp, author, post) in self.obj.db.posts:
            table.add_row(cnt,stamp.strftime("%Y-%m-%d %H:%M"),author,post)
            cnt += 1
        output = str(table)
        self.caller.msg(output)

class CmdNewsBoardPost(COMMAND_DEFAULT_CLASS):
    key = "post"
    locks = "cmd:superuser()"
    def func(self):
        stamp = datetime.now()
        self.obj.db.posts.append((stamp, self.caller.name, self.args))

class CmdNewsBoardDel(COMMAND_DEFAULT_CLASS):
    key = "bdelete"
    locks = "cmd:superuser()"
    def func(self):
        if not self.args:
            return
        else:
            p = int(self.args.strip())
            if p < len(self.obj.db.posts):
                del self.obj.db.posts[p]
                self.caller.msg("Remove post %s" % p)

class NewsBoardCmdSet(CmdSet):
    key = "NewsBoardCmdSet"
    def at_cmdset_creation(self):
        self.add(CmdNewsBoardPost)
        self.add(CmdNewsBoardRead)
        self.add(CmdNewsBoardDel)