from django.conf import settings
from evennia.utils import utils
from evennia.utils.evmenu import EvMenu
from typeclasses.rooms import Room
from evennia.commands.cmdset import CmdSet
from evennia.utils.create import create_object
from random import choice

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class ShopInvRoom(Room):
    def at_object_creation(self):
        super().at_object_creation()
        if not self.db.inventory:
            self.db.inventory = {"hunter": {'key': "a mob hunter",
                                            'typeclass': "typeclasses.wiztools.WizTool",
                                            'aliases': ['hunter'],
                                            'attributes': [
                                                ('desc', "This tool lets you {Yfindmobs{n to help with the hunt.")]},
                                 "tricorder": {'key': "a tricorder",
                                               'typeclass': "typeclasses.wiztools.Tricorder",
                                               'aliases': ['scanner', 'tricorder'],
                                               'attributes': [
                                                   ("desc", "This tool lets you {Yscan{n stuff... seems dangerous.")]},
                                 "launcher": {'key': "a rocket launcher",
                                              'typeclass': 'typeclasses.gun.Gun',
                                              'aliases': ['launcher'],
                                              'attributes': [('desc', "A rocket launcher. Blow em up good."),
                                                             ('max_ammo', 25),
                                                             ('ammo', 5),
                                                             ('ammo_type', 'rocket')]},
                                 "rockets": {"key": "a rocket pack",
                                             'typeclass': 'typeclasses.objects.Object',
                                             'aliases': ['pack'],
                                             'attributes': [('desc', 'a package of rocket ammunition.'),
                                                            ('capacity', 5),
                                                            ('ammo_type', 'rocket')]},
                                 "gun": {'key': "a generic gun",
                                         'typeclass': 'typeclasses.gun.Gun',
                                         'aliases': ['gun'],
                                         'attributes': [('desc', "A gun. You know, for shooting things."),
                                                        ('max_ammo', 16),
                                                        ('ammo', 8),
                                                        ('ammo_type', 'generic')]},
                                 "ammo": {"key": "a generic clip",
                                          'typeclass': 'typeclasses.objects.Object',
                                          'aliases': ['pack'],
                                          'attributes': [('desc', 'a generic clip of gun ammunition'),
                                                         ('capacity', 8),
                                                         ('ammo_type', 'generic')]}}
        self.cmdset.add_default(ShopInvRoomCmdSet, persistent=True)


class CmdShopInvRoomShop(COMMAND_DEFAULT_CLASS):
    key = "shop"

    def func(self):
        self.caller.ndb._shopInventory = self.obj.db.inventory
        EvMenu(self.caller, "typeclasses.shop_inven", "start_menu")


class ShopInvRoomCmdSet(CmdSet):
    key = "ShopInvRoomCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdShopInvRoomShop)


def start_menu(caller, **kwargs):
    text = \
        """
        The shopkeeper peers at you suspiciously.
          "{YWhat the hell do you want?{n"
        """

    options = ()
    for k, v in caller.ndb._shopInventory.items():
        options += ({"key": k, "desc": v['attributes'][0][1], 'goto': ('make_thing', {'item': k})},)
    return text, options


def make_thing(caller, **kwargs):
    inventory = caller.ndb._shopInventory
    selection = kwargs['item']
    item = inventory[selection]

    ob = create_object(item['typeclass'],
                       key=item['key'],
                       home=caller,
                       location=caller,
                       aliases=item['aliases'],
                       attributes=item['attributes'])

    caller.msg("You get a %s." % item['key'])
    caller.location.msg("%s purchases a %s." % (caller.name, ob.name))

    del caller.ndb._shopInventory
