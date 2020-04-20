from evennia import utils
from evennia.objects.objects import DefaultObject
from evennia.commands.command import Command
from evennia.commands.cmdset import CmdSet
from evennia import search_channel, search_object
from datetime import datetime

class StatsMachine(DefaultObject):
    def at_object_creation(self):
        """
        Called whenever a new object is created
        """
        super().at_object_creation()

        self.key = "a stats machine"
        self.db.desc = "A complicated-looking blinky box."
        self.db.stats = {"server_start": 1,
                         "server_stop": 0,
                         "cold_start": 0,
                         "cold_stop": 0,
                         "reload_start": 0,
                         "reload_stop": 0,
                         "loaded": 0}
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

class CmdStatsMachineStats(Command):
    """
    verb
    """
    key = "get stats"
    locks = "cmd:all()"

    def func(self):
        selection = []
        output = ""

        if not self.args:
            selection = ["ALL"]
        else:
            args = self.args.strip()
            if "guest" in args.lower():
                selection.append("GUESTS")
            if "server" in args.lower():
                selection.append("SERVER")
            if "general" in args.lower():
                selection.append("GENERAL")

        for item in selection:
            if item == "GENERAL" or item == "ALL":
                game_stats = self.obj.db.stats
                output += "{x***************** {Y General Stats {x********************\n"
                table = self.styled_table("|YEvent","|YCount")
                for (key,value) in self.obj.db.stats.items():
                    table.add_row(key,value)
                output += str(table) + "\n"
                output += "\n"

            if item=="GUESTS" or item=="ALL":
                guestlog = self.obj.db.guestlog
                table = self.styled_table("|yTimestamp","|yGuest","|yConnecting IP",
                                          border="table")
                for (time,ip,user) in guestlog:
                    table.add_row(datetime.fromtimestamp(time), user, ip)
                output += "{x*************** {YGuest Connection Log: {x***************\n"
                output += str(table) + '\n'

        self.msg(output)

class StatsMachineCmdSet(CmdSet):
    """
    CmdSet for the dev robot

    """

    key = "MachineCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdStatsMachineStats())

