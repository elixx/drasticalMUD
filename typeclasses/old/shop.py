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
        self.cmdset.add_default(ShopRoomCmdSet, persistent=True)


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
    options = ({"desc": "some clothes", "goto": "make_clothing"},
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
        Listen, though... you'll take whatever I can find...
        
        """
    options = ({"desc": "a shirt", "goto": "make_shirt"},
               {"desc": "some pants", "goto": "make_pants"},
               {"desc": "a hazmat suit", "goto": "make_hazmat"},
               {"desc": "some sunglasses", "goto": "make_sunglasses"},
               {"desc": "a hat", "goto": "make_hat"})
    return text, options


def make_shirt(caller):
    shirts = [("a hawaiian shirt", "a loud hawaiian shirt", "looking like a tourist"),
              ("a button-up shirt", "a plain, white button-up shirt", "looking clean and proper"),
              ("a extra-large white tee", "an XXL white tee", "hangs down"),
              ("a leather shirt", "It looks like something from the Village People.", "shows off Sharpie chest-hair"),
              ("a plain blue shirt", "It's blue. It's a shirt.", ""),
              ("a shiny knit shirt", "It's made out of some kind of shimmery fabric.", "that catches your attention")]
    name, desc, worn = choice(shirts)
    shirt = create_object("core.clothing.Clothing",
                          key=name,
                          aliases=["shirt"],
                          home=caller,
                          location=caller,
                          attributes=[("clothing_type", "top"),
                                      ("desc", desc),
                                      ("worn", worn)])
    caller.msg("You get %s" % shirt.name)


def make_pants(caller):
    pants = [("a pair of black sweats", "Plain, black sweatpants with an elastic waistband and drawstring.",
              ["sweats", "pants"], ""),
             ("a pair of faded jeans", "These jeans have been bean the hell up. THey are very faded and worn.",
              ["jeans", "pants"], ""),
             ("a pair of camo pants", "Standard-issue military wear.", ["pants", "camo"], "ready for war"),
             ("a pair of cotton shorts", "A plain pair of gym shorts.", ["shorts", "cotton"], "that are a little too "
                                                                                              "short"),
             ("a pair of black fatigues", "Military-style tactical wear, but less obvious.", ["fatigues", "pants"],
              "looking prepared"),
             ("a pair of pants", "They're pants. What more could you ask for?", ["pants"], "looking nondescript")]

    name, desc, aliases, worn = choice(pants)
    shirt = create_object("core.clothing.Clothing",
                          key=name,
                          aliases=aliases,
                          home=caller,
                          location=caller,
                          attributes=[("clothing_type", "bottom"),
                                      ("desc", desc),
                                      ("worn", worn)])
    caller.msg("You get %s" % shirt.name)


def make_hazmat(caller):
    name, desc = ("a |yyellow|n hazmat suit",
                  "A |yyellow|x hazmat suit|n, such as to protect from hazardous |Gchemicals|n and |Rradiation|n.")
    suit = create_object("core.clothing.Clothing",
                         key=name,
                         aliases=["hazmat", "suit"],
                         home=caller,
                         location=caller,
                         attributes=[("clothing_type", "fullbody"),
                                     ("desc", desc),
                                     ("worn", "to protect from |yhazardous|g chemicals|n")])
    caller.msg("You get %s" % suit.name)


def make_sunglasses(caller):
    glasses = create_object("core.clothing.Clothing",
                            key="a pair of |xdark sunglasses|n",
                            aliases=["glasses", "sunglasses"],
                            home=caller,
                            location=caller,
                            attributes=[("clothing_type", "jewelry"),
                                        ("desc", "A pair of |xdark sunglasses|n."),
                                        ("worn", "that let them see the world as it |yreally|n is")])
    caller.msg("You get %s" % glasses.name)


def make_hat(caller):
    hats = [("a viking helmet", "A horned, metal viking helmet", ["viking", "helmet"], "just like Flava Flav"),
            ("a woolen beanie", "A knit ski cap", ["beanie", "hat"], ""),
            ("a baseball cap", "A plain, brimmed baseball cap", ["cap", "hat"], "pulled down low"),
            ("a pith helmet", "You'll look just like an African explorer in this!", ["helmet"],
             "like an African explorer"),
            ("a fez", "A red velvet fez, complete with tassle.", ["fez"], "with a fuzzy tassle"),
            ("a graduation cap", "You feel smart just looking at this!", ["cap", "graduation"],
             "that makes them look smart")]
    name, desc, aliases, worn = choice(hats)
    hat = create_object("core.clothing.Clothing",
                        key=name,
                        aliases=aliases,
                        home=caller,
                        location=caller,
                        attributes=[("clothing_type", "hat"),
                                    ("desc", desc),
                                    ("worn", worn)])
    caller.msg("You get %s" % hat.name)
