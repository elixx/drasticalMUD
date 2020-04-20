from evennia import utils
from evennia.objects.objects import DefaultObject
from evennia.commands.command import Command
from evennia.commands.cmdset import CmdSet
from evennia import search_channel, search_object

class StatsMachine(DefaultObject):
    def at_object_creation(self):
        """
        Called whenever a new object is created
        """
        super().at_object_creation()

        self.key = "a stats machine"
        self.db.desc = "A complicated-looking blinky box."
        self.db.stats = {"startups": 1}
        self.db.guestlog = []

        self.locks.add("get:false()")
        self.cmdset.add_default(ThingCmdSet, permanent=True)


    def at_init(self):
        """
        Called when object is loaded into memory"
        """
        super().at_init()
        self.db.stats['startups'] += 1

    def at_heard_say(self, message, from_obj):
        """
        A simple listener and response.
        """
        message = message.split('says, ')[1].strip(' "')
        return message

    def msg(self, text=None, from_obj=None, **kwargs):
        """
        Custom msg() method reacting to say.
        """
        if from_obj != self:
            try:
                say_text, is_say = text[0], text[1]['type'] == 'say'
            except Exception:
                is_say = False
            if is_say:
                if("stats machine" in say_text):
                    response = self.at_heard_say(say_text, from_obj)
                    if response != None:
                        # respond to spoken text
                        pass

        super().msg(text=text, from_obj=from_obj, **kwargs)


class CmdThingStuff(Command):
    """
    verb
    """
    key = "stuff"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("You poke yourself in the face.")
            self.caller.location.msg_contents("%s pokes themself in the face." % self.caller, exclude=self.caller)
        else:
            target = self.args.strip()
            obj = self.caller.search(target)
            if not obj:
                self.caller.msg("You can't find it!")
            else:
                if 'CmdThingVerb' in dir(obj):
                    # target was Thing
                    pass

class ThingCmdSet(CmdSet):
    """
    CmdSet for the dev robot

    """

    key = "ThingCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdThingStuff())

