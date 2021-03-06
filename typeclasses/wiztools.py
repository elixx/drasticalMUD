from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from evennia import ObjectDB
from django.conf import settings
from evennia.utils import utils
from commands.command import CmdExamine
from string import capwords
from evennia.utils.evtable import EvTable
from evennia.utils.evmore import EvMore

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class WizTool(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(WizToolCmdSet, persistent=True)


class CmdFindMobs(COMMAND_DEFAULT_CLASS):
    key = "hunt"
    # locks = "cmd:superuser()"
    locks = "cmd:all()"

    def func(self):
        self.caller.msg("You use %s." % self.obj.name)
        self.caller.location.msg_contents("%s uses %s." % (self.caller.name, self.obj.name), exclude=self.caller)

        x = ObjectDB.objects.get_objs_with_attr("patrolling")
        table = EvTable("|Y#", "|YType", "|YLocation", "|YArea", '|YDB', "|YPtl", "|YAreas", "|YRooms",
                                  border="none")

        total_areas = []
        total_rooms = 0
        count = 0
        cexcount = 0
        for bot in x:
            count += 1
            # Get current area and location
            if bot.location != None:
                area = bot.location.tags.get(category='area')
                if area is not None:
                    area = capwords(area)
                location = utils.crop(str(bot.location.id) + ':' + bot.location.name, 30)
            else:
                location = None
                area = None

            # Get seen stats
            areas_seen = []
            rooms_seen = 0
            if bot.ndb.seen is not None:
                for area in bot.ndb.seen.keys():
                    if area is not None:
                        areas_seen.append(area)
                        rooms_seen += len(bot.ndb.seen[area])
                areas_seen = list(set(areas_seen))
                total_areas += areas_seen
                total_rooms += rooms_seen

            patrolling = "Y" if bot.db.patrolling else "N"
            explorer = "Y" if bot.ndb.seen else "N"
            if "Continent" in bot.typeclass_path:
                cexcount += 1
            # Append table row
            if area is not None:
                area = area
            else:
                area = "None"
            table.add_row(utils.crop(':'.join([str(bot.id), bot.key]),width=30, suffix=".."),
                          str(bot.db_typeclass_path).split('.')[-1][0],
                          utils.crop(location,width=30, suffix=".."),
                          utils.crop(area, width=15),
                          explorer,
                          patrolling,
                          len(areas_seen),
                          rooms_seen)

        areas = list(set(total_areas))
        rooms = total_rooms

        if self.caller.db.wiztool_last_len_areas:
            wiztool_last_len_areas = self.caller.db.wiztool_last_len_areas
        else:
            self.caller.db.wiztool_last_len_areas = 0
            wiztool_last_len_areas = 0

        if self.caller.db.wiztool_last_len_rooms:
            wiztool_last_len_rooms = self.caller.db.wiztool_last_len_rooms
        else:
            self.caller.db.wiztool_last_len_rooms = 0
            wiztool_last_len_rooms = 0

        if self.caller.db.wiztool_last_cex:
            wiztool_last_cex = self.caller.db.wiztool_last_cex
        else:
            self.caller.db.wiztool_last_cex = 0
            wiztool_last_cex = 0

        output = str(table) + '\n'
        output += "Total areas: %s (%s)" % (len(areas), len(areas) - wiztool_last_len_areas) + '\n'
        output += "Total rooms: %s (%s)" % (rooms, rooms - wiztool_last_len_rooms) + '\n'
        output += "CExplore bots: %s (%s)" % (cexcount, cexcount - wiztool_last_cex) + '\n'

        EvMore(self.caller, output)

        self.caller.db.wiztool_last_len_areas = len(areas)
        self.caller.db.wiztool_last_len_rooms = rooms
        self.caller.db.wiztool_last_cex = cexcount
        #self.caller.msg("Area list: %s" % (', '.join(areas)))


class WizToolCmdSet(CmdSet):
    key = "WizToolCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdFindMobs)


class Tricorder(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(TricorderCmdSet, persistent=True)
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
