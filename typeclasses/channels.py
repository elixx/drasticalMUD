from evennia import DefaultChannel
class Channel(DefaultChannel):
    pass

## Deprecated:
#     def pose_transform(self, msgobj, sender_string, **kwargs):
#         pose = False
#         message = msgobj.message
#         message_start = message.lstrip()
#         if message_start.startswith((":", ";")):
#             pose = True
#             message = message[1:]
#             if not message.startswith((":", "'", ",")):
#                 if not message.startswith(" "):
#                     message = " " + message
#         if pose:
#             return "%s%s" % (sender_string, message)
#         else:
#             return "%s: %s" % (sender_string, message)
#
#
#     def format_message(self, msgobj, emit=False, **kwargs):
#         senders = [sender for sender in msgobj.senders if hasattr(sender, "key")]
#         if not senders:
#             emit = True
#         if emit:
#             return msgobj.message
#         else:
#             senders = [sender.key for sender in msgobj.senders]
#             senders = ", ".join(senders)
#             if 'grapewinebot-gv' in senders:
#                 if ":" in msgobj.message:
#                     senders = msgobj.message.split(":")[0]
#                     senders = "{C" + senders + "{n"
#                     msgobj.message = msgobj.message.split(":")[1][1:]
#             else:
#                 senders = "{c" + senders + "{n"
#             return self.pose_transform(msgobj, senders)
