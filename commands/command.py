"""
Commands

Commands describe the input the account can do to the game.

"""
# from evennia.commands.default.muxcommand import MuxCommand as DefaultMuxCommand
from evennia import ObjectDB
from evennia import default_cmds
from django.conf import settings
from evennia import utils
from evennia.server.sessionhandler import SESSIONS
from world.utils import area_count
from core import sendWebHook
from core.utils import fingerPlayer, rainbow, fade, color_percent, ff
from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object, search_tag
from evennia.utils.evmore import EvMore
from evennia.utils.evtable import EvTable
from world.utils import visited_in_area, claimed_in_area, total_rooms_in_area
from string import capwords
from core.extended_room import CmdExtendedRoomLook

import time

COMMAND_DEFAULT_CLASS = utils.utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdExamine(default_cmds.CmdExamine):
    aliases = ["exa"]


class CmdWho(COMMAND_DEFAULT_CLASS):
    """
    list who is currently online

    Usage:
      who

    Shows who is currently online.

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
                ff("Name"),
                ff("On for"),
                ff("Idle"),
                #    "|YPuppeting",
                ff("Room"),
                ff("Area"),
                ff("Cmds"),
                ff("Via"),
                ff("Host"),
                pretty_corners=False,
                border="none",
                border_char="-",
                header_line_char="-"
            )
            for session in session_list:
                if not session.logged_in:
                    continue
                if session.puppet is None:
                    continue
                delta_cmd = time.time() - session.cmd_last_visible
                delta_conn = time.time() - session.conn_time
                account = session.get_account()
                puppet = session.get_puppet()
                if puppet is not None:
                    if puppet.location is not None:
                        location = puppet.location
                        if location.tags:
                            try:
                                area = capwords(puppet.location.tags.get(category='area'))
                            except:
                                area = "None"
                        else:
                            area = "None"
                        location = location.key
                    else:
                        location = "None"
                        area = "None"
                else:
                    location = "None"
                    area = "None"
                title = ""
                if puppet.db:
                    if puppet.db.title is not None:
                        try:
                            title = puppet.db.title
                        except:
                            title = ""
                else:
                    title = ""
                # title = puppet.db.title if puppet and puppet.db.title else ""
                table.add_row(
                    utils.crop(title + " " + account.get_display_name(account), width=25),
                    utils.time_format(delta_conn, 0),
                    utils.time_format(delta_cmd, 1),
                    utils.crop(location, width=25),
                    utils.crop(area, width=25),
                    session.cmd_total,
                    utils.crop(session.protocol_key, 6, suffix='..'),
                    utils.crop(isinstance(session.address, tuple) and session.address[0] or session.address, width=18),
                )
        else:
            # unprivileged
            table = self.styled_table(ff("Name"), ff("On for"), ff("Idle"), ff("Area"), ff("Via"),
                                      pretty_corners=True,
                                      border="none",
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
                if puppet == None:
                    continue
                location = puppet.location if puppet and puppet.location else "None"
                if location is not "None":
                    area = location.tags.get(category='area')
                    area = capwords(area) if area is not None else "None"
                if puppet.db:
                    if puppet.db.title:
                        title = puppet.db.title
                    else:
                        title = ""
                else:
                    title = ""
                table.add_row(
                    utils.crop(title + " " + account.get_display_name(account), width=25),
                    utils.time_format(delta_conn, 0),
                    utils.time_format(delta_cmd, 1),
                    utils.crop(area, width=25),
                    session.protocol_key,
                )
        is_one = naccounts == 1
        output = "|wAccounts:|n\n%s\n%s unique account%s logged in." % (table, "One" if is_one else naccounts, "" if is_one else "s")
        EvMore(self.caller, output)


class CmdFinger(COMMAND_DEFAULT_CLASS):
    """
    Get information about yourself or another user's stats

    """
    key = "finger"
    aliases = ["last"]
    locks = "cmd:all()"

    def func(self):
        # for access to ip addresses:
        privileged = self.caller.locks.check(self.caller, "cmd:perm_above(Helper)")

        # if no args then the target is the players self
        if not self.args:
            self.args = self.caller.name

        output = fingerPlayer(self.args)
        self.caller.msg(output)


class CmdAreas(COMMAND_DEFAULT_CLASS):
    """
    Show a table of all areas and room statistics.

    """

    key = "areas"
    locks = "cmd:all()"
    priority = -60

    def func(self):
        table = EvTable(ff("Area"), ff("Rooms"), width=60)
        for (key, value) in sorted(area_count().items(), key=lambda x: x[1], reverse=True):
            table.add_row(capwords(key), value)
        output = str(table) + '\n'
        EvMore(self.caller, output)


class CmdWhere(COMMAND_DEFAULT_CLASS):
    """
    Show info about your current area

    """

    key = "where"
    aliases = ["seen"]
    locks = "cmd:all()"

    def func(self):
        start = time.time()  ##DEBUG
        roomname = self.caller.location.name
        area = self.caller.location.tags.get(category="area")
        if area is None:
            if self.caller.location.db.area:
                area = self.caller.location.db.area
            else:
                area = "unknown"
        areaname = capwords(area)
        self.caller.msg("The room |c%s|n is a part of |y%s|n." % (roomname, areaname))
        if self.caller.location.db.owner:
            ownerid = self.caller.location.db.owner
            if ownerid == self.caller.id:
                self.caller.msg("This property is currently claimed by you.")
            else:
                owner_name = search_object("#" + str(ownerid))[0].name
                self.caller.msg("It is currently claimed by |y%s|n." % owner_name)

        total = total_rooms_in_area(area)
        count = len(visited_in_area(area, self.caller.id))
        owned = len(claimed_in_area(area, self.caller.id))

        pct = color_percent(round(count / total * 100, 2))
        opct = color_percent(round(owned / total * 100, 2))
        count = color_percent(count)
        self.caller.msg("You have visited %s out of |w%s|n (%s%%) rooms in |Y%s|n." % (count, total, pct, areaname))
        self.caller.msg("You own %s%% of %s." % (opct, areaname))
        end = time.time()  ##DEBUG
        utils.logger.log_err("CmdWhere.func() took %ss" % (end - start))  ##DEBUG


class CmdScore(COMMAND_DEFAULT_CLASS):
    """
    Show player statistics.

    """

    key = "score"
    locks = "cmd:all()"

    def func(self):
        start = time.time()  ##DEBUG
        character = self.caller
        output = ""
        explored = {}
        totalrooms = 0
        totalvisited = 0
        areas = [x.db_key for x in search_tag_object(category='area')]

        # Systemwide room total:
        e = ObjectDB.objects.object_totals()
        for k in e.keys():
            if "room" in k.lower():
                totalrooms += e[k]

        # Sanity check
        if not self.caller.db.stats:
            raise("NotAPlayerNoMore")
        else:
            owner = self.caller.id
            visited = self.caller.db.stats['visited']

        for area in visited.keys():
            if area not in explored.keys():
                explored[area] = {}
            explored[area]['total'] = total_rooms_in_area(area)
            explored[area]['seen'] = len(visited_in_area(area, owner))
            totalvisited += explored[area]['seen']
            claimed = claimed_in_area(area, owner)
            explored[area]['owned'] = claimed.count()

        totalpct = round(totalvisited / totalrooms * 100, 2)
        table = self.styled_table(ff("Area") + " " * 45, ff("Seen"), ff("%Seen"), ff("Owned"), ff("%Owned"), ff("Total"),
                                  border="none", width=80)
        for key, value in sorted(list(explored.items()), key=lambda x: x[1]['seen'], reverse=True):
            if key is not None:
                if value['total'] > value['seen']:
                    pct = round(value['seen'] / value['total'] * 100, 1)
                else:
                    pct = 0

                if value['total'] > value['owned']:
                    opct = round(value['owned'] / value['total'] * 100, 1)
                else:
                    opct = 0

                if opct == 100:
                    opct = rainbow("COMPLETE")
                else:
                    opct = color_percent(opct)

                if pct == 100:
                    pct = rainbow("COMPLETE")
                else:
                    pct = color_percent(pct)

                table.add_row(utils.crop(capwords(str(key)), width=50),
                              value['seen'],
                              pct + '%',
                              value['owned'],
                              opct + '%',
                              value['total'])

        output += ff("----------------------------")+ff(" Exploration Stats ")+ff("----------------------------") + '\n'
        output += str(table) + '\n'
        output += ff("-------------------")+ff(" Summary ")+ff("-------------------") + '\n'
        unseen = []
        for area in areas:
            if area not in explored.keys():
                unseen.append(area)
        areapct = color_percent(round(len(explored) / len(areas) * 100, 2))
        areastats = "{y%s{n of {Y%s (%s%%){n" % (len(explored.keys()), len(unseen), areapct)
        table = self.styled_table(width=50, border='none')
        table.add_row(ff("Visited Areas:"), areastats)
        if totalvisited:
            self.caller.db.stats['explored'] = totalpct
            totalpct = color_percent(totalpct)
            table.add_row(ff("Visited Rooms:"),
                          "{y" + str(totalvisited) + "{n of {Y" + str(totalrooms) + "{n (" + totalpct + "|n%|n)")
        output += str(table) + '\n'

        output = fingerPlayer(character) + output

        self.caller.msg(output)

        end = time.time()  ##DEBUG


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
                self.caller.location.msg_contents("%s is swept away...", exclude=self.caller)
                self.caller.msg("You summon your energy and are swept away...")
                self.caller.move_to(home[0])
        else:
            self.caller.msg("Uh-oh! You are homeless!")


class CmdLook(CmdExtendedRoomLook):
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
    # locks = "cmd:all()"
    # arg_regex = r"\s|$"
    # priority = -60

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
                super().func()
                return

        if 'false' not in target.locks.get('puppet') or target.has_account != 0:
            self.msg("You look at %s" % target, options=None)
            caller.location.msg_contents("%s looks at %s." % (caller, target), exclude=[caller, target])
            target.msg("%s looks at you." % caller)

        #self.msg((caller.at_look(target), {"type": "look"}), options=None)
        super().func()


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
                sendWebHook("Quit: " + self.caller.name + " from " + self.session.address)
            account.disconnect_session_from_account(self.session, reason)



class CmdClaimed(COMMAND_DEFAULT_CLASS):
    """
    See top landowners

    """
    key = "claimed"
    locks = "cmd:all()"

    def func(self):
        from typeclasses.rooms import topClaimed
        claimed = topClaimed()
        table = EvTable(ff("Player"), ff("Rooms Owned"))
        for (player, count) in claimed:
            table.add_row(player, count)
        output = str(table) + '\n'
        self.caller.msg(output)


class CmdProperty(COMMAND_DEFAULT_CLASS):
    """
    See what property you have currently claimed

    """
    key = "property"
    locks = "cmd:all()"

    def func(self):
        from evennia.utils.search import search_object_attribute
        claimed = [ room for room in search_object_attribute(key='owner', value=self.caller.id) ]
        claimed = sorted(claimed, key=lambda x: x.tags.get(category="area"))
        table = EvTable(ff("Area"), ff("Rooms"), border="none")
        for room in claimed:
            table.add_row(capwords(room.tags.get(category='area')), room.name)
        output = str(table) + '\n'
        self.caller.msg(output)



class CmdTopList(COMMAND_DEFAULT_CLASS):
    """
    See top player statistics

    """
    key = "toplist"
    aliases=['top']
    locks = "cmd:all()"

    def func(self):
        from typeclasses.rooms import topClaimed
        from world.utils import topGold
        claimed = topClaimed()
        gold = topGold()
        stats = {}
        for (player, count) in claimed:
            if player in stats.keys():
                stats[player]['claimed'] = count
            else:
                stats[player] = { 'claimed': count, 'gold': '-' }
        for (player, g) in gold:
            if player in stats.keys():
                stats[player]['gold'] = g
            else:
                stats[player] = { 'claimed': '-', 'gold': g }

        table = EvTable(ff("Player"), ff("Rooms Owned"), ff("Total Gold"), border="none")
        for i,v in stats.items():
            table.add_row(i, v['claimed'], v['gold'])
        output = str(table) + '\n'
        self.caller.msg(output)
