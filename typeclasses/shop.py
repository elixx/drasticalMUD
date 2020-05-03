from django.conf import settings
from evennia.utils import utils
from evennia.utils.evmenu import EvMenu
from typeclasses.rooms import Room
from evennia.commands.cmdset import CmdSet
from evennia.utils.create import create_object
from typeclasses.objects import Object

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class ShopRoom(Room):
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(ShopRoomCmdSet, permanent=True)


class CmdShopRoomShop(COMMAND_DEFAULT_CLASS):
    key = "shop"

    def func(self):
        EvMenu(self.caller, "typeclasses.shop", "start_menu")


class ShopRoomCmdSet(CmdSet):
    key = "ShopRoomCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdShopRoomShop)

def start_menu(caller):
    text = \
        """
        What do you want?
        """
    options = ({"desc": "Sunglasses",
                "goto": "make_sunglasses"},
               {"desc": "a gun",
                "goto": "make_gun"},
               {"desc": "ammo",
                "goto": "make_ammo"})
    return text, options

def make_sunglasses(self):
    glasses = create_object("evennia.contrib.clothing.Clothing",
                           key="a pair of {xdark sunglasses{n",
                           aliases=["glasses","sunglasses"],
                           home=self,
                           location=self,
                           attributes=[("clothing_type", "head"),
                                       ("desc", "A pair of {xdark sunglasses{n.")])
    self.msg("You get %s" % glasses.name)

def make_gun(self):
    ammo = create_object(Object,
                           key="a generic gun",
                           aliases=["gun"],
                           home=self,
                           location=self,
                           attributes=[("ammo_type", "generic"),
                                       ("max_ammo", 16),
                                       ("desc", "A gun. You know, for shooting things.")])
    self.msg("You get %s" % ammo.name)

def make_ammo(self):
    ammo = create_object(Object,
                           key="a generic clip",
                           aliases=["clip"],
                           home=self,
                           location=self,
                           attributes=[("ammo_type", "generic"),
                                       ("capacity", 8),
                                       ("desc", "A standard 8-shot clip.")])
    self.msg("You get %s" % ammo.name)