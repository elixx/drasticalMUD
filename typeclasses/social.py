from django.conf import settings
from evennia.utils import utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class DefaultCmdSocial(COMMAND_DEFAULT_CLASS):
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
                self.caller.msg("You can't find %s!" % self.args.strip())
                return

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


class DefaultCmdSocialFmt(COMMAND_DEFAULT_CLASS):
    """
    generic social command

    """
    # override parse() vars after super():
    #    no_target_self_msg
    #    no_target_room_msg
    #    target_not_found_room_msg
    #    target_not_found_self_msg
    #    target_found_self_msg
    #    target_found_room_msg
    #    target_found_target_msg

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
            if self.no_target_self_msg != "":
                self.caller.msg(self.no_target_self_msg)
            if self.no_target_room_msg != "":
                self.caller.location.msg_contents(self.no_target_room_msg, exclude=self.caller)
        else:
            if not self.target_found:
                if self.target_not_found_self_msg != "":
                    self.caller.msg(self.target_not_found_self_msg)
                if self.target_not_found_room_msg != "":
                    self.caller.location.msg_contents(self.target_not_found_room_msg,
                                                      exclude=[self.caller, self.target])
                return
            else:
                if self.target_found_self_msg != "":
                    self.caller.msg(self.target_found_self_msg)
                if self.target_found_room_msg != "":
                    self.caller.location.msg_contents(self.target_found_room_msg,
                                                      exclude=[self.caller, self.target])
                if self.target_found_target_msg != "":
                    self.target.msg(self.target_found_target_msg)