import random
from evennia import utils
from evennia.objects.objects import DefaultObject
from evennia.commands.command import Command
from evennia.commands.cmdset import CmdSet


class robot(DefaultObject):
    def at_object_creation(self):
        """

        Called whenever a new object is created

        """

        super().at_object_creation()
        self.locks.add("get:false()")
        self.db.desc = "{xHe's here for two reasons: to listen, and to be {ypoke{xd. You can {ygag{x him if you need (or want!)"
        self.db.get_err_msg = "The robot beeps at you, angrily. That's not a good idea."
        self.cmdset.add_default(RobotCmdSet, permanent=True)
        self.db.max = 20
        if self.db.quotes is None:
            self.db.quotes = ["I was a cockatoo, once...", "hmmm...", "I am working on... nothing!"]
        self.db.sleep = random.randint(1, 5)
        self.db.gagged = False
        self.delayQuote()

    def at_init(self):
        """
        Called when object is loaded into memory"

        """
        super().at_init()
        self.db.sleep = random.randint(1, 5)
        self.deferred = utils.delay(self.db.sleep, self.doQuote)

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
                response = self.at_heard_say(say_text, from_obj)
                if response != None:
                    chances = [True, False, False]  # 1/3 chance of listening
                    chosen = random.choice(chances)
                    if chosen:
                        self.db.quotes.insert(0, response)
                        if len(self.db.quotes) > self.db.max:
                            self.db.quotes.pop()

        super().msg(text=text, from_obj=from_obj, **kwargs)

    def delayQuote(self, to_ungag=False, sleeptime=-1):
        if sleeptime == -1:
            sleeptime = self.db.sleep
        self.deferred = utils.delay(sleeptime, self.doQuote, to_ungag)

    def doQuote(self, to_ungag=False):
        self.db.sleep = random.randint(60, 360)
        if self.db.gagged == False:
            if to_ungag:
                self.db.sleep = 1
            quote = random.choice(self.db.quotes)
            self.location.msg_contents("%s says, '%s'." % (self.name, quote))
            self.delayQuote()
        else:
            if to_ungag:
                self.location.msg_contents("%s wriggles out of the gag covering its speaker." % (self.name))
                self.db.gagged = False
                self.delayQuote()
            else:
                self.db.sleep = 600
                self.delayQuote(True)


class CmdRobotPoke(Command):
    """
    poke the robot

    """

    key = "poke"
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
                if 'doQuote' in dir(obj):
                    self.caller.msg("You poke %s." % obj)
                    self.caller.location.msg_contents("%s pokes %s." % (self.caller, obj), exclude=self.caller)
                    obj.delayQuote(to_ungag=True, sleeptime=1)
                else:
                    self.caller.msg("That wouldn't be nice.")


class CmdRobotGag(Command):
    """
    temporarily gag the robot

    """

    key = "gag"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Gag whom? The robot?")
        else:
            target = self.args.strip()
            obj = self.caller.search(target)
            if not obj:
                self.caller.msg("You can't find it!")
            else:
                if 'doQuote' in dir(obj):
                    self.caller.msg("You sneak up and put a strip of masking tape over %s's speaker." % obj)
                    self.caller.location.msg_contents(
                        "%s sneaks up and puts a strip of masking tape over %s's speaker." % (self.caller, obj),
                        exclude=self.caller)
                    obj.db.gagged = True
                else:
                    self.caller.msg("You can't gag " + self.args.strip() + "!")


class CmdRobotUngag(Command):
    """
    remove gag from the robot

    """

    key = "ungag"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Remove a gag from whom? The robot?")
        else:
            target = self.args.strip()
            obj = self.caller.search(target)
            if not obj:
                self.caller.msg("You can't find it!")
            else:
                if 'doQuote' in dir(obj):
                    if (obj.db.gagged):
                        self.caller.msg("You yank the piece of take off of %s's speaker." % obj)
                        self.caller.location.msg_contents(
                            "%s violently rips the masking tape from %s's speaker." % (self.caller, obj),
                            exclude=self.caller)
                        obj.db.gagged = False
                    else:
                        self.caller.msg("%s isn't gagged." % obj)
                else:
                    self.caller.msg("You can't ungag " + self.args.strip() + "!")


class RobotCmdSet(CmdSet):
    """
    CmdSet for the dev robot

    """

    key = "RobotCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdRobotPoke())
        self.add(CmdRobotGag())
        self.add(CmdRobotUngag())
        super().at_cmdset_creation()
