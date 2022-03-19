from typeclasses.mob import LegacyMob
from evennia import TICKER_HANDLER
import random


class ChattyMob(LegacyMob):
    def _chat_ticker(self, interval, hook_key, stop=False):
        idstring = "TalkerMob"
        last_chat_interval = self.db.last_chat_ticker_interval
        last_chat_hook_key = self.db.last_chat_hook_key
        if last_chat_interval and last_chat_hook_key:
            TICKER_HANDLER.remove(
                interval=last_chat_interval, callback=getattr(self, last_chat_hook_key), idstring=idstring
            )
        self.db.last_chat_ticker_interval = interval
        self.db.last_chat_hook_key = hook_key
        if not stop:
            TICKER_HANDLER.add(
                interval=interval, callback=getattr(self, hook_key), idstring=idstring
            )

    def _init_chatdb(self):
        if self.db.random_quotes == None:
            self.db.random_quotes = ["Blah blah blah", "foo bar baz"]
        if self.db.chatty == None:
            self.db.chatty = True
        if self.db.chat_frequency == None:
            self.db.chat_frequency = 5

    def do_chat(self):
        quote = random.choice(self.db.random_quotes)
        self.location.msg_contents("%s says, '%s'." % (self.name, quote))

    def at_init(self):
        super().at_init()
        self._init_chatdb()

    def at_object_creation(self):
        super().at_object_creation()
        self._init_chatdb()
        if self.db.chatty:
            self._chat_ticker(self.db.chat_frequency, "do_chat")
