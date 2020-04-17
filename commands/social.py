from django.conf import settings
from evennia.utils import utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

class CmdSocial(COMMAND_DEFAULT_CLASS):
    """
    generic social command, self verbs at target

    """

    key = "verb"
    locks = "cmd:all()"
    help_category = "social"

    def parse(self):
        if not self.args:
            self.no_args = True
        else:
            self.no_args = False
            self.target = self.caller.search(self.args.strip())
            if not self.target:
                return
                #self.caller.msg("You can't find %s!" % self.args.strip())

    def func(self):
        key = self.key
        if self.no_args:
            caller = self.caller
            self.caller.msg("You " + key + ".")
            self.caller.location.msg_contents("%s %ss." % (caller, key), exclude=caller)
        else:
            if not self.target:
                return
            else:
                self.caller.msg("You %s at %s." % (key, self.target))
                self.caller.location.msg_contents("%s %ss at %s." % (self.caller, key, self.target),
                                                  exclude=[self.caller, self.target])
                self.target.msg("%s %ss at you." % (self.caller, key))

class CmdSocialGoes(CmdSocial):
    """
    generic social command, self goes verb! at target

    """

    def parse(self):
        super().parse()
        self.goes = "go '" + self.key +"!'"

    def func(self):
        key = self.key + "!"
        if self.no_args:
            caller = self.caller
            goes = self.goes
            self.caller.msg("You " + goes +".")
            self.caller.location.msg_contents("%s %s." % (caller, goes.replace("go","goes")), exclude=caller)
        else:
            if not self.target:
                self.caller.msg("You can't find it!")
            else:
                self.caller.msg("You go '%s' at %s." % (key, self.target))
                self.caller.location.msg_contents("%s goes '%s' at %s." % (self.caller, key, self.target),
                                                  exclude=[self.caller, self.target])
                self.target.msg("%s %s at you." % (self.caller, self.goes.replace("go","goes")))

class CmdSocialDirect(CmdSocial):
    """
    generic social command, self verbs target

    """

    def func(self):
        if self.no_args:
            caller = self.caller
            self.caller.msg("You " + self.key +".")
            self.caller.location.msg_contents("%s %ss." % (caller, self.key), exclude=caller)
        else:
            if not self.target:
                self.caller.msg("You can't find it!")
            else:
                self.caller.msg("You %s %s." % (self.key, self.target))
                self.caller.location.msg_contents("%s %ss %s." % (self.caller, self.key, self.target),
                                                  exclude=[self.caller, self.target])
                self.target.msg("%s %ss you." % (self.caller, self.key))

class CmdSocialNod(CmdSocial):
    key = "nod"

class CmdSocialSwoon(CmdSocial):
    key = "swoon"

class CmdSocialFart(CmdSocial):
    key = "fart"

class CmdSocialYeet(CmdSocialGoes):
    key = "yeet"

class CmdSocialLeer(CmdSocial):
    key = "leer"

class CmdSocialWink(CmdSocial):
    key = "wink"

class CmdSocialWave(CmdSocial):
    key = "wave"

class CmdSocialShrug(CmdSocial):
    key = "shrug"

class CmdSocialBog(CmdSocial):
    key = "boggle"
    aliases = ["bog"]

class CmdSocialNarf(CmdSocialGoes):
    key = "narf"

class CmdSocialWoot(CmdSocialGoes):
    key = "w00t"
    aliases = ["woot"]

class CmdSocialWtf(CmdSocialGoes):
    key = "wtf"

class CmdSocialGlomp(CmdSocialDirect):
    key = "glomp"

class CmdSocialHate(CmdSocialDirect):
    key = "hate"

class CmdSocialNerf(CmdSocialDirect):
    key = "nerf"
