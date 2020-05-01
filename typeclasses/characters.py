"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia.contrib.clothing import ClothedCharacter


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
    def at_object_creation(self):
        super().at_object_creation()
        if self.db.stats == None:
            self.db.stats = {'kills': 0, 'deaths': 0, 'logins': 0, 'visited': []}

    def at_post_puppet(self):
        super().at_post_puppet()
        try:
            self.db.stats['logins'] += 1
        except KeyError:
            self.db.stats['logins'] = 1

    # def at_before_say(self, message, **kwargs):
    #     """
    #     Before the object says something.
    #
    #     This hook is by default used by the 'say' and 'whisper'
    #     commands as used by this command it is called before the text
    #     is said/whispered and can be used to customize the outgoing
    #     text from the object. Returning `None` aborts the command.
    #
    #     Args:
    #         message (str): The suggested say/whisper text spoken by self.
    #     Kwargs:
    #         whisper (bool): If True, this is a whisper rather than
    #             a say. This is sent by the whisper command by default.
    #             Other verbal commands could use this hook in similar
    #             ways.
    #         receivers (Object or iterable): If set, this is the target or targets for the say/whisper.
    #
    #     Returns:
    #         message (str): The (possibly modified) text to be spoken.
    #
    #     """
    #     styled_message = "|y" + message + "|n"
    #     return styled_message

    def at_after_move(self, source_location):
        try:
            if source_location and source_location.id not in self.db.stats['visited']:
                self.db.stats['visited'].append(source_location.id)

        except KeyError:
            self.db.stats['visited'] = []

        if source_location is not None:
            if source_location.db.area:
                area_name = str(source_location.db.area)
            else:
                area_name = "unknown territory"

            if self.db.last_area:
                if self.db.last_area != area_name:
                    self.msg("You have entered {y%s{n." % area_name.title())
                    self.db.last_area = area_name
            else:
                self.db.last_area = area_name

        super().at_after_move(source_location)
