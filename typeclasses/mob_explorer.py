from typeclasses.mob_talker import ChattyMob, LegacyMob
from evennia import TICKER_HANDLER

class ExplorerMob(ChattyMob):
    def at_init(self):
        self.ndb.seen = {}
        super(LegacyMob).at_init()

    def at_object_creation(self):
        super().at_object_creation()
        self.db.chatty = False

    def at_after_move(self, source_location, **kwargs):
        area = self.location.tags.get(category='area')

        if not self.ndb.seen:
            self.ndb.seen = {}

        if area not in self.ndb.seen.keys():
            self.ndb.seen[area] = [ self.location.id ]
        else:
            self.ndb.seen[area].append( self.location.id )
            self.ndb.seen[area] = set(self.ndb.seen[area])
        super().at_after_move(source_location)

    def do_chat(self):
        room_count = 0
        areas = []
        for key, value in self.ndb.seen.items():
            areas.append(key)
            room_count += len(value)
        self.location.msg_contents("%s says, '{yI have seen %s rooms in %s areas.{n'" %
                                   (self.name, room_count, len(areas)))