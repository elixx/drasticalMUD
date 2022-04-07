from random import shuffle, getrandbits
from time import time
from evennia.accounts.accounts import DefaultAccount, DefaultGuest
from evennia.utils import class_from_module, create, logger
from evennia.accounts.models import AccountDB
from django.conf import settings
from world.utils import findStatsMachine
from core import sendWebHook
import re


class Account(DefaultAccount):
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

    def at_pre_channel_msg(self, message, channel, senders=None, **kwargs):
        """
        Called by the Channel just before passing a message into `channel_msg`.
        This allows for tweak messages per-user and also to abort the
        receive on the receiver-level.

        Args:
            message (str): The message sent to the channel.
            channel (Channel): The sending channel.
            senders (list, optional): Accounts or Objects acting as senders.
                For most normal messages, there is only a single sender. If
                there are no senders, this may be a broadcasting message.
            **kwargs: These are additional keywords passed into `channel_msg`.
                If `no_prefix=True` or `emit=True` are passed, the channel
                prefix will not be added (`[channelname]: ` by default)

        Returns:
            str or None: Allows for customizing the message for this recipient.
                If returning `None` (or `False`) message-receiving is aborted.
                The returning string will be passed into `self.channel_msg`.

        Notes:
            This support posing/emotes by starting channel-send with : or ;.

        """
        if senders:
            if "grapewinebot" not in str(senders):
               sender_string = ", ".join(sender.get_display_name(self) for sender in senders)
            else:
                sender_string = "|C%s|n" % message.split(":")[0][:-1]
                message = message.split(":")[1][1:]

            message_lstrip = message.lstrip()
            if message_lstrip.startswith((":", ";")):
                # this is a pose, should show as e.g. "User1 smiles to channel"
                spacing = "" if message_lstrip[1:].startswith((":", "'", ",")) else " "
                message = f"{sender_string}{spacing}{message_lstrip[1:]}"
            else:
                # normal message
                message = f"{sender_string}: {message}"

        if not kwargs.get("no_prefix") or not kwargs.get("emit"):
            message = channel.channel_prefix() + message

        return message



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
