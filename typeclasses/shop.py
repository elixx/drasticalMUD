from django.conf import settings

import evennia
from evennia.commands.cmdset import CmdSet
from evennia.utils import class_from_module, variable_from_module
from evennia.prototypes import spawner
from typeclasses.objects import Object
from evennia.utils.evtable import EvTable
from core.utils import ff

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)

class Merchant(Object):

    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(ShopRoomCmdSet, persistent=True)
        if not self.db.stock:
            self.db.stock = [
                #Category, Stock,  Prototype,  Cost
                ("Farming",     -1,    'SPORE', 150),
                ("Farming",     -1,    'TREE', 200),
                ("Mining",     -1,    'REPAIR_KIT', 100),
                ("Mining",     -1,    'BASIC_AXE', 200),
                ("Mining",     -1, 'AMATEUR_AXE', 500),
                ("Mining",     -1,    'PRO_AXE', 1000),
                ("Mining",     -1,    'MASTER_AXE', 8000),
                ("Mining",     -1,    'JACKHAMMER', 15000),
                ("Buffs",     -1,    'SPEED_BOOTS', 5000),
            ]


class ShopRoomCmdSet(CmdSet):
    key = "ShopRoomCmdSet"
    def at_cmdset_creation(self):
        self.add(CmdShopRoomList)
        self.add(CmdShopRoomBuy)


class CmdShopRoomList(COMMAND_DEFAULT_CLASS):
    key = "list"
    def func(self):
        caller = self.caller
        merchant = caller.search('typeclasses.shop.Merchant', attribute_name='db_typeclass_path')
        caller.msg(f'You peruse the items offered by {merchant}:')
        rows = []
        c = 1
        for i in merchant.db.stock:
            category = i[0] if i[0] is not None else "-"
            quantity = i[1] if i[1] >= 0 else "Inf"
            item = variable_from_module(module='world.items', variable=i[2])
            cost = "%s gold" % i[3] if i[3] is not None else ' '.join(["|w%s |Y%s|n" % (v, k) for k, v in item['value'].items() if v != 0])
            rows.append((c, quantity, item['key'], cost, category))
            c+=1
        table = EvTable(ff("#"), ff("Qty"), ff("Item in Stock"), ff("Price"), ff("Category"))
        [ table.add_row(*row) for row in rows ]
        caller.msg(str(table))

class CmdShopRoomBuy(COMMAND_DEFAULT_CLASS):
    key = "buy"

    def func(self):
        selection = self.args.strip()
        caller = self.caller
        if not selection:
            caller.msg("Buy which item?")
            return False
        merchant = caller.search('typeclasses.shop.Merchant', attribute_name='db_typeclass_path')

        c=1
        stock={}
        for i in merchant.db.stock:
            category = i[0] if i[0] is not None else "-"
            quantity = i[1] if i[1] >= 0 else "Inf"
            item = variable_from_module(module='world.items', variable=i[2])
            cost = i[3] if i[3] is not None else item['value']
            stock[str(c)] = {'quantity': quantity, 'item': item, 'cost': cost, 'category': category}
            c+=1

        if str(selection) not in stock.keys():
            caller.msg(f"{merchant.name} can't find {selection} in stock.")
            caller.msg("Try using the item number like: |ybuy |Y#|n.")
            return False

        newob = stock[selection]['item']
        cost = stock[selection]['cost']
        if isinstance(cost, dict):
            if list(cost.keys()) == ['gold']:
                if cost['gold'] > caller.db.stats['gold']:
                    caller.msg("You do not have enough gold!")
                    return False
            else:
                raise("ComplexCost")

        elif isinstance(cost, int):
            if cost > caller.db.stats['gold']:
                caller.msg("You do not have enough gold!")
                return False
            else:
                cost = {'gold': cost}

            caller.db.stats['gold'] -= cost['gold']
            newob['location'] = caller
            newob['home'] = caller
            from evennia.prototypes.spawner import spawn
            spawn(newob)
            caller.msg(f"You pay {cost['gold']} gold and receive {newob['key']} from {merchant}.")

# class CmdShopRoomAddItem(COMMAND_DEFAULT_CLASS):
#     key = "add"
#
#     def func(self):
#         if not self.args:
#             self.caller.msg("Add what item?")
#             return False
#         if not self.access(self.caller, "control"):
#             self.caller.msg("You are not allowed to add things to this shop.")
#             return False
#         obj1 = self.caller.search(self.rhs)
#         if not obj1:
#             self.caller.msg(f"Can't find {self.rhs}!")
#             return False
#         pass


# class CmdShopRoomRemoveItem(COMMAND_DEFAULT_CLASS):
#     key = "remove"
#
#     def func(self):
#         if not self.args:
#             self.caller.msg("Add what item?")
#             return False
#         if not self.access(self.caller, "control"):
#             self.caller.msg("You are not allowed to add things to this shop.")
#             return False
#         obj1 = self.caller.search(self.rhs)
#         if not obj1:
#             self.caller.msg(f"Can't find {self.rhs}!")
#             return False
#         pass
