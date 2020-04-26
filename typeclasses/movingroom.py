from evennia import TICKER_HANDLER
from typeclasses.exits import Exit
from evennia import search_object
from evennia.utils.create import create_object
from evennia import DefaultRoom



class MovingRoom(DefaultRoom):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.in_service = False
        self.db.broken = False
        self.db.in_station = False
        self.db.destinations = [("#2",20),
                                ("#214",60]

        self.db.current_pos = 0
        self.db.wait_at_destination = 60
        self.db.speed = 1

        self.db.last_ticker_interval = None
        self.db.last_hook_key = None

        self.create_exits()

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
        idstring = "moving_room_" + str(self.id)
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
        self.db.exitOut = exitOut.id

        exitIn = create_object("typeclasses.movingroom.MovingExit",
                               key="enter")
        self.db.exitIn = exitIn.id


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
            if d == dest
                del self.db.destinations[i]
                self.msg_contents(self.name + "announces, '" + loc.name + " has been removed from the route.'")
                return self.db.destinations


    def start_service(self):
        # current_pos 1000 = destinations[0], 2000 = destinations[2] , etc...
        self.db.in_service = True
        destinations = self.db.destinations
        last_dest = int( self.db.current_pos / 1000 )
        current_dist = int( self.db.current_pos % 1000 )
        next_dest = search_object(destinations[last_dest + 1])
        dist_to_go = destinations[last_dest][1] - current_dist
        if dist_to_go < 1:
            self.db.current_pos = next_dest

        self._set_ticker(self.db.speed, "travel")

    def stop_service(self):
        self.db.in_service = False
        self._set_ticker(None, None, stop=True)

    def travel(self):
        self.db.current_pos += self.db.speed
        last_dest = int( self.db.current_pos / 1000 )
        current_dist = int( self.db.current_pos % 1000 )


    def arrive(self):
        entrance = search_object(self.db.exitIn)[0]
        dest = self.db.destinations[ int( self.db.current_pos / 1000 ) + 1 ][0]
        current_loc = search_object(dest)[0]
        entrance.location = current_loc



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
