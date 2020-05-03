from django.conf import settings
from evennia.utils import utils
from evennia.utils.evmenu import EvMenu
from typeclasses.rooms import Room
from evennia.commands.cmdset import CmdSet
from evennia.utils.create import create_object
from typeclasses.objects import Object
from random import choice

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
    options = ({"desc": "clothing", "goto": "make_clothing"},
               {"desc": "a gun", "goto": "make_gun"},
               {"desc": "ammo", "goto": "make_ammo"})
    return text, options


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


def make_clothing(caller):
    text = \
        """
        What kind of clothing are you looking for?
        """
    options = ({"desc": "Shirt", "goto": "make_shirt"},
               {"desc": "Pants", "goto": "make_pants"},
               {"desc": "Hazmat suit", "goto": "make_hazmat"},
               {"desc": "Sunglasses", "goto": "make_sunglasses"},
               {"desc": "Hat", "goto": "make_hat"})
    return text, options


def make_shirt(caller):
    shirts = [("a hawaiian shirt", "a loud hawaiian shirt"),
              ("a button-up shirt", "a plain, white button-up shirt"),
              ("a extra-large white tee", "an XXL white tee"),
              ("a leather shirt", "It looks like something from the Village People."),
              ("a plain blue shirt", "It's blue. It's a shirt."),
              ("a shiny knit shirt", "It's made out of some kind of shimmery fabric.")]
    name, desc = choice(shirts)
    shirt = create_object("evennia.contrib.clothing.Clothing",
                          key=name,
                          aliases=["shirt"],
                          home=caller,
                          location=caller,
                          attributes=[("clothing_type", "top"),
                                      ("desc", desc)])
    caller.msg("You get %s" % shirt.name)


def make_pants(caller):
    pants = [("a pair of black sweats", "Plain, black sweatpants with an elastic waistband and drawstring.",
              ["sweats", "pants"]),
             ("a pair of faded jeans", "These jeans have been bean the hell up. THey are very faded and worn.",
              ["jeans", "pants"]),
             ("a pair of camo pants", "Standard-issue military wear.", ["pants", "camo"]),
             ("a pair of cotton shorts", "A plain pair of gym shorts.", ["shorts", "cotton"]),
             ("a pair of black fatigues", "Military-style tactical wear, but less obvious.", ["fatigues", "pants"]),
             ("a pair of pants", "They're pants. What more could you ask for?", ["pants"])]

    name, desc, aliases = choice(pants)
    shirt = create_object("evennia.contrib.clothing.Clothing",
                          key=name,
                          aliases=aliases,
                          home=caller,
                          location=caller,
                          attributes=[("clothing_type", "bottom"),
                                      ("desc", desc)])
    caller.msg("You get %s" % shirt.name)


def make_hazmat(caller):
    name, desc = ("a {Yyellow{n hazmat suit",
                  "A {Yyellow{x hazmat suit{n, such as to protect from hazardous {Gchemicals{n and {Rradiation{n.")
    suit = create_object("evennia.contrib.clothing.Clothing",
                         key=name,
                         aliases=["hazmat", "suit"],
                         home=caller,
                         location=caller,
                         attributes=[("clothing_type", "fullbody"),
                                     ("desc", desc)])
    caller.msg("You get %s" % suit.name)


def make_sunglasses(caller):
    glasses = create_object("evennia.contrib.clothing.Clothing",
                            key="a pair of {xdark sunglasses{n",
                            aliases=["glasses", "sunglasses"],
                            home=caller,
                            location=caller,
                            attributes=[("clothing_type", "jewelry"),
                                        ("desc", "A pair of {xdark sunglasses{n.")])
    caller.msg("You get %s" % glasses.name)


def make_hat(caller):
    hats = [("a viking helmet", "A horned, metal viking helmet", ["viking", "helmet"]),
            ("a woolen beanie", "A knit ski cap", ["beanie", "hat"]),
            ("a baseball cap", "A plain, brimmed baseball cap", ["cap", "hat"]),
            ("a pith helmet", "You'll look just like an African explorer in this!", ["helmet"]),
            ("a fez", "A red velvet fez, complete with tassle.", ["fez"]),
            ("a graduation cap", "You feel smart just looking at this!", ["cap", "graduation"])]
    name, desc, aliases = choice(hats)
    hat = create_object("evennia.contrib.clothing.Clothing",
                        key=name,
                        aliases=aliases,
                        home=caller,
                        location=caller,
                        attributes=[("clothing_type", "hat"),
                                    ("desc", desc)])
    caller.msg("You get %s" % hat.name)
