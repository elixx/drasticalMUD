import random
from evennia import utils
from django.conf import settings
from evennia.utils.create import create_object
from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from evennia import search_channel
from world.utils import findStatsMachine

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class robot(DefaultObject):
    def at_object_creation(self):
        """

        Set up the robot

        """

        super().at_object_creation()
        self.locks.add("get:false()")
        self.db.good_desc = "It's here for two reasons: to listen, and to be |ypoke|xd. You can |ygag|x him if you need (or like!)"
        self.db.broken_desc = "|XIt looks like something is seriously wrong. It's |rbroken|x. Maybe you can fix it?"
        self.db.get_err_msg = "The robot beeps at you, angrily. That's not a good idea."
        self.db.broken_messages = ["The %s buzzes. I think it's broken.",
                                   "The %s makes an odd humming noise and spits sparks.",
                                   "You hear a low-pitched whine coming from the %s.",
                                   "A quiet grinding noise comes from the direction of the %s.",
                                   "Blip-blop. The %s is broken.",
                                   "The robot starts to glow for a moment, then fades."]
        self.cmdset.add_default(RobotCmdSet, persistent=True)
        self.db.max = 20
        if self.db.quotes is None:
            self.db.quotes = ["I was a cockatoo, once...", "hmmm...", "I am working on... nothing!"]
        self.db.sleep = random.randint(1, 3)
        self.db.gagged = False
        self.db.broken = False
        self.db.fixers = []
        self.db.needed_fixers = -1
        self.db.desc = self.db.good_desc
        self.remove_keys = []
        self.delayQuote()

    def at_init(self):
        """
        Called when object is loaded into memory"

        """
        super().at_init()
        self.db.sleep = random.randint(1, 3)
        self.db.broken = False
        self.db.fixers = []
        self.db.needed_fixers = -1
        self.remove_keys = []
        self.delayQuote()

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

    def malfunction(self):
        if self.db.broken:
            self.location.msg_contents("A grinding sound emanates from the %s." % self.name)
        else:
            self.db.broken = True
            self.db.needed_fixers = random.randint(1, 5)
            self.db.fixers = []
            self.db.desc = self.db.broken_desc
            self.location.msg_contents("The %s gives off a bad odor and lets out a bunch of magic smoke." % self.name)

    def repair(self):
        if self.db.broken:
            self.db.broken = False
            self.db.needed_fixers = -1
            self.db.fixers = []
            self.db.desc = self.db.good_desc
            self.location.msg_contents("Suddenly, the %s whirrs back to life." % self.name)

    def drop_key(self):
        adjectives = ["golden", "silver", "shiny", "silicon", "rusty", "smelly", "glowing", "dull", "crystal", "magic"]
        keyname = "a " + random.choice(adjectives) + " key"
        newkey = create_object("typeclasses.objects.Object",
                               key=keyname,
                               home=self.location,
                               location=self.location,
                               aliases=["key"],
                               attributes=[("unlocks", ["xyzzy"]),
                                           ("ephemeral", True),
                                           ("desc",
                                            "Something seems off about it. Like it could disappear at any time.")])
        self.location.msg_contents("The %s drops %s." % (self.name, keyname))
        self.remove_keys.append(utils.delay(300, self.delay_del_key, newkey, persistent=True))

    def delay_del_key(self, obj):
        obj.location.msg_contents("%s shimmers and fades away." % obj.name)
        obj.delete()

    def delayQuote(self, poked=False, sleeptime=-1):
        if sleeptime == -1:
            sleeptime = self.db.sleep
        self.deferred = utils.delay(sleeptime, self.doQuote, poked=poked)

    def doQuote(self, poked=False):
        self.db.sleep = random.randint(10, 120)

        chances = random.randint(0, 100)  # chance of break/fix randomly
        if chances <= 2:
            chosen = True
        else:
            chosen = False

        if self.db.broken:
            if chosen:
                random.choice([self.repair(), self.drop_key()])
                self.delayQuote()
            else:
                chances = random.randint(0, 100)  # chance of break/fix randomly
                if chances < 20: chosen = True
                if chosen:
                    self.location.msg_contents(random.choice(self.db.broken_messages) % self.name)
        else:
            if chosen:
                self.malfunction()
                self.delayQuote()
            else:
                if not self.db.gagged:
                    quote = random.choice(self.db.quotes)
                    self.location.msg_contents("%s says, '%s'." % (self.name, quote))
                    self.delayQuote()
                else:
                    if poked:
                        self.location.msg_contents("%s wriggles out of the gag covering its speaker." % (self.name))
                        self.db.gagged = False
                        self.delayQuote()
                    else:
                        self.delayQuote(poked=True, sleeptime=300)


class CmdRobotPoke(COMMAND_DEFAULT_CLASS):
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
                    chances = random.randint(0, 100)  # chance of breaking
                    if chances < 8:
                        chosen = True
                    else:
                        chosen = False
                    if chosen:
                        self.caller.msg(
                            "{xYou must have hit something! Sparks fly and the {Y%s{x makes a frizzing noise." % obj)
                        self.caller.location.msg_contents(
                            "{xSparks fly and you hear a frizzing noise. It looks like {Y%s{x just {rbroke{x %s." % (
                                self.caller, obj.name),
                            exclude=self.caller)
                        yield 1
                        obj.malfunction()
                        yield random.randint(1, 3)
                        obj.delayQuote(poked=True, sleeptime=random.randint(1, 3))
                    else:
                        obj.delayQuote(poked=True, sleeptime=random.randint(1, 3))
                else:
                    self.caller.msg("That wouldn't be nice.")


class CmdRobotGag(COMMAND_DEFAULT_CLASS):
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
                    if obj.db.gagged:
                        self.caller.msg("It's already gagged!")
                    else:
                        self.caller.msg("You sneak up and put a strip of masking tape over %s's speaker." % obj)
                        self.caller.location.msg_contents(
                            "%s sneaks up and puts a strip of masking tape over %s's speaker." % (self.caller, obj),
                            exclude=self.caller)
                        obj.db.gagged = True
                else:
                    self.caller.msg("You can't gag " + self.args.strip() + "!")


class CmdRobotUngag(COMMAND_DEFAULT_CLASS):
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


class CmdRobotFix(COMMAND_DEFAULT_CLASS):
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
                    if obj.db.broken:
                        if self.caller.name in obj.db.fixers:
                            self.caller.msg(
                                "You're already working on fixing the %s! Maybe you need more help." % obj.name)
                            self.caller.location.msg_contents(
                                "%s continues to work on the %s. Maybe you can help?" % (self.caller, obj.name),
                                exclude=self.caller)
                        else:
                            obj.db.fixers.append(self.caller.name)
                            if len(obj.db.fixers) >= obj.db.needed_fixers:
                                heroes = []
                                for name in obj.db.fixers:
                                    if (name == self.caller.name):
                                        pass
                                    else:
                                        heroes.append(name)

                                machine = findStatsMachine()
                                machine.incr("robot_fixed")

                                self.caller.msg("You got it! The %s is fixed!" % obj.name)
                                self.caller.location.msg_contents(
                                    "{Y%s{x has saved the day! The {Y%s{x is {yfixed{x!" % (self.caller, obj.name),
                                    exclude=self.caller)
                                message = "{Y%s{x just fixed the robot, again"
                                if len(heroes) >= 1:
                                    message += ", with help from: {Y%s{x !"
                                    search_channel("public")[0].msg(message % (self.caller, ', '.join(heroes)))
                                else:
                                    message += "!"
                                    search_channel("public")[0].msg(message % (self.caller))
                                yield 1
                                search_channel("public")[0].msg("{xThe {Y%s{x has been fixed {Y%i{x times." % (
                                    obj.name, machine.db.stats['robot_fixed']))
                                obj.repair()
                                yield 1
                                obj.drop_key()
                            else:
                                self.caller.msg(
                                    "You set to work fixing the %s, but it seems beyond your skill. Maybe you need more help?" % obj.name)
                                self.caller.location.msg_contents(
                                    "%s starts work on the robot, looking perplexed." % self.caller,
                                    exclude=self.caller)
                                obj.db.desc = "Open panels reveal a loose wiring harness and other gizmos. It is being worked on by: {Y" + " ".join(
                                    obj.db.fixers) + "{x."
                    else:
                        self.caller.msg(
                            "You try to fix %s, but it beeps angrily and gives you an electric shock." % obj.name)
                        self.caller.location.msg_contents(
                            "%s screws around with the %s, but it gets pissed off and shocks them!" % (
                                self.caller, obj.name),
                            exclude=self.caller)
                else:
                    self.caller.msg("You try to fix the" + obj.name + ", but can't seem to figure them out.")
                    obj.msg("%s is trying to do something weird to you!" % self.caller)
                    self.caller.location.msg_contents(
                        "%s goes to work on the %s, trying to fix something or other." % (self.caller, obj.name),
                        exclude=[self.caller, obj])
                    yield 2
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
