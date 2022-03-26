from evennia import utils
from django.conf import settings
from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from evennia import search_channel
from datetime import datetime
from evennia.utils import wrap

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class NewsBoard(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false()")
        if not self.db.posts:
            self.db.posts = []
        self.cmdset.add_default(NewsBoardCmdSet, persistent=True)


class CmdNewsBoardRead(COMMAND_DEFAULT_CLASS):
    key = "read"
    locks = "cmd:all()"

    def func(self):
        table = self.styled_table("{Y#", "{YTime", "{YAuthor", "{YPost                                ")
        cnt = 0
        for (stamp, author, post) in self.obj.db.posts:
            table.add_row(cnt, stamp.strftime("%m-%d{r@{n%H:%M"), '{G' + author, wrap(post, width=50))
            cnt += 1
        output = "You read %s.\n" % self.obj.name
        output += str(table)
        self.caller.msg(output)
        self.caller.location.msg_contents("%s reads %s." % (self.caller.name, self.obj.name), exclude=self.caller)


class CmdNewsBoardPost(COMMAND_DEFAULT_CLASS):
    key = "post"
    locks = "cmd:superuser()"

    def func(self):
        stamp = datetime.now()
        post = str(self.args).strip()
        self.obj.db.posts.append((stamp, self.caller.name, post))
        self.caller.msg("You post an update to %s" % self.obj.name)
        self.caller.location.msg_contents("%s makes a new post on %s." % (self.caller.name, self.obj.name),
                                          exclude=self.caller)
        message = "%s has made a new post on %s in %s!" % (self.caller.name, self.obj.name, self.obj.location.name)
        search_channel("public")[0].msg(message)


class CmdNewsBoardDel(COMMAND_DEFAULT_CLASS):
    key = "bdelete"
    locks = "cmd:superuser()"

    def func(self):
        if not self.args:
            return
        else:
            p = int(self.args.strip())
            if p < len(self.obj.db.posts):
                answer = yield ("Delete post %s? [Yes/No]" % p)
                if answer.strip().lower() in ['yes', 'y']:
                    del self.obj.db.posts[p]
                    self.caller.msg("You removed post %s from %s" % (p, self.obj.name))
                    self.caller.location.msg_contents("%s removes a post from %s." % (self.caller.name, self.obj.name),
                                                      exclude=self.caller)


class NewsBoardCmdSet(CmdSet):
    key = "NewsBoardCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdNewsBoardPost)
        self.add(CmdNewsBoardRead)
        self.add(CmdNewsBoardDel)
