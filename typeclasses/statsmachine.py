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
        self.db.stats = {"startups": 1}
        self.db.guestlog = []

        self.locks.add("get:false()")
        self.cmdset.add_default(StatsMachineCmdSet, permanent=True)


    def at_init(self):
        """
        Called when object is loaded into memory"
        """
        super().at_init()
        self.db.stats['startups'] += 1

class CmdStatsMachineStats(Command):
    """
    verb
    """
    key = "get stats"
    locks = "cmd:all()"

    def func(self):
        selection = []
        output = ""
        game_stats = self.obj.db.stats
        guestlog = self.obj.db.guestlog

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
                output += "{x***************** {Y General Stats {x********************\n"
                output += "{xThe server has been {rreloaded{x {Y%i{x times" % game_stats['startups'] + '\n'
                output += "\n"

            if item=="GUESTS" or item=="ALL":
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

