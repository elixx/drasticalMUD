"""
Commands

Commands describe the input the account can do to the game.

"""
#from evennia.commands.default.muxcommand import MuxCommand as DefaultMuxCommand
from evennia import ObjectDB
from evennia import default_cmds
from django.conf import settings
from evennia import utils
from evennia.server.sessionhandler import SESSIONS
from core.utils import color_percent
from world.utils import area_count
from core import sendWebHook
from evennia.utils.search import object_search as search_object
from evennia.utils.search import search_tag_object, search_tag
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
                "|YName",
                "|YOn for",
                "|YIdle",
                #    "|YPuppeting",
                "|YRoom",
                "|YArea",
                "|YCmds",
                "|YVia",
                "|YHost",
                pretty_corners=False,
                border="table",
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
                                area = puppet.location.tags.get(category='area').title()
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
                #title = puppet.db.title if puppet and puppet.db.title else ""
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
            table = self.styled_table("|YName", "|YOn for", "|YIdle", "|YArea", "|YVia",
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
                if puppet == None:
                    continue
                location = puppet.location if puppet and puppet.location else "None"
                location = location.tags.get(category='area').title() if location.tags and location else "None"
                if puppet.db:
                    if puppet.db.title: title = puppet.db.title
                    else: title = ""
                else: title = ""
                table.add_row(
                    utils.crop(title + " " + account.get_display_name(account), width=25),
                    utils.time_format(delta_conn, 0),
                    utils.time_format(delta_cmd, 1),
                    utils.crop(location, width=25),
                    session.protocol_key,
                )
        is_one = naccounts == 1
        self.caller.msg(
            "|wAccounts:|n\n%s\n%s unique account%s logged in."
            % (table, "One" if is_one else naccounts, "" if is_one else "s")
        )


class CmdFinger(COMMAND_DEFAULT_CLASS):
    """
    Get information about a user's stats

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

        # find user
        target = utils.search.search_account(self.args)
        if len(target) < 1:
            self.caller.msg("I don't know about %s!" % self.args)
        else:
            target = target[0]
            if len(target.characters) > 0:
                character = target.characters[0]
                if character.db.title: title = character.db.title
                else: title = ""
            else:
                return

            max = 3
            name = title + " " + target.name
            output = "{WReporting on User: {Y%s{n\n" % name
            table = self.styled_table()
            if character.db.stats:
                logincount = character.db.stats['logins']
                visited = len(character.db.stats['visited'])
                try:
                    gold = character.db.stats['gold']
                except KeyError:
                    gold = 0
                    character.db.stats['gold'] = gold
                lastlogin = target.db.lastsite[0]
                stamp = time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime(lastlogin[1]))
                totaltime = character.db.stats['conn_time']
                m, s = divmod(totaltime.seconds, 60)
                h, m = divmod(m, 60)
                totaltime = "%dh %02dm %02ds" % (h, m, s)
                try: pct = character.db.stats['explored']
                except KeyError: pct = -1
                table.add_row("{yTimes Connected:", logincount)
                table.add_row("{yTime Online:", totaltime)
                table.add_row("{yLast Login:", stamp)
                table.add_row("{yRooms Seen:", visited)
                if pct > -1:
                    pct = str(pct) + '%'
                else:
                    pct = "???"
                table.add_row("{yPercent Explored:", pct)
                table.add_row("{yGold:", gold)
                output += str(table) + '\n'
                output += "Exploration stats are updated by visiting the Stats Machine.\n"
            if privileged and target is not None:
                logins = []
                for c in range(len(target.db.lastsite)):
                    (ip, intstamp) = target.db.lastsite[-c]
                    stamp = time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime(intstamp))
                    logins.append( (stamp, ip) )
                    if c >= max: break
                output += "{yLast %s logins:{n\n" % max
                table = self.styled_table("Date","IP")
                for(stamp, ip) in sorted(logins, reverse=True):
                    table.add_row(stamp, ip)
                output += str(table) + '\n'

            self.caller.msg(output)


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
        area = self.caller.location.tags.get(category="area")
        if area is None:
            if self.caller.location.db.area:
                area = self.caller.location.db.area
            else:
                area = "unknown"
        areaname = area.title()
        self.caller.msg("The room {c%s{n is a part of {y%s{n." % (roomname, areaname))
        if self.caller.location.db.owner:
            ownerid = self.caller.location.db.owner
            if ownerid == self.caller.id:
                self.caller.msg("This property is currently claimed by you.")
            else:
                owner_name = search_object("#"+str(ownerid))[0].name
                self.caller.msg("It is currently owned by {y%s{n." % owner_name)
        total = search_tag(area, category="area")
        total = len(total.filter(db_typeclass_path__contains="room"))
        count = 0
        owned = 0
        visited = self.caller.db.stats['visited']
        for roomid in visited:
            room = search_object("#" + str(roomid))
            if len(room) > 0:
                temp = room[0].tags.get(category='area')
                if temp == area:
                    count += 1
                    if room[0].db.owner == self.caller.id:
                        owned += 1
            else:
                continue
        pct = color_percent(round(count / total * 100, 2))
        opct = color_percent(round(owned / total * 100, 2))
        count = color_percent(count)
        self.caller.msg("You have visited %s out of {w%s{n (%s%%) rooms in {Y%s{n." % (count, total, pct, areaname))
        self.caller.msg("You own %s%% of %s." % (opct, areaname))

class CmdScore(COMMAND_DEFAULT_CLASS):
    """
    Show progress stats.

    """

    key = "score"
    locks = "cmd:all()"

    def func(self):

        character = self.caller
        if character.db.title:
            title = character.db.title
        else:
            title = ""
        name = title + " " + character.name
        table = self.styled_table()
        logincount = character.db.stats['logins']
        try:
            gold = character.db.stats['gold']
        except KeyError:
            gold = 0
            character.db.stats['gold'] = gold
        if 'conn_time' in character.db.stats.keys():
            totaltime = character.db.stats['conn_time']
            m, s = divmod(totaltime.seconds, 60)
            h, m = divmod(m, 60)
            totaltime = "%dh %02dm %02ds" % (h, m, s)
        else:
            totaltime = '-'
        if 'explored' in character.db.stats.keys():
            pct = character.db.stats['explored']
        else:
            pct = -1
        table.add_row("{yName:", name)
        table.add_row("{yTimes Connected:", logincount)
        table.add_row("{yTime Online:", totaltime)
        if pct > -1:
            pct = str(pct) + '%'
        else:
            pct = "???"
        table.add_row("{yPercent Explored:", pct)
        table.add_row("{yGold:", gold)
        output = str(table) + '\n'

        explored = {}
        totalrooms = 0
        areas = [x.db_key for x in search_tag_object(category='area')]
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
                    owner = True
                else:
                    owner = False
            else:
                continue
            if area not in explored.keys():
                total = search_tag(area, category="room").count()
                if owner:
                    explored[area] = {'total': total, 'seen': 1, 'owned': 1}
                else:
                    explored[area] = {'total': total, 'seen': 1, 'owned': 0}
            else:
                explored[area]['seen'] += 1
                if owner:
                    explored[area]['owned'] += 1
        totalvisited = len(visited)
        totalpct = round(totalvisited / totalrooms * 100, 2)
        table = self.styled_table("|YArea"+" "*35, "|YRooms", "|YSeen", "|Y%Seen", "|Y%Owned",
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
                    opct = "{wCOMPLETE{n"
                else:
                    opct = color_percent(opct)

                if pct == 100:
                    pct = "{wCOMPLETE{n"
                else:
                    pct = color_percent(pct)

                table.add_row(utils.crop(str(key).title(), width=40), value['total'], value['seen'], pct + '%', opct + '%')


        output += "{w" + utils.utils.pad(" {YExploration Stats{w ", width=79, fillchar="-") + '\n'
        output += str(table) + '\n'
        output += "{x" + utils.utils.pad(" Summary ", width=79, fillchar="-") + '\n'
        unseen = []
        for area in areas:
            if area not in explored.keys():
                unseen.append(area)
        areapct = color_percent(round(len(explored) / len(areas) * 100, 2))
        areastats = "{y%s{n of {Y%s (%s%%){n" %  ( len(explored.keys()), len(unseen), areapct )
        table = self.styled_table(width=50, border='none')
        table.add_row("|YVisited Areas:", areastats)
        if totalvisited:
            self.caller.db.stats['explored'] = totalpct
            totalpct = color_percent(totalpct)
            table.add_row("|YVisited Rooms:", "{y"+str(totalvisited)+"{n of {Y" +  str(totalrooms) + "{n (" + totalpct + "|n%|n)")
        output += str(table) + '\n'

        self.caller.msg(output)


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
                sendWebHook("Quit: " + self.caller.name + " from " + self.session.address)
            account.disconnect_session_from_account(self.session, reason)
