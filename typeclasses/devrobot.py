#from evennia import DefaultCharacter as Character
from typeclasses.characters import Character
import random

class devRobot01(Character):
    def at_object_creation(self):
        "Called whenever a new object is created"
        # lock the object down by default
        self.locks.add("get:false()")
        # the default "get" command looks for this Attribute in order
        # to return a customized error message (we just happen to know
        # this, you'd have to look at the code of the 'get' command to
        # find out).
        self.db.get_err_msg = "This is too heavy to pick up."   

    def at_init(self):
        "Called when object is loaded into memory"
        self.ndb.counter = 0
        self.ndb.quotes = []

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
                        self.ndb.quotes.insert(response)
                    # speak ourselves, using the return
                    #self.execute_cmd("say %s" % response)   

        # this is needed if anyone ever puppets this NPC - without it you would never
        # get any feedback from the server (not even the results of look)
        super().msg(text=text, from_obj=from_obj, **kwargs)         
