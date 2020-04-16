r"""
Evennia settings file.

The available options are found in the default settings file found
here:

/usr/src/evennia/evennia/settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "drastical"
GAME_SLOGAN = "I don't know what's going on, here..."

#CHANNEL_CONNECTINFO = {}
RSS_ENABLED = True
GRAPEVINE_ENABLED = True
IRC_ENABLED = True
IMC2_ENABLED = True

MULTISESSION_MODE = 0


TIME_FACTOR = 1.0
TIME_GAME_EPOCH = None
TIME_IGNORE_DOWNTIMES = True

ADMINS = ('elixx', 'elixx@drastical.net')

# Prod
WEBSOCKET_CLIENT_URL = "wss://mud.drastical.tech/ws"
trust_x_forwarded_for = 2
UPSTREAM_IPS = ["10.10.0.191"]
IDLE_TIMEOUT = 86400
IN_GAME_ERRORS = False
DEBUG = False

# Dev
# SERVER_LOG_DAY_ROTATION = 2
# SERVER_LOG_MAX_SIZE = 1000000
# PORTAL_LOG_DAY_ROTATION = 2
# PORTAL_LOG_MAX_SIZE = 1000000
# IDLE_TIMEOUT = -1
# IN_GAME_ERRORS = True
# DEBUG = True

#COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
