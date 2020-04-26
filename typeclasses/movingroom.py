from evennia import TICKER_HANDLER
from typeclasses.exits import Exit
from evennia import search_object
from evennia.utils.create import create_object
from evennia import DefaultRoom

from random import choice

class MovingRoom(DefaultRoom):
    def at_object_creation(self):
        super().at_object_creation()

        self.create_exits()

        self.db.in_service = False
        self.db.in_station = True
        self.db.route = [ "#2", 30, "#214", 30 ]
        self.db.wait_at_destination = 60
        self.db.speed = 2

        self.db.current_pos = 0
        self.db.route_pos = 0
        self.db.next_dest = 1

        self.db.last_ticker_interval = None
        self.db.last_hook_key = None

        self.update_position()
        self.update_exits()

    def _set_ticker(self, interval, hook_key, stop=False):
        """
        Set how often the given hook key should
        be "ticked".

        Args:
            interval (int): The number of seconds
                between ticks
            hook_key (str): The name of the method
                (on this mob) to call every interval
                seconds.
            stop (bool, optional): Just stop the
                last ticker without starting a new one.
                With this set, the interval and hook_key
                arguments are unused.

        In order to only have one ticker
        running at a time, we make sure to store the
        previous ticker subscription so that we can
        easily find and stop it before setting a
        new one. The tickerhandler is persistent so
        we need to remember this across reloads.

        """
        idstring = "moving_room"
        last_interval = self.db.last_ticker_interval
        last_hook_key = self.db.last_hook_key
        if last_interval and last_hook_key:
            # we have a previous subscription, kill this first.
            TICKER_HANDLER.remove(
                interval=last_interval, callback=getattr(self, last_hook_key), idstring=idstring
            )
        self.db.last_ticker_interval = interval
        self.db.last_hook_key = hook_key
        if not stop:
            # set the new ticker
            TICKER_HANDLER.add(
                interval=interval, callback=getattr(self, hook_key), idstring=idstring
            )

    def create_exits(self):
        exitOut = create_object("typeclasses.movingroom.MovingExit",
                               key="out", location=self)
        self.db.exitOut = "#" + str(exitOut.id)

        exitIn = create_object("typeclasses.movingroom.MovingExit",
                               key="enter")
        self.db.exitIn = "#" + str(exitIn.id)

    def update_exits(self):
        if self.db.in_station:
            newloc = search_object( self.db.route[self.db.route_pos] )[0]

            exitIn = search_object(self.db.exitIn)[0]
            exitOut = search_object(self.db.exitOut)[0]
            exitOut.location = self
            exitOut.home = self

            exitIn.location = newloc
            exitIn.destination = self
            exitOut.location = self
            exitOut.destination = newloc
        else:
            exitIn = search_object(self.db.exitIn)[0]
            exitOut = search_object(self.db.exitOut)[0]
            exitIn.location = None
            exitOut.location = None

    def update_position(self):
        pass

    def start_service(self):
        self.db.in_service = True
        if self.db.in_station:
            self.db.in_station = False
            self.db.route_pos += 1
            self.msg_contents("The doors close as %s rumbles to life and begins to move." % self.name)
            self.update_exits()
        self._set_ticker(self.db.speed, "travel")

    def stop_service(self):
        if self.db.in_service:
            self.msg_contents("%s slows to a halt." % self.name)
            self.db.in_service = False
            self._set_ticker(None, None, stop=True)

    def travel(self):
        if self.db.in_service:
            self.db.current_pos += self.db.speed
            if self.db.current_pos >= self.db.route[self.db.route_pos]:
                self._set_ticker(None, None, stop=True)
                self.arrive()
            else:
                if(choice([True,False,False])):
                    self.msg_contents("%s shakes slightly as it moves along its course." % self.name)

            route = self.db.destinations

    def arrive(self):
        self.db.in_station = True
        self.db.route_pos += 1
        loc = search_object(self.db.route[self.db.route_pos])[0]
        self.msg_contents("%s announces, 'Now arriving at %s.'" % (self.name, loc.name))
        self.update_exits()
        self.msg_contents("%s glides to a halt and the doors open." % self.name)
        self._set_ticker(self.db.wait_at_destination, "start_service")

    def add_destination(self,dest,time_to_next,index=-1):
        if isinstance(dest,int):
            dest = "#" + str(dest)
        elif isinstance(dest,obj):
            dest = "#" + str(dest.id)
        try:
            loc = search_object(dest)[0]
        except:
            return None

        if index == -1:
            index = len(self.db.destinations)

        for i, (d, time) in enumerate(self.db.destinations):
            if d == loc.id:
                return self.db.destinations

        self.db.destinations.insert(index,(loc.id,time_to_next))
        self.msg_contents(self.name + " announces, '" + loc.name + " has been added to the route.'")
        return self.db.destinations


    def del_destination(self,dest):
        if isinstance(dest,int):
            dest = "#" + str(dest)
        elif isinstance(dest,obj):
            dest = "#" + str(dest.id)
        try:
            loc = search_object(dest)[0]
        except:
            return None

        for i, (d, time) in enumerate(self.db.destinations):
            if d == dest:
                del self.db.destinations[i]
                self.msg_contents(self.name + "announces, '" + loc.name + " has been removed from the route.'")
                return self.db.destinations



class MovingExit(Exit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_after_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """

    pass