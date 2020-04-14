#from evennia import DefaultCharacter as Character
from typeclasses.characters import Character
import random
from evennia import utils
from evennia import default_cmds
from evennia import CmdSet
from evennia import DefaultScript

class devRobot01(Character):
    def at_object_creation(self):
        "Called whenever a new object is created"
        # lock the object down by default
        self.locks.add("get:false()")
        # the default "get" command looks for this Attribute in order
        # to return a customized error message (we just happen to know
        # this, you'd have to look at the code of the 'get' command to
        # find out).
        self.db.get_err_msg = "The robot beeps at you, angrily. That's not a good idea."
        # We don't want to add the command to the robot.. but users in the same room...
        self.cmdset.add("typeclasses.devrobot.DevRobotCmdSet", permanent=True)
        self.scripts.add("typeclasses.devrobot.ScriptPokeRobot")
        
        self.db.max = 20
        if(self.db.quotes is None):
            self.db.quotes = ["I was a cockatoo, once...","hmmm...","I am working on... nothing!"]
        self.ndb.sleep = random.randint(1,3)
        self.deferred = utils.delay(self.ndb.sleep, self.doQuote)

    def at_init(self):
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
                    # speak ourselves, using the return
                    #self.execute_cmd("say %s" % response)   

        # this is needed if anyone ever puppets this NPC - without it you would never
        # get any feedback from the server (not even the results of look)
        super().msg(text=text, from_obj=from_obj, **kwargs)         

    def doQuote(self):
        self.ndb.sleep = random.randint(60,280)
        quote = random.choice(self.db.quotes)
        self.execute_cmd("say %s" % quote)
        self.deferred = utils.delay(self.ndb.sleep, self.doQuote)

class CmdRobotPoke(default_cmds.MuxCommand):
    key = "poke robot"
    aliases = ["poke"]
    def func(self):
        if not self.args:
            self.caller.msg("You poke yourself in the face.")
        else:
            self.caller.msg("You poke the %s" % self.args)
            self.caller.location.msg_contents("%s pokes the robot." % (self.caller.name), exclude=self.caller)
            self.obj.doQuote()
        
    
class DevRobotCmdSet(CmdSet):
    key = "DevRobotCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdRobotPoke())

class ScriptPokeRobot(DefaultScript):
    def at_script_creation(self):
        "Called when script first created."
        self.key = "poke_robot"
        self.desc = "Script that manages poking the robot."
        self.persistent = True

    def at_start(self):
        """
        This is called once every server restart, so we want to add the
        (memory-resident) cmdset to the object here. is_valid is automatically
        checked so we don't need to worry about adding the script to an
        open lid.
        """
        # All we do is add the cmdset for the closed state.
        self.obj.cmdset.add("typeclasses.devrobot.DevRobotCmdSet")

    def is_valid(self):
        """
        The script is only valid while the lid is closed.
        self.obj is the red_button on which this script is defined.
        """
        #return not self.obj.db.lid_open
        pass

    def at_stop(self):
        """
        When the script stops we must make sure to clean up after us.

        """
        self.obj.cmdset.delete("typeclasses.devrobot.DevRobotCmdSet")



