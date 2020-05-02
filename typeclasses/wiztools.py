from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from evennia import ObjectDB
from django.conf import settings
from evennia.utils import utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)



class WizTool(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(WizToolCmdSet, permanent=True)


class CmdFindMobs(COMMAND_DEFAULT_CLASS):
    key = "findmobs"
    #locks = "cmd:superuser()"
    locks = "cmd:all()"

    def func(self):
        x = ObjectDB.objects.get_objs_with_attr("patrolling")
        table = self.styled_table("|YMob", "|YLocation","|YArea", border="none")
        for n in x:
            if n.location.db.area:
                area = n.location.db.area
            else:
                area = ""
            table.add_row(n.name, n.location.name, area)
        self.caller.msg(str(table))



class WizToolCmdSet(CmdSet):
    key = "WizToolCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdFindMobs)

