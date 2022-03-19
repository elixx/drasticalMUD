"""
Channel

The channel class represents the out-of-character chat-room usable by
Accounts in-game. It is mostly overloaded to change its appearance, but
channels can be used to implement many different forms of message
distribution systems.

Note that sending data to channels are handled via the CMD_CHANNEL
syscommand (see evennia.syscmds). The sending should normally not need
to be modified.

"""

from evennia import DefaultChannel
from evennia.utils.logger import log_info

class Channel(DefaultChannel):
    """
    Working methods:
        at_channel_creation() - called once, when the channel is created
        has_connection(account) - check if the given account listens to this channel
        connect(account) - connect account to this channel
        disconnect(account) - disconnect account from channel
        access(access_obj, access_type='listen', default=False) - check the
                    access on this channel (default access_type is listen)
        delete() - delete this channel
        message_transform(msg, emit=False, prefix=True,
                          sender_strings=None, external=False) - called by
                          the comm system and triggers the hooks below
        msg(msgobj, header=None, senders=None, sender_strings=None,
            persistent=None, online=False, emit=False, external=False) - main
                send method, builds and sends a new message to channel.
        tempmsg(msg, header=None, senders=None) - wrapper for sending non-persistent
                messages.
        distribute_message(msg, online=False) - send a message to all
                connected accounts on channel, optionally sending only
                to accounts that are currently online (optimized for very large sends)

    Useful hooks:
        channel_prefix(msg, emit=False) - how the channel should be
                  prefixed when returning to user. Returns a string
        format_senders(senders) - should return how to display multiple
                senders to a channel
        pose_transform(msg, sender_string) - should detect if the
                sender is posing, and if so, modify the string
        format_external(msg, senders, emit=False) - format messages sent
                from outside the game, like from IRC
        format_message(msg, emit=False) - format the message body before
                displaying it to the user. 'emit' generally means that the
                message should not be displayed with the sender's name.

        pre_join_channel(joiner) - if returning False, abort join
        post_join_channel(joiner) - called right after successful join
        pre_leave_channel(leaver) - if returning False, abort leave
        post_leave_channel(leaver) - called right after successful leave
        pre_send_message(msg) - runs just before a message is sent to channel
        post_send_message(msg) - called just after message was sent to channel

    """

    def pose_transform(self, msgobj, sender_string, **kwargs):
        """
        Hook method. Detects if the sender is posing, and modifies the
        message accordingly.

        Args:
            msgobj (Msg or TempMsg): The message to analyze for a pose.
            sender_string (str): The name of the sender/poser.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            string (str): A message that combines the `sender_string`
                component with `msg` in different ways depending on if a
                pose was performed or not (this must be analyzed by the
                hook).

        """
        pose = False
        message = msgobj.message
        message_start = message.lstrip()
        if message_start.startswith((":", ";")):
            pose = True
            message = message[1:]
            if not message.startswith((":", "'", ",")):
                if not message.startswith(" "):
                    message = " " + message
        if pose:
            return "%s%s" % (sender_string, message)
        else:
            return "%s: %s" % (sender_string, message)


    def format_message(self, msgobj, emit=False, **kwargs):
        """
        Hook method. Formats a message body for display.

        Args:
            msgobj (Msg or TempMsg): The message object to send.
            emit (bool, optional): The message is agnostic of senders.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            transformed (str): The formatted message.

        """
        # We don't want to count things like external sources as senders for
        # the purpose of constructing the message string.
        senders = [sender for sender in msgobj.senders if hasattr(sender, "key")]
        if not senders:
            emit = True
        if emit:
            return msgobj.message
        else:
            senders = [sender.key for sender in msgobj.senders]
            senders = ", ".join(senders)
            if 'grapewinebot-gv' in senders:
                if ": " in msgobj.message:
                    senders = msgobj.message.split(":")[0]
                    senders = "{c" + senders + "{n"
                    msgobj.message = msgobj.message.split(":")[1][1:]
            else:
                senders = "{c" + senders + "{n"
            msgobj.message = "{y" + msgobj.message + "{n"
            return self.pose_transform(msgobj, senders)


    def format_external(self, msgobj, senders, emit=False, **kwargs):
        """
        Hook method. Used for formatting external messages. This is
        needed as a separate operation because the senders of external
        messages may not be in-game objects/accounts, and so cannot
        have things like custom user preferences.

        Args:
            msgobj (Msg or TempMsg): The message to send.
            senders (list): Strings, one per sender.
            emit (bool, optional): A sender-agnostic message or not.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            transformed (str): A formatted string.

        """
        if emit or not senders:
            return msgobj.message

        senders = ", ".join(senders)

        return self.pose_transform(msgobj, senders)