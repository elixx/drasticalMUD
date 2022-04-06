"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

from random import shuffle, getrandbits
from time import time
from evennia.accounts.accounts import DefaultAccount, DefaultGuest
from evennia.utils import class_from_module, create, logger
from evennia.accounts.models import AccountDB
from django.conf import settings
from world.utils import findStatsMachine
from core import sendWebHook


class Account(DefaultAccount):
    """
    This class describes the actual OOC account (i.e. the user connecting
    to the MUD). It does NOT have visual appearance in the game world (that
    is handled by the character which is connected to this). Comm channels
    are attended/joined using this object.

    It can be useful e.g. for storing configuration options for your game, but
    should generally not hold any character-related info (that's best handled
    on the character level).

    Can be set using BASE_ACCOUNT_TYPECLASS.


    * available properties

     key (string) - name of account
     name (string)- wrapper for user.username
     aliases (list of strings) - aliases to the object. Will be saved to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     user (User, read-only) - django User authorization object
     obj (Object) - game object controlled by account. 'character' can also be used.
     sessions (list of Sessions) - sessions connected to this account
     is_superuser (bool, read-only) - if the connected user is a superuser

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create a database entry when storing data
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().

    * Helper methods

     msg(text=None, **kwargs)
     execute_cmd(raw_string, session=None)
     search(ostring, global_search=False, attribute_name=None, use_nicks=False, location=None, ignore_errors=False, account=False)
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hook methods (when re-implementation, remember methods need to have self as first arg)

     basetype_setup()
     at_account_creation()

     - note that the following hooks are also found on Objects and are
       usually handled on the character level:

     at_init()
     at_cmdset_get(**kwargs)
     at_first_login()
     at_post_login(session=None)
     at_disconnect()
     at_message_receive()
     at_message_send()
     at_server_reload()
     at_server_shutdown()

    """

    def at_post_login(self, session=None, **kwargs):
        super().at_post_login(session=session, **kwargs)
        do_not_exceed = 24  # Keep the last two dozen entries
        session = self.sessions.all()[-1]  # Most recent session
        if not self.db.lastsite:
            self.db.lastsite = []
        self.db.lastsite.insert(0, (session.address, int(time())))
        if len(self.db.lastsite) > do_not_exceed:
            self.db.lastsite.pop()

        machine = findStatsMachine()
        if "guest" not in str(session.account).lower():
            machine.incr_kv(str(session.account), "logins", db="userstats")

        sendWebHook("New logon: " + self.name + " from " + session.address)


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """

    @classmethod
    def authenticate(cls, **kwargs):
        """
        Gets or creates a Guest account object.

        Kwargs:
            ip (str, optional): IP address of requestor; used for ban checking,
                throttling and logging

        Returns:
            account (Object): Guest account object, if available
            errors (list): List of error messages accrued during this request.

        """
        errors = []
        account = None
        username = None
        ip = kwargs.get("ip", "").strip()

        # check if guests are enabled.
        if not settings.GUEST_ENABLED:
            errors.append("Guest accounts are not enabled on this server.")
            return None, errors

        try:
            GUEST_LIST = settings.GUEST_LIST
            shuffle(GUEST_LIST)
            # Find an available guest name.
            for name in GUEST_LIST:
                if not AccountDB.objects.filter(username__iexact=name).count():
                    username = name
                    break
            if not username:
                errors.append("All guest accounts are in use. Please try again later.")
                if ip:
                    LOGIN_THROTTLE.update(ip, "Too many requests for Guest access.")
                return None, errors
            else:
                # build a new account with the found guest username
                password = "%016x" % getrandbits(64)
                home = settings.GUEST_HOME
                permissions = settings.PERMISSION_GUEST_DEFAULT
                typeclass = settings.BASE_GUEST_TYPECLASS

                # Call parent class creator
                account, errs = super(DefaultGuest, cls).create(
                    guest=True,
                    username=username,
                    password=password,
                    permissions=permissions,
                    typeclass=typeclass,
                    home=home,
                    ip=ip,
                )
                errors.extend(errs)

                machine = findStatsMachine()
                machine.db.guestlog.insert(0, (int(time()), ip, username))
                if len(machine.db.guestlog) > 50:
                    machine.db.guestlog.pop()

                machine.incr_kv("*Guests", "logins", db="userstats")
                sendWebHook("Guest logon: " + username + " from " + ip)

                return account, errors

        except Exception as e:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't,
            # we won't see any errors at all.
            errors.append("An error occurred. Please e-mail an admin if the problem persists.")
            logger.log_trace()
            return None, errors

        return account, errors
