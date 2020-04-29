"""
Commands

Commands describe the input the account can do to the game.

"""
from evennia.commands.default.muxcommand import MuxCommand as DefaultMuxCommand
from evennia import default_cmds
from django.conf import settings
from evennia.utils import utils
from evennia.server.sessionhandler import SESSIONS
from world.utils import area_count
import time


COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)



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
    aliases = ["where"]
    locks = "cmd:all()"
    priority = -60

    def func(self):
        table = self.styled_table("|YArea", "|YRooms", width=45)
        for (key, value) in sorted(area_count().items(), key=lambda x: x[1], reverse=True):
            table.add_row(key, value)
        output = str(table) + '\n'
        self.caller.msg(output)



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


