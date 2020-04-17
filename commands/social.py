from django.conf import settings
from evennia.utils import utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

class CmdSocialFmt(COMMAND_DEFAULT_CLASS):
    """
    generic social command, format string support

    """

    key = "verb2"
    locks = "cmd:all()"
    help_category = "social"

    def parse(self):
        caller = self.caller
        if not self.args:
            self.no_args = True
            self.no_target_self_msg = "You %s." % self.key
            self.no_target_room_msg = "%s %ss." % (self.caller, self.key)
        else:
            self.no_args = False
            self.target = self.caller.search(self.args.strip())
            if not self.target:
                self.target_found = False
                self.target_not_found_room_msg = "%s looks for a %s." % (self.caller, self.args.strip())
                self.target_not_found_self_msg = "You look around for %s, but can't find it!" % self.args.strip()
            else:
                self.target_found = True
                self.target_found_self_msg = "You %s at %s." % (self.key, self.target)
                self.target_found_room_msg = "%s %ss at %s." % (self.caller, self.key, self.target)
                self.target_found_target_msg = "%s %ss at you." % (self.caller, self.key)

    def func(self):
        key = self.key
        if self.no_args:
            self.caller.msg(self.no_target_self_msg)
            self.caller.location.msg_contents(self.no_target_room_msg, exclude=self.caller)
        else:
            if not self.target:
                self.caller.msg(self.target_not_found_self_msg)
                self.caller.location.msg_contents(self.target_not_found_room_msg,
                                                  exclude=[self.caller, self.target])
                return
            else:
                self.caller.msg(self.target_found_self_msg)
                self.caller.location.msg_contents(self.target_found_room_msg,
                                                  exclude=[self.caller, self.target])
                self.target.msg(self.target_found_target_msg)

class CmdSocialGlomp(CmdSocialFmt):
    key = "glomp"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You glomp around." % self.target
            self.no_target_room_msg = "%s glomps around the room." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You glomp %s." % self.target
            self.target_found_room_msg = "%s glomps %s." % (self.caller, self.target)
            self.target_found_target_msg = "%s glomps you!" % self.caller
        else:
            self.target_not_found_room_msg = "%s looks for someone to glomp." % self.caller

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

class CmdSocialGlare(CmdSocial):
    key = "glare"

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

class CmdSocialShake(CmdSocial):
    """
    shake something

    """
    key = "shake"

    def func(self):
        key = self.key
        if self.no_args:
            self.caller.msg("You shake your head.")
            self.caller.location.msg_contents("%s shakes their head." % self.caller, exclude=self.caller)
        else:
            if not self.target:
                self.caller.msg("You shake and shiver uncontrollably.")
                self.caller.location.msg_contents("%s shakes and shivers uncontrollably." % self.caller, exclude=self.caller)
            else:
                self.caller.msg("You shake your head at %s." % self.target)
                self.caller.location.msg_contents("%s shakes their head at %s." % (self.caller, self.target),
                                                  exclude=[self.caller, self.target])
                self.target.msg("%s shakes their head at you." % (self.caller))

class CmdSocialWiggle(CmdSocial):
    """
    wiggle something

    """
    key = "wiggle"

    def func(self):
        key = self.key
        if self.no_args:
            self.caller.msg("You wiggle your bottom.")
            self.caller.location.msg_contents("%s wiggles their bottom." % self.caller, exclude=self.caller)
        else:
            if not self.target:
                self.caller.msg("You wiggle around like a worm.")
                self.caller.location.msg_contents("%s wiggles around like a worm." % self.caller, exclude=self.caller)
            else:
                self.caller.msg("You wiggle your bottom at %s." % self.target)
                self.caller.location.msg_contents("%s wiggles their bottom at %s." % (self.caller, self.target),
                                                  exclude=[self.caller, self.target])
                self.target.msg("%s wiggles their bottom at you." % (self.caller))

