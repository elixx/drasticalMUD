from typeclasses.mob_talker import ChattyMob
from typeclasses.rooms import CmdClaimRoom
from core.utils import combineNames
from evennia import ObjectDB
from evennia.utils.logger import log_warn
from evennia.utils.utils import crop
import random
import time


class ExplorerMob(ChattyMob):

    def at_init(self):
        self.ndb.is_patrolling = self.db.patrolling and not self.db.is_dead
        # if self.db.patrolling:
        #     self.start_patrolling()

    def at_object_creation(self):
        super().at_object_creation()
        self.ndb.seen = {}

    def at_after_move(self, source_location, **kwargs):
        area = self.location.tags.get(category='area')
        if not self.ndb.seen:
            self.ndb.seen = {}

        if area not in self.ndb.seen.keys():
            self.ndb.seen[area] = [self.location.id]
        else:
            self.ndb.seen[area].append(self.location.id)
            self.ndb.seen[area] = list(set(self.ndb.seen[area]))
        super().at_after_move(source_location)

    def do_chat(self):
        room_count = 0
        areas = []
        for key, value in self.ndb.seen.items():
            areas.append(key)
            room_count += len(value)
        self.location.msg_contents("%s says, '{yI have seen %s rooms in %s areas.{n'" %
                                   (self.name, room_count, len(areas)))

    def do_patrol(self, *args, **kwargs):
        if self.db.aggressive:
            room = self.location
            if CmdClaimRoom in self.cmdset.current.commands:
                CmdClaimRoom.func(self)

        exits = [exi for exi in self.location.exits if exi.access(self, "traverse")]
        if exits:
            exit = random.choice(exits)
            self.move_to(exit.destination)
        else:
            self.move_to(self.home)


class ContinentExplorer(ExplorerMob):
    def at_init(self):
        if not self.ndb.seen:
            self.ndb.seen = {}
        if self.db.seen:
            self.ndb.seen = self.db.seen
        if self.db.patrolling is None:
            self.db.patrolling = True
        super().at_init()

    def _find_target(self, location):
        targets = [
            obj
            for obj in location.contents_get(exclude=self)
            if obj.db_typeclass_path == "typeclasses.mob_explorer.ContinentExplorer"
        ]
        return targets[0] if targets else None

    def do_patrol(self, *args, **kwargs):
        target = self._find_target(self.location)
        if target:
            targetName = target.key
            self.key = combineNames(self.key, targetName)
            self.ndb.seen.update(target.ndb.seen)
            self.db.seen = self.ndb.seen
            target.delete()
            log_warn("%s-%s (convergence) %s+%s=%s" % (self.key, target.key, self.id, target.id, self.key))
        super().do_patrol(*args, **kwargs)

    def at_msg_receive(self, text=None, from_obj=None, **kwargs):
        if "pokes at you" in text:
            self.at_object_creation()


def restartExplorers():
    for mob in ContinentExplorer.objects.all():
        mob.location = mob.home
        mob.db.patrolling = True
        mob.db.is_dead = False
    mob.at_object_creation()


def fixContinentExplorers():
    for bot in ContinentExplorer.objects.all():
        if bot.db.seen == None:
            bot.at_object_creation()
        if not bot.db.patrolling:
            bot.db.patrolling = True
            bot.at_init()
        if bot.db.is_dead:
            bot.db.is_dead = False
        bot.db.patrolling = True


# def explorerReport(typeclass=None):
#
#     if typeclass is None:
#         x = ObjectDB.objects.get_objs_with_attr("patrolling")
#     else:
#
#
#
#     table = self.styled_table("|Y#", "|YType", "|YLocation", "|YArea", '|YDB', "|YPtl", "|YAreas", "|YRooms",
#                               border="none")
#
#     total_areas = []
#     total_rooms = 0
#     count = 0
#     cexcount = 0
#     for bot in x:
#         count += 1
#         # Get current area and location
#         if bot.location != None:
#             area = bot.location.tags.get(category='area')
#             if area is not None:
#                 area = area.title()
#             location = crop(str(bot.location.id) + ':' + bot.location.name, 30)
#         else:
#             location = None
#             area = None
#
#         # Get seen stats
#         areas_seen = []
#         rooms_seen = 0
#         if bot.ndb.seen is not None:
#             for area in bot.ndb.seen.keys():
#                 if area is not None:
#                     areas_seen.append(area)
#                     rooms_seen += len(bot.ndb.seen[area])
#             areas_seen = list(set(areas_seen))
#             total_areas += areas_seen
#             total_rooms += rooms_seen
#
#         patrolling = "Y" if bot.db.patrolling else "N"
#         explorer = "Y" if bot.ndb.seen else "N"
#         if "Continent" in bot.typeclass_path:
#             cexcount += 1
#         # Append table row
#         if area is not None:
#             area = area
#         else:
#             area = "None"
#         table.add_row(utils.crop(':'.join([str(bot.id), bot.key]), width=30, suffix=".."),
#                       str(bot.db_typeclass_path).split('.')[-1][0],
#                       utils.crop(location, width=30, suffix=".."),
#                       utils.crop(area, width=15),
#                       explorer,
#                       patrolling,
#                       len(areas_seen),
#                       rooms_seen)
