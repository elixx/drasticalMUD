"""
Commands

Commands describe the input the account can do to the game.

"""
from evennia.commands.default.muxcommand import MuxCommand as DefaultMuxCommand
from evennia import default_cmds
from django.conf import settings
from evennia import utils
from evennia.server.sessionhandler import SESSIONS
from world.utils import area_count, sendWebHook
import time

COMMAND_DEFAULT_CLASS = utils.utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdExamine2(default_cmds.CmdExamine):
    aliases = ["exa"]


class CmdWho2(COMMAND_DEFAULT_CLASS):
    """
    list who is currently online

    Usage:
      who
      doing

    Shows who is currently online. Doing is an alias that limits info
    also for those with all permissions.
    """

    key = "who"
    aliases = "doing"
    locks = "cmd:all()"

    # this is used by the parent
    account_caller = True

    def func(self):
        """
        Get all connected accounts by polling session.
        """

        account = self.account
        session_list = SESSIONS.get_sessions()

        session_list = sorted(session_list, key=lambda o: o.account.key)

        if self.cmdstring == "doing":
            show_session_data = False
        else:
            show_session_data = account.check_permstring("Developer") or account.check_permstring(
                "Admins"
            )

        naccounts = SESSIONS.account_count()
        if show_session_data:
            # privileged info
            table = self.styled_table(
                "|YAccount Name",
                "|YOn for",
                "|YIdle",
                #    "|YPuppeting",
                "|YRoom",
                "|YCmds",
                "|YProtocol",
                "|YHost",
                pretty_corners=False,
                border="table",
                border_char="-",
                header_line_char="-"
            )
            for session in session_list:
                if not session.logged_in:
                    continue
                delta_cmd = time.time() - session.cmd_last_visible
                delta_conn = time.time() - session.conn_time
                account = session.get_account()
                puppet = session.get_puppet()
                location = puppet.location.key if puppet and puppet.location else "None"
                table.add_row(
                    utils.crop(account.get_display_name(account), width=20),
                    utils.time_format(delta_conn, 0),
                    utils.time_format(delta_cmd, 1),
                    utils.crop(location, width=25),
                    session.cmd_total,
                    utils.crop(session.protocol_key, 6, suffix='..'),
                    utils.crop(isinstance(session.address, tuple) and session.address[0] or session.address, width=18),
                )
        else:
            # unprivileged
            table = self.styled_table("|YAccount name", "|YOn for", "|YIdle", "|YRoom", "|YCmds", "|YProtocol",
                                      pretty_corners=True,
                                      border="table",
                                      border_char="-",
                                      header_line_char="-",
                                      )
            for session in session_list:
                if not session.logged_in:
                    continue
                delta_cmd = time.time() - session.cmd_last_visible
                delta_conn = time.time() - session.conn_time
                account = session.get_account()
                puppet = session.get_puppet()
                location = puppet.location.key if puppet and puppet.location else "None"
                table.add_row(
                    utils.crop(account.get_display_name(account), width=20),
                    utils.time_format(delta_conn, 0),
                    utils.time_format(delta_cmd, 1),
                    utils.crop(location, width=25),
                    session.cmd_total,
                    session.protocol_key,
                )
        is_one = naccounts == 1
        self.caller.msg(
            "|wAccounts:|n\n%s\n%s unique account%s logged in."
            % (table, "One" if is_one else naccounts, "" if is_one else "s")
        )


class CmdAreas(COMMAND_DEFAULT_CLASS):
    """
    list of tagged areas

    """

    key = "areas"
    locks = "cmd:all()"
    priority = -60

    def func(self):
        table = self.styled_table("|YArea", "|YRooms", width=60)
        for (key, value) in sorted(area_count().items(), key=lambda x: x[1], reverse=True):
            table.add_row(key, value)
        output = str(table) + '\n'
        self.caller.msg(output)


class CmdWhere(COMMAND_DEFAULT_CLASS):
    """
    Show current area

    """

    key = "where"
    locks = "cmd:all()"

    def func(self):
        roomname = self.caller.location.name
        if (self.caller.location.db.area):
            areaname = self.caller.location.db.area
            areaname = areaname.title()
        else:
            areaname = "Unknown"
        self.caller.msg("The room {c%s{n is a part of {y%s{n." % (roomname, areaname))


class CmdRecall(COMMAND_DEFAULT_CLASS):
    """
    Return to your home.

    """
    key = "recall"
    locks = "cmd:all()"

    def func(self):
        home = self.caller.home
        home = utils.search.search_object(home)
        if len(home) > 0:
            if not self.caller.db.no_recall and not self.caller.ndb.no_recall:
                self.caller.location.msg_contents("%s is {cswept{C away{n...", exclude=self.caller)
                self.caller.msg("You summon your energy and are {cswept{C away{n...")
                self.caller.move_to(home[0])
        else:
            self.caller.msg("Uh-oh! You are homeless!")


class CmdLook2(default_cmds.CmdLook):
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<account>

    Observes your location or objects in your vicinity.
    """

    key = "look"
    aliases = ["l", "ls", "ll"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    priority = -60

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        if not self.args:
            target = caller.location
            caller.msg("You look around.")
            caller.location.msg_contents("%s looks around." % caller, exclude=caller)
            if not target:
                caller.msg("You have no location to look at!")
                return
        else:
            target = caller.search(self.args)
            if not target:
                return

        if 'false' not in target.locks.get('puppet') or target.has_account != 0:
            self.msg("You look at %s" % target, options=None)
            caller.location.msg_contents("%s looks at %s." % (caller, target), exclude=[caller, target])
            target.msg("%s looks at you." % caller)

        self.msg((caller.at_look(target), {"type": "look"}), options=None)


class CmdQuit(COMMAND_DEFAULT_CLASS):
    """
    quit the game

    Usage:
      quit

    Switch:
      all - disconnect all connected sessions

    Gracefully disconnect your current session from the
    game. Use the /all switch to disconnect from all sessions.
    """

    key = "quit"
    switch_options = ("all",)
    locks = "cmd:all()"

    # this is used by the parent
    account_caller = True

    logout_screen = """
                                      
|W88                                    |w88  
|C88                                    |W88  
|C88                                    |y88  
|C88,dPPYba,   8b       d8   ,adPPYba,  |y88  
|c88P'    "8a  `8b     d8'  a8P_____88  |y88  
|c88       d8   `8b   d8'   8PP"""""""  ""  
|b88b,   ,a8"    `8b,d8'    "8b,   ,aa  |Yaa  
|b8Y"Ybbd8"'       Y88'      `"Ybbd8"'  |Y88  
|B                 d8'                      
|B                d8'                       

    """

    def func(self):
        """hook function"""
        account = self.account

        if "all" in self.switches:
            account.msg(
                "|RQuitting|n all sessions. Hope to see you soon again.", session=self.session
            )
            reason = "quit/all"
            for session in account.sessions.all():
                account.disconnect_session_from_account(session, reason)
        else:
            nsess = len(account.sessions.all())
            reason = "quit"
            if nsess == 2:
                account.msg("|RQuitting|n. One session is still connected.", session=self.session)
            elif nsess > 2:
                account.msg(
                    "|RQuitting|n. %i sessions are still connected." % (nsess - 1),
                    session=self.session,
                )
            else:
                # we are quitting the last available session
                account.msg("{YY'all c{yome b{Wack n{yow, y{Y'hear{n...?\n" + self.logout_screen, session=self.session)
            sendWebHook("Quit: " + self.name + " from " + session.address)
            account.disconnect_session_from_account(self.session, reason)
