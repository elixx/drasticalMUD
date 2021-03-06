from evennia import DefaultObject
from evennia.commands.cmdset import CmdSet
from django.conf import settings
from evennia.utils import utils
from random import choice

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class Gun(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.ammo = 0
        self.db.max_ammo = 8
        self.db.ammo_type = 'generic'
        self.ndb.aiming = False
        self.ndb.target = None
        self.cmdset.add_default(GunCmdSet, persistent=True)

    def on_hit_target(self, target, shooter, range=0, first=True):
        exits = [exi for exi in target.location.exits if exi.access(target, "traverse")]
        if exits:
            exit = choice(exits)
            dest = exit.destination

            if self.db.ammo_type == "rocket" and first:
                utils.delay(1,self.on_hit_target(target,shooter,range,first=False))
            target.msg("You are blasted to the %s!" % exit.name)
            target.location.msg_contents("%s is blown away to the %s!" % (target.name, exit.name),
                                         exclude=target)

            target.move_to(dest)

            target.location.msg_contents("%s comes flying in, propelled by an explosion from somewhere!" % (target.name),
                                         exclude=target)
            if target.db.stats:
                if 'deaths' in target.db.stats.keys():
                    target.db.stats['deaths'] += 1
            if shooter.db.stats:
                if 'kills' in shooter.db.stats.keys():
                    shooter.db.stats['kills'] += 1



class CmdGunAim(COMMAND_DEFAULT_CLASS):
    key = "aim"
    aliases = ["attack"]
    locks = "cmd:all()"

    def func(self):
        target = self.caller.search(self.args, quiet=True)
        if not target:
            exits = [exi for exi in self.caller.location.exits if exi.access(self.caller, "traverse")]
            if exits:
                for exit in exits:
                    for entry in exit.destination.contents:
                        if self.args in entry.name:
                            target = entry
                            self.obj.ndb.aiming = True
                            self.obj.ndb.target = target
                            self.caller.msg(
                                "You take aim at %s to the %s with %s." % (target.name, exit.name, self.obj.name))
                            self.caller.location.msg_contents(
                                "%s aims %s %s at %s." % (self.caller.name, exit.name, self.obj.name, target.name),
                                exclude=[self.caller, target])
                            target.msg("%s takes aim at you from afar with %s!" % (self.caller.name, self.obj.name))
        else:
            target = target[0]
            self.caller.msg("You take aim at %s with %s." % (target.name, self.obj.name))
            self.caller.location.msg_contents(
                "%s aims %s at %s." % (self.caller.name, self.obj.name, target.name),
                exclude=[self.caller,target])
            target.msg("%s aims %s at you!" % (self.caller.name, self.obj.name))
            self.obj.ndb.aiming = True
            self.obj.ndb.target = target

        if not target:
            self.caller.msg("You can't find it!")


class CmdGunShoot(COMMAND_DEFAULT_CLASS):
    key = "shoot"
    aliases = ["fire"]
    locks = "cmd:all()"

    def func(self):
        if not self.obj.ndb.aiming:
            self.caller.msg("You are not aiming at anything!")
        else:
            if (self.obj.db.ammo >= 1):
                target = self.caller.search(self.obj.ndb.target, quiet=True)

                if len(target) < 1:
                    exits = [exi for exi in self.caller.location.exits if exi.access(self.caller, "traverse")]
                    if exits:
                        for exit in exits:
                            for entry in exit.destination.contents:
                                if entry == self.obj.ndb.target:
                                    target = entry
                                    self.caller.msg(
                                        "You open fire to the %s at %s with %s!" % (exit, target.name, self.obj))
                                    self.caller.location.msg_contents(
                                        "%s opens fire from afar and hits %s with %s!" % (
                                            self.caller.name, target.name, self.obj.name),
                                        exclude=[self.caller, target])
                                    target.msg("%s opens fire at you from afar with %s!" % (self.caller, self.obj.name))
                                    self.obj.db.ammo -= 1
                                    self.obj.on_hit_target(target, self.caller, range=1)
                                    return
                else:
                    target = target[0]
                    self.caller.msg("You open fire at %s with %s at point blank range!" % (target.name, self.obj))
                    self.caller.location.msg_contents(
                        "%s opens fire at %s with %s from point blank range!" % (
                            self.caller.name, target.name, self.obj.name),
                        exclude=[self.caller, target])
                    target.msg("%s opens fire at you with %s from point blank range!" % (self.caller, self.obj.name))
                    self.obj.db.ammo -= 1
                    self.obj.on_hit_target(target, self.caller, range=0)
                    return

                self.caller.msg("You can't find your target!")

            else:
                self.caller.msg("%s is out of ammunition!" % self.obj.name)
                self.caller.location.msg_contents("Click! %s attempts to shoot %s but nothing happens." %
                                                  (self.caller.name, self.obj.name),
                                                  exclude=self.caller)


class CmdGunReload(COMMAND_DEFAULT_CLASS):
    key = "load"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Reload with what ammo?")
        else:
            target = self.caller.search(self.args)
            if not target:
                return
            if target.db.ammo_type == self.obj.db.ammo_type:
                self.obj.db.ammo += target.db.capacity
                if self.obj.db.ammo > self.obj.db.max_ammo:
                    self.obj.db.ammo = self.obj.db.max_ammo
                self.caller.msg("You load %s into %s." % (target.name, self.obj.name))
                self.caller.location.msg_contents(
                    "%s loads %s with %s." % (self.caller.name, self.obj.name, target.name),
                    exclude=self.caller)
                target.delete()
            else:
                self.caller.msg("It doesn't fit!")


class GunCmdSet(CmdSet):
    key = "GunCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdGunAim)
        self.add(CmdGunShoot)
        self.add(CmdGunReload)
