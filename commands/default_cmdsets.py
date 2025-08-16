"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

import commands.social
from commands.command import CmdAreas
from commands.command import CmdBrief
from commands.command import CmdClaimed
from commands.command import CmdExamine
from commands.command import CmdFinger
from commands.command import CmdLook
from commands.command import CmdNoMap
from commands.command import CmdProperty
from commands.command import CmdQuit
from commands.command import CmdRecall
from commands.command import CmdResourceSplit
from commands.command import CmdScore
from commands.command import CmdTopList
from commands.command import CmdWhere
from commands.command import CmdWho
from commands.command import CmdWorth
from commands.command import CmdGet
from commands.social import *
from core import extended_room
from core import mail
from core.clothing import ClothedCharacterCmdSet
from evennia import default_cmds


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """

        super().at_cmdset_creation()

        self.add(ClothedCharacterCmdSet)
        self.add(SocialCmdSet)
        self.add(CmdExamine)
        self.add(CmdWhere)
        self.add(CmdRecall)
        self.add(CmdWho)
        self.add(CmdAreas)
        self.add(CmdQuit)
        self.add(CmdLook)
        self.add(extended_room.CmdExtendedRoomDesc)
        self.add(extended_room.CmdExtendedRoomDetail)
        self.add(CmdClaimed)
        self.add(CmdTopList)
        self.add(CmdProperty)
        self.add(CmdWorth)
        self.add(CmdResourceSplit)
        self.add(CmdNoMap)
        self.add(CmdBrief)
        self.add(CmdGet)

        #
        # any commands you add below will overload the default ones.
        #


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """


        super().at_cmdset_creation()

        self.add(mail.CmdMail())
        self.add(CmdFinger)
        #
        # any commands you add below will overload the default ones.
        #


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """

        self.add(CmdLook)
        self.add(CmdScore)

        super().at_cmdset_creation()

        #
        # any commands you add below will overload the default ones.
        #


class SocialCmdSet(default_cmds.CharacterCmdSet):

    key = "DefaultSocial"
    priority = 60

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()

        socials = [n for n in dir(commands.social) if n[:9] == "CmdSocial"]
        for social in socials:
            self.add(eval(social))
