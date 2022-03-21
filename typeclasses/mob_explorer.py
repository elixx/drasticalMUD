from typeclasses.mob_talker import ChattyMob, LegacyMob
from typeclasses.rooms import CmdClaimRoom
from world.bookmarks import starts as start_rooms
from world.utils import combineNames
from evennia.utils.logger import log_warn
import random

class ExplorerMob(ChattyMob):

    def at_init(self):
        super(LegacyMob).at_init()
        self.ndb.seen = {}

    def at_object_creation(self):
        super().at_object_creation()
        self.db.chatty = False
        self.ndb.seen = {}

    def at_after_move(self, source_location, **kwargs):
        area = self.location.tags.get(category='area')
        if not self.ndb.seen:
            self.ndb.seen = {}

        if area not in self.ndb.seen.keys():
            self.ndb.seen[area] = [ self.location.id ]
        else:
            self.ndb.seen[area].append( self.location.id )
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
        self.ndb.seen = self.db.seen
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
            log_warn("%s %s - convergence detected: %s %s" % (self.id, self.key, target.id, target.key))
            targetName = target.key
            self.key = combineNames(self.key, targetName)
            self.ndb.seen.update(target.ndb.seen)
            self.db.seen = self.ndb.seen
            log_warn("\t #%s seen: [%s]" % (self.id, ','.join(list(self.ndb.seen.keys()))))
            target.delete()
        super().do_patrol(*args, **kwargs)

        # exits = [exi for exi in self.location.exits if exi.access(self, "traverse")]
        # if exits:
        #     exit = random.choice(exits)
        #     self.move_to(exit.destination)
        # else:
        #     self.move_to(self.home)

