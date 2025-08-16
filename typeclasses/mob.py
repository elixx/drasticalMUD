import random

from django.conf import settings

from evennia import TICKER_HANDLER
from evennia import utils
from evennia.commands.cmdset import CmdSet
from typeclasses.objects import Object

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdMobOnOff(COMMAND_DEFAULT_CLASS):
    """
    Activates/deactivates Mob

    Usage:
        mobon <mob>
        moboff <mob>

    This turns the mob from active (alive) mode
    to inactive (dead) mode. It is used during
    building to  activate the mob once it's
    prepared.
    """

    key = "mobon"
    aliases = "moboff"
    locks = "cmd:superuser()"

    def func(self):
        """
        Uses the mob's set_alive/set_dead methods
        to turn on/off the mob."
        """
        if not self.args:
            self.caller.msg("Usage: mobon||moboff <mob>")
            return
        mob = self.caller.search(self.args)
        if not mob:
            return
        if self.cmdstring == "mobon":
            mob.set_alive()
        else:
            mob.set_dead()


class MobCmdSet(CmdSet):
    """
    Holds the admin command controlling the mob
    """

    def at_cmdset_creation(self):
        self.add(CmdMobOnOff())


# TODO: Copied from contrib, needs attack stuff cleaned up:
class LegacyMob(Object):
    def at_before_say(self, message, **kwargs):
        """
        Before the object says something.
        """
        styled_message = "|R" + message + "|n"
        return styled_message

    def at_init(self):
        self.ndb.is_patrolling = self.db.patrolling and not self.db.is_dead
        self.ndb.is_hunting = False
        self.ndb.is_immortal = self.db.immortal or self.db.is_dead

        super().at_init()

    def at_object_creation(self):
        """
        Called the first time the object is created.
        We set up the base properties and flags here.
        """
        self.cmdset.add(MobCmdSet, persistent=True)
        if self.db.patrolling == None:
            self.db.patrolling = True

        self.db.immortal = False
        self.db.is_dead = False

        self.db.patrolling_pace = 6
        self.db.hunting_pace = 2
        self.db.death_pace = 300  # stay dead for 100 seconds

        self.db.last_ticker_interval = None

        self.db.desc_alive = "This is a moving object."
        self.db.desc_dead = "A dead body."

        # self.db.send_defeated_to = "#2"
        # self.db.defeat_msg = "You fall to the ground."
        # self.db.defeat_msg_room = "%s falls to the ground."
        # self.db.death_msg = "After the last hit %s evaporates." % self.key
        self.db.irregular_msgs = ["the enemy looks about.", "the enemy changes stance."]

        if self.db.patrolling:
            self.start_patrolling()

        super().at_object_creation()

    def _set_ticker(self, interval, hook_key, stop=False):
        idstring = "LegacyMob"  # this doesn't change
        last_interval = self.db.last_ticker_interval
        last_hook_key = self.db.last_hook_key
        if last_interval and last_hook_key:
            TICKER_HANDLER.remove(
                interval=last_interval, callback=getattr(self, last_hook_key), idstring=idstring
            )
        self.db.last_ticker_interval = interval
        self.db.last_hook_key = hook_key
        if not stop:
            TICKER_HANDLER.add(
                interval=interval, callback=getattr(self, hook_key), idstring=idstring
            )

    def _find_target(self, location):
        targets = [
            obj
            for obj in location.contents_get(exclude=self)
            if obj.has_account  # and not obj.is_superuser
        ]
        return targets[0] if targets else None

    def set_alive(self, *args, **kwargs):
        self.db.is_dead = False
        self.db.desc = self.db.desc_alive
        self.ndb.is_immortal = self.db.immortal
        self.ndb.is_patrolling = True
        self.db.patrolling = True
        if not self.location:
            self.move_to(self.home)
        self.start_patrolling()

    def set_dead(self):
        self.db.patrolling = False
        self.ndb.is_patrolling = False
        self.ndb.is_hunting = False
        self.ndb.is_immortal = True
        # we shall return after some time
        self.start_idle()

    def start_idle(self):
        self._set_ticker(None, None, stop=True)

    def start_patrolling(self):
        if not self.db.patrolling:
            self.start_idle()
            return
        self._set_ticker(self.db.patrolling_pace, "do_patrol")
        self.ndb.is_patrolling = True
        self.ndb.is_hunting = False

    def start_hunting(self):
        if not self.db.hunting:
            self.start_patrolling()
            return
        self._set_ticker(self.db.hunting_pace, "do_hunt")
        self.ndb.is_patrolling = False
        self.ndb.is_hunting = True

    def start_attacking(self):
        if not self.db.aggressive:
            self.start_hunting()
            return
        # self._set_ticker(self.db.aggressive_pace, "do_attack")
        self.ndb.is_patrolling = False
        self.ndb.is_hunting = False
        self.ndb.is_attacking = True

    def do_patrol(self, *args, **kwargs):
        if random.random() < 0.01 and self.db.irregular_msgs:
            self.location.msg_contents(random.choice(self.db.irregular_msgs))
        if self.db.aggressive:
            target = self._find_target(self.location)
            if target:
                self.start_attacking()
                return
        exits = [exi for exi in self.location.exits if exi.access(self, "traverse")]
        if exits:
            exit = random.choice(exits)
            self.move_to(exit.destination)
        else:
            self.move_to(self.home)

    def do_hunting(self, *args, **kwargs):
        if random.random() < 0.01 and self.db.irregular_msgs:
            self.location.msg_contents(random.choice(self.db.irregular_msgs))
        if self.db.aggressive:
            target = self._find_target(self.location)
            if target:
                self.start_attacking()
                return
        exits = [exi for exi in self.location.exits if exi.access(self, "traverse")]
        if exits:
            for exit in exits:
                target = self._find_target(exit.destination)
                if target:
                    self.move_to(exit.destination)
                    return
            self.start_patrolling()
        else:
            self.move_to(self.home)

    def do_attack(self, *args, **kwargs):
        if random.random() < 0.01 and self.db.irregular_msgs:
            self.location.msg_contents(random.choice(self.db.irregular_msgs))
        target = self._find_target(self.location)
        if not target:
            self.start_hunting()
            return
        # attack_cmd = random.choice(("thrust", "pierce", "stab", "slash", "chop"))
        attack_cmd = random.choice(("burp", "fart", "smile", "narf"))
        self.execute_cmd("%s %s" % (attack_cmd, target))

    def at_new_arrival(self, new_character):
        if self.db.aggressive and not self.ndb.is_hunting:
            self.start_hunting()
