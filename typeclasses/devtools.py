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
        self.db.good_desc = "{xHe's here for two reasons: to listen, and to be {ypoke{xd. You can {ygag{x him if you need (or like!)"
        self.db.broken_desc = "{XIt looks like something is seriously wrong. It's {rbroken{X. Maybe you can fix it?"
        self.db.get_err_msg = "The robot beeps at you, angrily. That's not a good idea."
        self.cmdset.add_default(RobotCmdSet, permanent=True)
        self.db.max = 20
        if self.db.quotes is None:
            self.db.quotes = ["I was a cockatoo, once...", "hmmm...", "I am working on... nothing!"]
        self.db.sleep = random.randint(1, 5)
        self.db.gagged = False
        self.db.broken = False
        self.db.fixers = 0
        self.db.needed_fixers = 0
        self.db.desc = self.db.good_desc
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

    def malfunction(self):
        self.db.broken = True
        self.db.needed_fixers = random.randint(1,5)
        self.db.fixers = 0
        self.db.desc = self.db.broken_desc
        self.location.msg_contents("The %s gives a final 'clink' and lets out its magic smoke." % self.name)


    def repair(self):
        self.db.broken = False
        self.db.needed_fixers = 0
        self.db.fixers = 0
        self.db.desc = self.db.good_desc
        self.location.msg_contents("Suddenly, the %s whirrs back to life! I think it's fixed!" % self.name)

    def doQuote(self, to_ungag=False):
        self.db.sleep = random.randint(60, 360)
        chances = random.randint(0,100)  # chance of break/fix randomly
        if chances < 2: chosen = True
        else: chosen = False

        if self.db.broken:
            self.location.msg_contents("The %s makes a dull rumbling sound sound. I think it's broken." % self.name)
            if chosen:
                self.repair()
                self.delayQuote()
        else:
            if not self.db.gagged:
                if to_ungag:
                    self.db.sleep = 2
                if chosen:
                    self.malfunction()
                    self.delayQuote()
                else:
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
                    chances = random.randint(0,100)  # chance of breaking
                    if chances < 20: chosen = True
                    else: chosen = False
                    if chosen:
                        self.caller.msg("Uh-oh, you sure did something! Sparks fly and the %s makes a frizzing noise." % obj)
                        self.caller.location.msg_contents("Sparks fly and you hear a frizzing noise. It looks like %s just broke the %s..." % (self.caller, obj.name),
                                                          exclude=self.caller)
                        obj.malfunction()
                    else:
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
                    if obj.db.gagged:
                        self.caller.msg("You yank the piece of take off of %s's speaker." % obj)
                        self.caller.location.msg_contents(
                            "%s violently rips the masking tape from %s's speaker." % (self.caller, obj),
                            exclude=self.caller)
                        obj.db.gagged = False
                    else:
                        self.caller.msg("%s isn't gagged." % obj)
                else:
                    self.caller.msg("You can't ungag " + self.args.strip() + "!")



class CmdRobotFix(Command):
    """
    fix the robot
    """

    key = "fix"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("What, you think you can fix something?")
        else:
            target = self.args.strip()
            obj = self.caller.search(target)
            if not obj:
                self.caller.msg("You can't find it!")
            else:
                if 'doQuote' in dir(obj):
                    self.caller.msg("You go to work on %s, trying to fix the problem." % obj)
                    self.caller.location.msg_contents(
                        "% starts working on fixing %s." % (self.caller, obj),
                        exclude=self.caller)
                    if obj.db.broken:
                        obj.db.fixers += 1
                        if obj.db.fixers >= obj.db.needed_fixers:
                            self.caller.msg("You got it! The %s is fixed!" % obj.name)
                            self.caller.location.msg_contents("%s has saved the day! The %s is fixed!" % (self.caller, obj.name),
                                                              exclude=self.caller)
                            obj.repair()
                    else:
                        self.caller.msg("You try to fix %s, but it beeps angrily and gives you an electric shock." % obj.name)
                        self.caller.location.msg_contents("%s screws around with %s, but it gets pissed off and shocks them!" % (self.caller, obj.name),
                                                          exclude=self.caller)
                else:
                    self.caller.msg("You try to fix " + obj.name + ", but can't seem to figure them out.")
                    obj.msg("%s is trying to do something weird to you!" % self.caller)
                    self.caller.location.msg_contents("%s goes to work on %s, trying to fix something or other." % (self.caller, obj.name),
                                                        exclude=[self.caller, obj])
                    self.caller.location.msg_contents("%s gives up." % self.caller, exclude=[self.caller, obj])



class RobotCmdSet(CmdSet):
    """
    CmdSet for the dev robot

    """

    key = "RobotCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdRobotPoke())
        self.add(CmdRobotGag())
        self.add(CmdRobotUngag())
        self.add(CmdRobotFix())
        super().at_cmdset_creation()
