from django.conf import settings
from evennia.utils import utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

class CmdSocialNod(COMMAND_DEFAULT_CLASS):
    """
    nod
    """

    key = "nod"
    locks = "cmd:all()"

    def func(self):
        """Run the nod command"""
        caller = self.caller
        if not self.args:
                self.caller.msg("You nod.")
                self.caller.location.msg_contents("%s nods." % (self.caller), exclude=self.caller)
        else:
            target = self.args.strip()
            obj = self.caller.search(target)
            if not obj:
                self.caller.msg("You can't find it!")
            else:
                self.caller.msg("You nod at %s." % obj)
                self.caller.location.msg_contents("%s nods at %s." % (self.caller, obj), exclude=[self.caller,obj])
                obj.msg("%s nods at you." % obj)

class CmdSocialNarf(COMMAND_DEFAULT_CLASS):
    """
    narf
    """

    key = "narf"
    locks = "cmd:all()"

    def func(self):
        """Run the narf command"""
        caller = self.caller
        if not self.args:
            self.caller.msg("You go 'narf!''.")
            self.caller.location.msg_contents("%s goes 'narf!'." % (self.caller), exclude=self.caller)
        else:
            target = self.args.strip()
            obj = self.caller.search(target)
            if not obj:
                self.caller.msg("You can't find it!")
            else:
                self.caller.msg("You narf %s." % obj)
                self.caller.location.msg_contents("%s goes 'narf!' at %s." % (self.caller, obj),
                                                  exclude=[self.caller, obj])
                obj.msg("%s narfs at you." % obj)




        # receivers = [recv.strip() for recv in self.lhs.split(",")]
        #
        # receivers = [caller.search(receiver) for receiver in set(receivers)]
        # receivers = [recv for recv in receivers if recv]
        #
        # speech = self.rhs
        # # If the speech is empty, abort the command
        # if not speech or not receivers:
        #     return
        #
        # # Call a hook to change the speech before whispering
        # speech = caller.at_before_say(speech, whisper=True, receivers=receivers)
        #
        # # no need for self-message if we are whispering to ourselves (for some reason)
        # msg_self = None if caller in receivers else True
        # caller.at_say(speech, msg_self=msg_self, receivers=receivers, whisper=True)
        #
