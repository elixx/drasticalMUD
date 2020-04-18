from django.conf import settings
from evennia.utils import utils

from typeclasses.social import DefaultCmdSocial, DefaultCmdSocialFmt

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

class CmdSocialNod(DefaultCmdSocial):    key = "nod"
class CmdSocialSwoon(DefaultCmdSocial):  key = "swoon"
class CmdSocialFart(DefaultCmdSocial):   key = "fart"
class CmdSocialGlare(DefaultCmdSocial):  key = "glare"
class CmdSocialLeer(DefaultCmdSocial):   key = "leer"
class CmdSocialWink(DefaultCmdSocial):   key = "wink"
class CmdSocialWave(DefaultCmdSocial):   key = "wave"
class CmdSocialShrug(DefaultCmdSocial):  key = "shrug"
class CmdSocialBog(DefaultCmdSocial):
    key = "boggle"
    aliases = ["bog"]

class CmdSocialYeet(DefaultCmdSocialFmt):
    key = "yeet"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You yeet and YOLO and it's totes extra."
            self.no_target_room_msg = "%s goes, 'YEET!' and complains about boomers." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You totes yeet %s." % self.target
            self.target_found_room_msg = "%s grabs %s and.... YEET!" % (self.caller, self.target)
            self.target_found_target_msg = "%s grabs you and.. YEET!" % self.caller
        else:
            self.target_not_found_room_msg = "%s looks around for someone to yeet." % self.caller

class CmdSocialNarf(DefaultCmdSocialFmt):
    key = "narf"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You blurt out, 'NARF!'."
            self.no_target_room_msg = "%s goes, 'NARF!', and stares off absently." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You go, 'NARF!' at %s." % self.target
            self.target_found_room_msg = "%s looks at %s and goes, 'NARF!'." % (self.caller, self.target)
            self.target_found_target_msg = "%s looks at you and goes, 'NARF!'." % self.caller
        else:
            self.target_not_found_room_msg = "%s looks around for a moment, and then stares off into space." % self.caller

class CmdSocialWoot(DefaultCmdSocialFmt):
    key = "w00t"
    aliases = ["woot"]
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You go 'w00t!'."
            self.no_target_room_msg = "%s goes, 'w00t!'." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You go, 'w00t!' at %s." % self.target
            self.target_found_room_msg = "%s looks at %s and goes, 'w00t!'." % (self.caller, self.target)
            self.target_found_target_msg = "%s looks at you and goes, 'w00t!'." % self.caller
        else:
            self.target_not_found_room_msg = ""


# noinspection PyAttributeOutsideInit
class CmdSocialWtf(DefaultCmdSocialFmt):
    key = "wtf"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You go 'wtf?!'."
            self.no_target_room_msg = "%s goes, 'wtf?!'." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You go, 'wtf?!' at %s." % self.target
            self.target_found_room_msg = "%s looks at %s and goes, 'wtf?!'." % (self.caller, self.target)
            self.target_found_target_msg = "%s looks at you and goes, 'wtf?!'." % self.caller
        else:
            self.target_not_found_room_msg = "%s wtfs." % self.caller

class CmdSocialShake(DefaultCmdSocialFmt):
    key = "shake"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You shake your head."
            self.no_target_room_msg = "%s shakes their head." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You shake your head at %s." % self.target
            self.target_found_room_msg = "%s shakes their head at %s." % (self.caller, self.target)
            self.target_found_target_msg = "%s shakes their head at you." % (self.caller)
        else:
            self.target_not_found_room_msg = "%s shakes and shivers uncontrollably." % self.caller

class CmdSocialWiggle(DefaultCmdSocialFmt):
    key = "wiggle"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You wiggle your bottom."
            self.no_target_room_msg = "%s wiggles their bottom." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You wiggle your bottom at %s." % self.target
            self.target_found_room_msg = "%s wiggles their bottom at %s." % (self.caller, self.target)
            self.target_found_target_msg = "%s wiggles their bottom at you." % (self.caller)
        else:
            self.target_not_found_room_msg = "%s wiggles around like a worm." % self.caller

class CmdSocialGlomp(DefaultCmdSocialFmt):
    key = "glomp"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You glomp around."
            self.no_target_room_msg = "%s glomps around the room." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You glomp %s." % self.target
            self.target_found_room_msg = "%s glomps %s." % (self.caller, self.target)
            self.target_found_target_msg = "%s glomps you!" % self.caller
        else:
            self.target_not_found_room_msg = "%s looks for someone to glomp." % self.caller

class CmdSocialArgh(DefaultCmdSocialFmt):
    key = "argh"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You let out an 'ARRGHHHH!!!' of frustration."
            self.no_target_room_msg = "%s lets out a frustrated 'ARRGHHHH!!!'." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You go, 'ARRGHHHH!!!' at %s." % self.target
            self.target_found_room_msg = "%s looks at %s and goes, 'ARRGHHHH!!!', frustratedly." % (self.caller, self.target)
            self.target_found_target_msg = "%s looks at you and goes, 'ARRGHHHH!!!' in frustration.." % self.caller
        else:
            self.target_not_found_room_msg = ""

class CmdSocialScream(DefaultCmdSocialFmt):
    key = "scream"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You scream loudly! "
            self.no_target_room_msg = "%s lets out a scream!'." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You scream at %s!" % self.target
            self.target_found_room_msg = "%s screams madly at %s!" % (self.caller, self.target)
            self.target_found_target_msg = "%s screams at you!" % self.caller
        else:
            self.target_not_found_room_msg = ""

class CmdSocialFall(DefaultCmdSocialFmt):
    key = "fall"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You fall over. "
            self.no_target_room_msg = "%s falls over." % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You fall on top of %s." % self.target
            self.target_found_room_msg = "%s falls on top of %s." % (self.caller, self.target)
            self.target_found_target_msg = "%s falls on top of you. Watch it!" % self.caller
        else:
            self.target_not_found_room_msg = ""

class CmdSocialRage(DefaultCmdSocialFmt):
    key = "rage"
    def parse(self):
        super().parse()
        if(self.no_args):
            self.no_target_self_msg = "You rage out. Fuck this shit!!"
            self.no_target_room_msg = "%s explodes in rage!" % self.caller
        elif(self.target_found):
            self.target_found_self_msg = "You rage out on %s." % self.target
            self.target_found_room_msg = "%s explodes in rage at %s!" % (self.caller, self.target)
            self.target_found_target_msg = "%s rages at you!" % self.caller
        else:
            self.target_not_found_room_msg = "%s wants to rage out, but can't find a reason why." % self.caller