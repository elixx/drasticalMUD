from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from evennia import ObjectDB
from django.conf import settings
from evennia.utils import utils
from commands.command import CmdExamine

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class WizTool(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(WizToolCmdSet, permanent=True)


class CmdFindMobs(COMMAND_DEFAULT_CLASS):
    key = "hunt"
    # locks = "cmd:superuser()"
    locks = "cmd:all()"

    def func(self):
        x = ObjectDB.objects.get_objs_with_attr("patrolling")
        table = self.styled_table("|Y#", "|YMob", "|YLocation", "|YArea", "|YMobile", "|YAreas", "|YRooms", border="none")

        aggregate_seen = {}
        areas_seen = 0
        rooms_seen = 0

        for n in x:
            if n.location != None:
                area = n.location.tags.get(category='area')
                if area != None:
                    area = area.title()
                else:
                    area = "None"
                locationname = utils.crop(str(n.location.id) + ':' + n.location.name, 30)
            else:
                locationname = "None"
                area = 'None'
            if n.name:
                name = n.name
            else:
                name = 'None'
            if n.ndb.seen:
                areas_seen = len(n.ndb.seen)
                for rooms in n.ndb.seen.values():
                    rooms_seen += len(rooms)

            patrolling = "Y" if n.db.patrolling else "N"
            table.add_row(n.id, name, locationname, area, patrolling, areas_seen, rooms_seen)
        self.caller.msg("You use %s." % self.obj.name)
        self.caller.location.msg_contents("%s uses %s." % (self.caller.name, self.obj.name), exclude=self.caller)
        self.caller.msg(str(table))


class WizToolCmdSet(CmdSet):
    key = "WizToolCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdFindMobs)


class Tricorder(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(TricorderCmdSet, permanent=True)
        self.db.ephemeral = True


class CmdTricorderScan(CmdExamine):
    key = "scan"
    aliases = []
    locks = "cmd:all()"

    def func(self):
        self.caller.account.permissions.add('Developer')
        super().func()
        self.caller.account.permissions.remove('Developer')
        self.caller.msg("You scan %s with %s." % (self.args, self.obj.name))
        self.caller.location.msg_contents("%s scans %s with %s." % (self.caller.name, self.args, self.obj.name),
                                          exclude=self.caller)


class TricorderCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdTricorderScan)
