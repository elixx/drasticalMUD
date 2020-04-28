from evennia.utils import logger, utils, gametime, create, search, pad
from django.conf import settings
from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from evennia import search_channel, search_object
from evennia import ObjectDB
from datetime import datetime

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class StatsMachine(DefaultObject):
    def at_object_creation(self):
        """
        Called whenever a new object is created
        """
        super().at_object_creation()

        self.key = "a stats machine"
        self.db.desc = "{xA statistics keeping machine. You can {Yget stats{x for stuff.{n"
        self.db.stats = {"server_start": 1,
                         "server_stop": 0,
                         "cold_start": 0,
                         "cold_stop": 0,
                         "reload_start": 0,
                         "reload_stop": 0,
                         "loaded": 0}
        self.db.userstats = {}
        self.db.guestlog = []

        self.locks.add("get:false()")
        self.cmdset.add_default(StatsMachineCmdSet, permanent=True)


    def at_init(self):
        """
        Called when object is loaded into memory"
        """
        super().at_init()
        if not self.db.stats['loaded']:
            self.db.stats['loaded'] = 1
        else:
            self.db.stats['loaded'] += 1

    def incr(self,statname):
        if not statname in self.db.stats.keys():
            self.db.stats[statname] = 1
        else:
            self.db.stats[statname] += 1

    def incr_kv(self, stat, key, db="stats"):
        if(db=="stats"):
            if not stat in self.db.stats.keys():
                self.db.stats[stat] = { key: 1 }
            if not key in self.db.stats[stat].keys():
                self.db.stats[stat][key] = 1
            else:
                self.db.stats[stat][key] += 1
        elif(db=="userstats"):
            if not stat in self.db.userstats.keys():
                self.db.userstats[stat] = {}
            if not key in self.db.userstats[stat].keys():
                self.db.userstats[stat][key] = 1
            else:
                self.db.userstats[stat][key] += 1

    def set(self,statname, value):
        self.db.stats[statname] = value

    def set_kv(self, stat, key, value, db="stats"):
        if(db=="stats"):
            if not stat in self.db.stats.keys():
                self.db.stats[stat] = { key: {} }
            self.db.stats[stat][key] = value
        elif(db=="userstats"):
            if not stat in self.db.userstats.keys():
                self.db.userstats[stat] = { key: {} }
            self.db.userstats[stat][key] = value



class CmdStatsMachineStats(COMMAND_DEFAULT_CLASS):
    """
    verb
    """
    key = "get stats"
    locks = "cmd:all()"

    def func(self):
        selection = []
        maxlines = 5
        width = 60

        privileged=self.caller.locks.check(self.caller,"cmd:perm_above(Helper)")

        if not self.args:
            selection = ["ALL"]
        else:
            args = self.args.strip()
            args = args.lower().split(" ")
            if "gen" in args:
                selection.append("GENERAL")
            if "ser" in args:
                selection.append("SERVER")
            if "ga" in args:
                selection.append("GAME")
            if "gu" in args:
                selection.append("GUESTS")
            if "use" in args:
                selection.append("USERS")

########################################################################################################################
        output = "\n"
        output += "{Y" + pad("{W "+ settings.SERVERNAME.upper() + " STATS {Y",width=width,fillchar="*") + '\n'
        for item in selection:

            if item == "GENERAL" or item == "ALL": ##################################################################
                totalrooms = 0
                e = ObjectDB.objects.object_totals()
                for k in e.keys():
                    if "room" in k.lower():
                        totalrooms += e[k]
                if self.caller.db.stats['visited']:
                    visited = len(self.caller.db.stats['visited'])
                else: visited=None
                if visited: pct = round(visited / totalrooms,2)

                output += "{x" + pad(" {yGeneral Stats{x ",width=width,fillchar="*") + '\n'
                table = self.styled_table(border="none", width=width)
                table.add_row(
                    "Current time ", datetime.fromtimestamp(gametime.gametime(absolute=True)) )
                table.add_row("Total rooms ", totalrooms)
                if(visited):
                    table.add_row("You have visited ", str(visited) + " (" + str(pct) + "%)")
                output += str(table)+"\n\n"

            if item == "SERVER" or item == "ALL": ###################################################################
                output += "{x" + pad(" {yServer Stats{x ",width=width,fillchar="*") + '\n'
                table = self.styled_table(border="none", width=width)
                table.add_row("Current uptime", utils.time_format(gametime.uptime(), 3))
                table.add_row("First start", datetime.fromtimestamp(gametime.server_epoch()))
                table.add_row("Total runtime", utils.time_format(gametime.runtime(), 2))
                output += str(table)+"\n\n"
                if privileged:
                    table = self.styled_table("|YEvent","|YCount",border="none", width=width)
                    for (key, value) in self.obj.db.stats.items():
                        #if ("start" in key or "stop" in key):
                        label = key.replace("_", " ").capitalize()
                        table.add_row(label, value)
                    output += str(table) + "\n\n"

            if item=="USERS" or item=="ALL": #########################################################################
                output += "{x" + pad(" {YTop "+str(maxlines)+" Users:{x ", width=width, fillchar="*") + '\n'
                userlog = self.obj.db.userstats
                table = self.styled_table("|YUser","|YLogins", border=None, width=width)
                count = 0
                for k, v in sorted(userlog.items(), key=lambda v: v[1]['logins'], reverse=True):
                    count += 1
                    if count > maxlines:
                        break
                    if not privileged:
                        user = k[:k.find("(")]
                    else:
                        user = k
                    table.add_row(user,v['logins'])
                output += str(table) + '\n\n'

            if item=="GUESTS" or item=="ALL": #########################################################################
                if privileged:
                    output += "{x" + pad(" {YLast " + str(maxlines) + " Guests:{x ", width=width, fillchar="*") + '\n'
                    guestlog = self.obj.db.guestlog
                    table = self.styled_table("{yTimestamp","{yGuest","{yConnecting IP", border="none", width=width)
                    count = 0
                    for (time,ip,user) in guestlog:
                        count += 1
                        if count > maxlines:
                            break
                        table.add_row(datetime.fromtimestamp(time), user, ip)
                    output += str(table) + '\n'

########################################################################################################################
        self.msg(output)

class StatsMachineCmdSet(CmdSet):
    """
    CmdSet for the dev robot

    """

    key = "MachineCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdStatsMachineStats())



