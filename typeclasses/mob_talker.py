import random

from evennia import TICKER_HANDLER
from typeclasses.mob import LegacyMob


class ChattyMob(LegacyMob):
    def at_init(self):
        if not self.db.random_quotes:
            self._init_chatdb()
        super().at_init()

    # def at_object_creation(self):
    #     super().at_object_creation()
    #     self._init_chatdb()
    #     if self.db.chatty:
    #         self._chat_ticker(self.db.chat_frequency, "do_chat")

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
        if self.db.random_quotes is  None:
            self.db.random_quotes = ["Blah blah blah", "foo bar baz"]
        if self.db.chatty is None:
            self.db.chatty = True
        if self.db.chat_frequency is None:
            self.db.chat_frequency = 5

    def do_chat(self):
        quote = random.choice(self.db.random_quotes)
        self.location.msg_contents("%s says, '%s'." % (self.name, quote))
