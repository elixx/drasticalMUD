from evennia.utils import utils, gametime, pad, search
from django.conf import settings
from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from evennia import ObjectDB
from evennia import search_object
from datetime import datetime
from world.utils import color_percent
from evennia import TICKER_HANDLER as tickerhandler
from world.utils import area_count

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class StatsMachine(DefaultObject):
    def at_object_creation(self):
        """
        Called whenever a new object is created
        """
        super().at_object_creation()

        self.key = "a stats machine"
        self.db.desc = "{xA statistics keeping machine. You can {Yget stats{x for stuff.{n"
        if not self.db.stats:
            self.db.stats = {"server_start": 1,
                             "server_stop": 0,
                             "cold_start": 0,
                             "cold_stop": 0,
                             "reload_start": 0,
                             "reload_stop": 0,
                             "loaded": 0}
        if not self.db.userstats:
            self.db.userstats = {}
        if not self.db.guestlog:
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

    def incr(self, statname):
        if not statname in self.db.stats.keys():
            self.db.stats[statname] = 1
        else:
            self.db.stats[statname] += 1

    def incr_kv(self, stat, key, db="stats"):
        if (db == "stats"):
            if not stat in self.db.stats.keys():
                self.db.stats[stat] = {key: 1}
            if not key in self.db.stats[stat].keys():
                self.db.stats[stat][key] = 1
            else:
                self.db.stats[stat][key] += 1
        elif (db == "userstats"):
            if not stat in self.db.userstats.keys():
                self.db.userstats[stat] = {}
            if not key in self.db.userstats[stat].keys():
                self.db.userstats[stat][key] = 1
            else:
                self.db.userstats[stat][key] += 1

    def set(self, statname, value):
        self.db.stats[statname] = value

    def set_kv(self, stat, key, value, db="stats"):
        if (db == "stats"):
            if not stat in self.db.stats.keys():
                self.db.stats[stat] = {key: {}}
            self.db.stats[stat][key] = value
        elif (db == "userstats"):
            if not stat in self.db.userstats.keys():
                self.db.userstats[stat] = {key: {}}
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
        width = 70

        privileged = self.caller.locks.check(self.caller, "cmd:perm_above(Helper)")

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
            if "ar" in args or "wo" in args:
                selection.append("AREAS")

        ########################################################################################################################
        output = "\n"
        output += "{Y" + pad("{W " + settings.SERVERNAME.upper() + " STATS {Y", width=width, fillchar="*") + '\n'
        for item in selection:
            if item == "GENERAL" or item == "ALL":  #####################################################################
                output += "{x" + pad(" {yGeneral Stats{x ", width=width, fillchar="*") + '\n'
                table = self.styled_table(border="none", width=width)
                table.add_row("Current time ", datetime.fromtimestamp(gametime.gametime(absolute=True)))
                output += str(table) + "\n"

            if item == "SERVER" or item == "ALL":  ######################################################################
                output += "{x" + pad(" {yServer Stats{x ", width=width, fillchar="*") + '\n'
                table = self.styled_table(border="none", width=width)
                table.add_row("Current uptime", utils.time_format(gametime.uptime(), 3))
                table.add_row("First start", datetime.fromtimestamp(gametime.server_epoch()))
                table.add_row("Total runtime", utils.time_format(gametime.runtime(), 2))
                output += str(table) + "\n"
                # if privileged:
                table = self.styled_table("|YEvent", "|YCount", border="none", width=width)
                for (key, value) in self.obj.db.stats.items():
                    # if ("start" in key or "stop" in key):
                    label = key.replace("_", " ").title()
                    table.add_row(label, value)
                output += str(table) + "\n"

            if item == "AREAS" or item == "ALL":  ###########################################################################
                explored = {}
                owned = {}
                totalrooms = 0
                e = ObjectDB.objects.object_totals()
                for k in e.keys():
                    if "room" in k.lower():
                        totalrooms += e[k]
                visited = self.caller.db.stats['visited']
                for roomid in visited:
                    room = search_object("#" + str(roomid))
                    if len(room) > 0:
                        room = room[0]
                        area = room.tags.get(category='area')
                        if room.db.owner == self.caller.id:
                            if area not in owned.keys():
                                owned[area] = 1
                            else:
                                owned[area] +=1
                    else:
                        continue
                    if area not in explored.keys():
                        total = search.search_tag(area, category="area")
                        total = len(total.filter(db_typeclass_path__contains="room"))
                        explored[area] = {'total': total, 'count': 1}
                    else:
                        explored[area]['count'] += 1
                totalvisited = len(visited)
                totalpct = round(totalvisited / totalrooms * 100, 2)

                table = self.styled_table("|YArea                          ", "|YRooms", "|YVisited", "|Y%Seen", "|Y%Owned",
                                          border="none", width=width)
                for key, value in sorted(explored.items(), key=lambda x: x[1]['count'] / x[1]['total'], reverse=True):
                    if key is not None:
                        pct = round(value['count'] / value['total'] * 100, 1)
                        if key in owned.keys():
                            opct = round(owned[key] / value['total'] * 100, 1)
                        else:
                            opct = 0
                        pct = color_percent(pct)
                        opct = color_percent(opct)
                        table.add_row(utils.crop(str(key).title(),width=18), value['total'], value['count'], pct + '%', opct + '%')

                output += "{x" + pad(" {YExploration Stats{x ", width=width, fillchar="*") + '\n'
                output += str(table) + '\n'
                table = self.styled_table(width=width, border='none')
                table.add_row("|YTotal Rooms", totalrooms)
                if totalvisited:
                    self.caller.db.stats['explored'] = totalpct
                    totalpct = color_percent(totalpct)
                    table.add_row("|YTotal Explored:", str(totalvisited) + " (" + totalpct + "|G%|n)")

                output += str(table) + '\n'

            if item == "USERS" or item == "ALL":  ###########################################################################
                output += "{x" + pad(" {YTop " + str(maxlines) + " Users:{x ", width=width, fillchar="*") + '\n'
                userlog = self.obj.db.userstats
                table = self.styled_table("|YUser", "|YLogins", border=None, width=width)
                count = 0
                for k, v in sorted(userlog.items(), key=lambda v: v[1]['logins'], reverse=True):
                    count += 1
                    if count > maxlines:
                        break
                    if not privileged:
                        user = k[:k.find("(")]
                    else:
                        user = k
                    table.add_row(user, v['logins'])
                output += str(table) + '\n'

            if item == "GUESTS" or item == "ALL":  ##########################################################################
                if privileged:
                    table = self.styled_table("{yTimestamp", "{yGuest", "{yConnecting IP", border="none", width=width)
                else:
                    table = self.styled_table("{yTimestamp", "{yGuest", border="none", width=width)
                output += "{x" + pad(" {YLast " + str(maxlines) + " Guests:{x ", width=width, fillchar="*") + '\n'
                guestlog = self.obj.db.guestlog
                count = 0
                for (time, ip, user) in guestlog:
                    count += 1
                    if count > maxlines:
                        break
                    if (privileged):
                        table.add_row(datetime.fromtimestamp(time), user, ip)
                    else:
                        table.add_row(datetime.fromtimestamp(time), user)
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
