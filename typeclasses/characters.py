"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from string import capwords

from core.clothing import ClothedCharacter
from evennia import gametime
from evennia.utils.logger import log_err


class Character(ClothedCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    @property
    def gold(self):
        total = 0
        if self.db.stats is not None:
            if 'gold' in self.db.stats.keys():
                total += self.db.stats['gold']
        return total

    @gold.setter
    def gold(self, amount):
        if self.db.stats:
            self.db.stats['gold'] = amount
            # Invalidate gold-based leaderboards and toplist context
            try:
                from world.stats import invalidate_topGold_cache
                invalidate_topGold_cache()
            except Exception:
                pass

    def at_object_creation(self):
        super().at_object_creation()
        if self.db.stats is None:
            self.db.stats = {'gold': 0,
                             'logins': 0,
                             'visited': {},
                             'takeovers': 0,
                             'claims': 0,
                             'times_mined': 0,
                             'times_planted': 0,
                             'times_harvested': 0}

    def at_post_puppet(self):
        super().at_post_puppet()
        try:
            self.db.stats['logins'] += 1
        except KeyError:
            self.db.stats['logins'] = 1

    def at_post_unpuppet(self, account, session=None, **kwargs):
        if session is not None:
            start_time = gametime.datetime.fromtimestamp(session.conn_time)
            delta = gametime.datetime.now() - start_time
            if 'conn_time' in self.db.stats.keys():
                self.db.stats['conn_time'] += delta
            else:
                self.db.stats['conn_time'] = delta

    def at_pre_say(self, message, **kwargs):
        """
        Before the object says something.

        This hook is by default used by the 'say' and 'whisper'
        commands as used by this command it is called before the text
        is said/whispered and can be used to customize the outgoing
        text from the object. Returning `None` aborts the command.

        Args:
            message (str): The suggested say/whisper text spoken by self.
        Kwargs:
            whisper (bool): If True, this is a whisper rather than
                a say. This is sent by the whisper command by default.
                Other verbal commands could use this hook in similar
                ways.
            receivers (Object or iterable): If set, this is the target or targets for the say/whisper.

        Returns:
            message (str): The (possibly modified) text to be spoken.

        """
        styled_message = "|y" + message + "|n"
        return styled_message

    def at_pre_move(self, destination, **kwargs):
        """
        Called just before starting to move this object to
        destination.

        Args:
            destination (Object): The object we are moving to

        Returns:
            shouldmove (bool): If we should move or not.

        Notes:
            If this method returns False/None, the move is cancelled
            before it is even started.

        """
        if self.db.is_busy:
            if self.db.busy_doing:
                self.msg("You can't move until you stop %s." % self.db.busy_doing)
            else:
                self.msg("You are too busy!")
            return False
        else:
            return True

    def at_post_move(self, source_location, move_type=None, **kwargs):
        if source_location is not None:
            if source_location.tags.get(category='area'):
                source_area = source_location.tags.get(category='area')
            else:
                source_area = "unknown territory"

            if  self.location.tags.get(category='area'):
                cur_area = self.location.tags.get(category='area')
            else:
                cur_area = "unknown territory"

            if self.db.last_area:
                if cur_area != self.db.last_area:
                    self.msg("You have entered |Y%s|n." % capwords(cur_area))
                    self.db.last_area = cur_area
            else:
                self.db.last_area = source_area

            try:
                if 'visited' in self.db.stats.keys():
                    if cur_area not in self.db.stats['visited'].keys():
                        self.db.stats['visited'][cur_area] = [self.location.id]
                    else:
                        self.db.stats['visited'][cur_area].append(self.location.id)
                        self.db.stats['visited'][cur_area] = list(set(self.db.stats['visited'][cur_area]))
                else:
                    self.db.stats['visited'] = { cur_area: [self.location.id] }

                # Invalidate cached total_visited and toplist context so /toplist updates promptly
                try:
                    from world.stats import invalidate_total_visited_cache, invalidate_toplist_context
                    invalidate_total_visited_cache(self.id)
                    invalidate_toplist_context()
                except Exception:
                    pass

            except Exception as e:
                self.db.stats['visited'] = {}
                log_err("at_post_move:110: Resettings stats on %s:%s - %s" % (self.id, self.name, e))

        super().at_after_move(source_location)


    def at_look(self, target=None, session=None, **kwargs):
        if target is not None:
            if target.typeclass_path == "typeclasses.rooms.ImportedRoom":
                try:
                    target.update_description()
                except Exception as e:
                    log_err("characters:at_look():116: %s" % e)
                    pass
            if not target.access(self, "view"):
                try:
                    return "Could not view '%s'." % target.get_display_name(self, **kwargs)
                except AttributeError:
                    return "Could not view '%s'." % target.key
        description = target.return_appearance(self, **kwargs)
        target.at_desc(looker=self, **kwargs)

        return description


    def create_gold(self, amount):
        if amount <= self.gold:
            from evennia.utils.create import create_object
            from world.resource_types import SIZES
            newkey = "%s pile of gold" % SIZES(amount)

            ob = create_object(typeclass="typeclasses.resources.Resource",
                               key=newkey,
                               aliases=['gold','pile'],
                               location=self,
                               home=self,
                               attributes=[
                                   ('resources', {'gold': amount})
                               ])

            self.gold -= amount
            return ob
        else:
            return False