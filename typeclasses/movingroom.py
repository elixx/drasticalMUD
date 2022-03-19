from evennia import utils
from evennia import TICKER_HANDLER
from typeclasses.exits import Exit
from evennia import search_object
from evennia.utils.create import create_object
from evennia import DefaultRoom
from typeclasses.objects import Object
from evennia.utils.evtable import EvTable

from random import choice


class MovingRoom(DefaultRoom):
    def at_object_creation(self):
        super().at_object_creation()

        if (self.db.exitIn) and (self.db.exitOut):
            self.exitIn = search_object(self.db.exitIn)[0]
            self.exitOut = search_object(self.db.exitOut)[0]
        else:
            self.create_exits()

        if not self.db.route:
            self.db.route = ["#2", 6, "#140", 6, "#1000", 10]
            self.db.wait_at_destination = 10
            self.db.speed = 2

        self.db.in_service = False
        self.db.in_station = True
        self.db.current_dist = 0
        self.db.route_pos = 0

        self.db.transit_msgs = ["%s shakes slightly as it moves along its course.",
                                "You feel the floor of %s moving beneath you.",
                                "%s hums quietly as it moves.",
                                "%s hits a bump and you are jostled, momentarily."]

        self.update_exits()

        utils.delay(self.db.wait_at_destination, self.start_service)
        self.db.last_hook_key = "start_service"

    def _set_ticker(self, interval, hook_key, stop=False):
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
        self.exitOut = create_object("typeclasses.movingroom.MovingExit",
                                     key="leave", location=self)
        self.db.exitOut = "#" + str(self.exitOut.id)

        self.exitIn = create_object("typeclasses.movingroom.MovingExit",
                                    key="board")
        self.db.exitIn = "#" + str(self.exitIn.id)

    def update_exits(self):
        if self.db.in_station:
            newloc = search_object(self.db.route[self.db.route_pos])[0]

            self.exitIn = search_object(self.db.exitIn)[0]
            self.exitOut = search_object(self.db.exitOut)[0]
            self.exitOut.location = self
            self.exitOut.home = self

            self.exitIn.location = newloc
            self.exitIn.destination = self
            self.exitOut.location = self
            self.exitOut.destination = newloc
        else:
            self.exitIn = search_object(self.db.exitIn)[0]
            self.exitOut = search_object(self.db.exitOut)[0]
            self.exitIn.location = None
            self.exitOut.location = None

    def start_service(self):
        del self.db.last_hook_key
        del self.db.last_ticker_interval
        self.db.in_service = True

        if self.db.in_station:
            self.db.in_station = False
            if self.db.route_pos + 1 > len(self.db.route) - 1:
                self.db.route_pos = 0
            else:
                self.db.route_pos += 1
            loc = search_object(self.db.route[self.db.route_pos - 1])[0]
            if len(self.db.route) - 1 > (self.db.route_pos + 1):
                next = search_object(self.db.route[self.db.route_pos + 1])[0]
            else:
                next = search_object(self.db.route[0])[0]
            if next.tags.get(category='area') != None:
                nextarea = next.tags.get(category='area')
                announce = "%s announces, '{xNext stop: {c%s{x in {y%s{x.{n'" % (
                self.name.capitalize(), next.name, nextarea.title())
            else:
                announce = "%s announces, '{xNext stop: {c%s{x.{n'" % (self.name.capitalize(), loc.name)
            self.db.desc = "An electronic sign reads:\n\t{yDeparting:\t{c%s{x\n\t{yNext Stop:\t{c%s{x" % (
            loc.name, next.name)
            self.msg_contents(announce)
            loc.msg_contents(announce)
            next.msg_contents("You hear %s approaching in the distance." % self.name)
            self.update_exits()
            self.msg_contents("The doors close as %s rumbles to life and begins to move." % self.name)
            loc.msg_contents("The doors close as %s begins picking up speed and pulls off." % self.name)
        self._set_ticker(self.db.speed, "travel")

    def stop_service(self):
        if self.db.in_service:
            self.msg_contents("%s slows to a halt." % self.name.capitalize())
            self.db.in_service = False
            self.db.desc = "An electronic sign reads:\n\t{rTemporarily out of service.{x"
            self._set_ticker(None, None, stop=True)

    def travel(self):
        if self.db.in_service:
            self.db.current_dist += self.db.speed
            if self.db.current_dist >= self.db.route[self.db.route_pos]:
                self._set_ticker(None, None, stop=True)
                self.arrive()
            else:
                if (choice([True, False, False])):
                    self.msg_contents(choice(self.db.transit_msgs) % self.name.capitalize())

            route = self.db.destinations

    def arrive(self):
        self.db.in_station = True
        if self.db.route_pos + 1 >= len(self.db.route) - 1:
            self.db.route_pos = 0
        else:
            self.db.route_pos += 1
        loc = search_object(self.db.route[self.db.route_pos])[0]
        if loc.tags.get(category='area') != None:
            area = loc.tags.get(category='area')
            announce = "%s announces, '{wWelcome to {y%s{w in {c%s{x.'" % (
            self.name.capitalize(), loc.name, area.title())
            # announce = "%s announces, '{xNow arriving at {c%s{x in {y%s{x.'" % (self.name, loc.name, area.title())
        else:
            announce = "%s announces, '{xNow arriving at {c%s{x.'" % (self.name.capitalize(), loc.name)
        self.msg_contents(announce)
        self.update_exits()
        self.msg_contents("%s glides to a halt and the doors open." % self.name.capitalize())
        loc.msg_contents("%s pulls up and slows to a halt. The doors open." % self.name.capitalize())
        self.db.current_dist = 0
        if self.db.route_pos < len(self.db.route) - 3:
            next = search_object(self.db.route[self.db.route_pos + 2])[0]
        else:
            next = search_object(self.db.route[0])[0]
        self.db.desc = "An electronic sign reads:\n\t{yCurrent Stop:\t{c%s{x\n\t{yNext:\t\t{c%s{x" % (
        loc.name, next.name)
        loc.msg_contents(announce)
        self._set_ticker(self.db.wait_at_destination, "start_service")

    def add_destination(self, dest, time_to_next=10, index=-1):
        try:
            loc = search_object(dest)[0]
        except:
            return None

        if index == -1:
            index = len(self.db.route)

        for i in self.db.route:
            if not isinstance(i, int):
                if i == dest:
                    return (self.db.routes)

        self.db.route.append(dest)
        self.db.route.append(time_to_next)

        self.msg_contents(self.name.capitalize() + " announces, '{c" + loc.name + "{x has been added to the route.'")
        return self.db.routes

    def del_destination(self, dest=None):
        if dest == None: dest = self.db.route[self.db.route_pos]
        try:
            loc = search_object(dest)[0]
        except:
            return None

        for i, d in enumerate(self.db.route):
            if d == dest:
                del self.db.route[i]
                self.msg_contents(
                    self.name.capitalize() + "announces, '{c" + loc.name + "{x has been removed from the route.'")
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



class RoomDisplayBoard(Object):
    def at_object_creation(self):
        self.locks.add("get:false()")
        self.location = None
        if not self.db.source:
            self.db.source = search_object("a", typeclass="typeclasses.movingroom.MovingRoom", exact=False)[0]
        self.route = self.db.source.db.route
        self.db.base_desc = "A board displaying the route for %s" % self.db.source.name
        self.db.desc = self._update_desc()

    def _update_desc(self):
        display = EvTable("|YStop", "|YArea", "|YTime")
        stop_name = None
        stop_time = None
        for stop in self.route:
            if isinstance(stop, str):
                s = search_object(stop)[0]
                stop_name = s.name
                area_name = s.tags.get(category='area')
            elif isinstance(stop, int):
                stop_time = stop
            if stop_name != None and stop_time != None:
                display.add_row(stop_name, area_name.title(), stop_time)
                stop_name = None
                stop_time = None
        output = self.db.base_desc + "\n" + str(display)
        return (output)

