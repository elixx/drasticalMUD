from django.conf import settings
from evennia.utils import utils
from evennia.utils.evmenu import EvMenu
from typeclasses.rooms import Room
from evennia.commands.cmdset import CmdSet
from evennia.utils.create import create_object
from typeclasses.objects import Object
from random import choice

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class SShopRoom(Room):
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(SShopRoomCmdSet, permanent=True)


class CmdSShopRoomShop(COMMAND_DEFAULT_CLASS):
    key = "shop"

    def func(self):
        EvMenu(self.caller, "typeclasses.shop_special", "start_menu")


class SShopRoomCmdSet(CmdSet):
    key = "SShopRoomCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdSShopRoomShop)


def start_menu(caller):
    text = \
        """
        Use these things wisely...
        """
    options = ({"desc": "a mob hunter", "goto": "make_findmobtool"},
               {"desc": "a tricorder", "goto": "make_tricorder"},
               {"desc": "a gun", "goto": "make_gun"},
               {"desc": "ammo", "goto": "make_ammo"})
    return text, options


def make_findmobtool(caller):
    wiztool = create_object("typeclasses.wiztools.WizTool",
                         key="a mob hunter",
                         aliases=["mob", "hunter"],
                         home=caller,
                         location=caller,
                         attributes=[("desc", "This tool lets you {Yfindmobs{n to help with the hunt.")])
    caller.msg("You get %s" % wiztool.name)

def make_tricorder(caller):
    wiztool = create_object("typeclasses.wiztools.Tricorder",
                         key="a tricorder",
                         aliases=["tricorder"],
                         home=caller,
                         location=caller,
                         attributes=[("desc", "This tool lets you {Yscan{n stuff... seems dangerous.")])
    caller.msg("You get %s" % wiztool.name)


def make_gun(caller):
    ammo = create_object("typeclasses.gun.Gun",
                         key="a generic gun",
                         aliases=["gun"],
                         home=caller,
                         location=caller,
                         attributes=[("ammo_type", "generic"),
                                     ("max_ammo", 16),
                                     ("desc", "A gun. You know, for shooting things.")])
    caller.msg("You get %s" % ammo.name)


def make_ammo(caller):
    ammo = create_object(Object,
                         key="a generic clip",
                         aliases=["clip"],
                         home=caller,
                         location=caller,
                         attributes=[("ammo_type", "generic"),
                                     ("capacity", 8),
                                     ("desc", "A standard 8-shot clip.")])
    caller.msg("You get %s" % ammo.name)


