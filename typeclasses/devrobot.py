#from evennia import DefaultCharacter as Character
from typeclasses.characters import Character
import random
from evennia import utils, default_cmds
from evennia import Command, CmdSet

class devRobot01(Character):
    def at_object_creation(self):
        "Called whenever a new object is created"
        super().at_object_creation()
        # lock the object down by default
        self.locks.add("get:false()")
        self.locks.add("call:false()")
        # the default "get" command looks for this Attribute in order
        # to return a customized error message (we just happen to know
        # this, you'd have to look at the code of the 'get' command to
        # find out).
        self.db.get_err_msg = "The robot beeps at you, angrily. That's not a good idea."
        # We don't want to add the command to the robot.. but users in the same room...
        self.cmdset.add_default(DevRobotCmdSet, permanent=True)
        #self.cmdset.add("commands.default_cmdsets.CharacterCmdSet",permanent=True)
        self.db.max = 20
        if(self.db.quotes is None):
            self.db.quotes = ["I was a cockatoo, once...","hmmm...","I am working on... nothing!"]
        self.ndb.sleep = random.randint(1,3)
        self.deferred = utils.delay(self.ndb.sleep, self.doQuote)

    def at_init(self):
        super().at_init()
        "Called when object is loaded into memory"
        self.ndb.sleep = random.randint(1,5)
        self.deferred = utils.delay(self.ndb.sleep, self.doQuote)

    def at_heard_say(self, message, from_obj):
        """
        A simple listener and response. This makes it easy to change for
        subclasses of NPCs reacting differently to says.

        """ 
        # message will be on the form `<Person> says, "say_text"`
        # we want to get only say_text without the quotes and any spaces
        message = message.split('says, ')[1].strip(' "')

        # we'll make use of this in .msg() below
        #return "%s said: '%s'" % (from_obj, message)
        return message

    def msg(self, text=None, from_obj=None, **kwargs):
        "Custom msg() method reacting to say."

        if from_obj != self:
            # make sure to not repeat what we ourselves said or we'll create a loop
            try:
                # if text comes from a say, `text` is `('say_text', {'type': 'say'})`
                say_text, is_say = text[0], text[1]['type'] == 'say'
            except Exception:
                is_say = False
            if is_say:
                # First get the response (if any)
                response = self.at_heard_say(say_text, from_obj)
                # If there is a response
                if response != None:
                    chances = [True,False,False] # 1/3 chance of listening
                    chosen = random.choice(chances)
                    if(chosen):
                        self.db.quotes.insert(0,response)
                        if(len(self.db.quotes) > self.db.max):
                            self.db.quotes.pop()

        # this is needed if anyone ever puppets this NPC - without it you would never
        # get any feedback from the server (not even the results of look)
        super().msg(text=text, from_obj=from_obj, **kwargs)         

    def doQuote(self):
        self.ndb.sleep = random.randint(60,280)
        quote = random.choice(self.db.quotes)
        self.location.msg_content("%s says, '%s'." % (self.name, quote) )
        self.deferred = utils.delay(self.ndb.sleep, self.doQuote)

#class CmdRobotPoke(default_cmds.MuxCommand):
class CmdRobotPoke(Command):
    key = "poke"
    aliases = ["poke robot"]
    locks = "cmd:all()"
    
    def parse(self):
        target = self.args.strip()

    def func(self):
        super().func()
        if not self.args:
            self.caller.msg("You poke yourself in the face.")
        else:
            obj = self.caller.search(target)
            if not obj:
                self.caller.msg("You can't find it!")
            else:
                self.caller.msg("You poke %s." % obj)
                self.caller.location.msg_contents("%s pokes %s." % (self.caller, obj), exclude=self.caller)
                obj.doQuote()

        
class DevRobotCmdSet(default_cmds.CharacterCmdSet):
    key = "DevRobotCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdRobotPoke())
        super().at_cmdset_creation()       
