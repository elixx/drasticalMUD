"""
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
from evennia.contrib import color_markups
COLOR_ANSI_EXTRA_MAP = color_markups.CURLY_COLOR_ANSI_EXTRA_MAP
COLOR_XTERM256_EXTRA_FG = color_markups.CURLY_COLOR_XTERM256_EXTRA_FG
COLOR_XTERM256_EXTRA_BG = color_markups.CURLY_COLOR_XTERM256_EXTRA_BG
COLOR_XTERM256_EXTRA_GFG = color_markups.CURLY_COLOR_XTERM256_EXTRA_GFG
COLOR_XTERM256_EXTRA_GBG = color_markups.CURLY_COLOR_XTERM256_EXTRA_GBG
COLOR_ANSI_BRIGHT_BG_EXTRA_MAP = color_markups.CURLY_COLOR_ANSI_XTERM256_BRIGHT_BG_EXTRA_MAP

#CHANNEL_CONNECTINFO = {}
RSS_ENABLED = True
IMC2_ENABLED = True

MULTISESSION_MODE = 0
TIME_FACTOR = 1.0
TIME_GAME_EPOCH = None
TIME_IGNORE_DOWNTIMES = True

ADMINS = ('elixx', 'elixx@drastical.net')
GUEST_ENABLED = True

BASE_GUEST_TYPECLASS = "typeclasses.accounts.Guest"
BASE_OBJECT_TYPECLASS = "typeclasses.objects.Object"
COMMAND_DEFAULT_CLASS = "commands.muxcommand.MuxCommand"

GUEST_COLORS = ['Amaranth','Amber','Amethyst','Apricot','Aquamarine','Azure','Baby','Beige','Black','Blue','Blush','Bronze','Brown','Burgundy','Byzantium','Carmine','Cerise','Cerulean','Champagne','Chartreuse','Chocolate','Cobalt','Coffee','Copper','Coral','Crimson','Cyan','Desert','Electric','Emerald','Erin','Gold','Gray','Green','Harlequin','Indigo','Ivory','Jade','Jungle','Lavender','Lemon','Lilac','Lime','Magenta','Magenta','Maroon','Mauve','Navy','Ochre','Olive','Orange','Orchid','Peach','Pear','Periwinkle','Persian','Pink','Plum','Prussian','Puce','Purple','Raspberry','Red','Rose','Ruby','Salmon','Sangria','Sapphire','Scarlet','Silver','Slate','Spring','Spring','Tan','Taupe','Teal','Turquoise','Ultramarine','Violet','Viridian','White','Yellow']
GUEST_LIST = [str(s) + "_Guest" for s in GUEST_COLORS ]

# Prod
SERVERNAME = "drastical"
GAME_SLOGAN = "I don't know what's going on, here..."
WEBSOCKET_CLIENT_URL = "wss://mud.drastical.tech/ws"
trust_x_forwarded_for = 1
UPSTREAM_IPS = ["10.15.0.20"]
IDLE_TIMEOUT = 86400
IN_GAME_ERRORS = False
DEBUG = False
GRAPEVINE_ENABLED = True
STAFF_CONTACT_EMAIL = "elixx@drastical.net"
SESSION_COOKIE_AGE = 172800   # 86400=1d  # Default: 1209600 (2 weeks, in seconds)
SESSION_COOKIE_DOMAIN = "mud.drastical.tech"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# # Dev
# SERVERNAME = "[DEV] drastical"
# GAME_SLOGAN = "dev"*5
# SERVER_LOG_DAY_ROTATION = 2
# SERVER_LOG_MAX_SIZE = 1000000
# PORTAL_LOG_DAY_ROTATION = 2
# PORTAL_LOG_MAX_SIZE = 1000000
# IDLE_TIMEOUT = -1
# IN_GAME_ERRORS = True
# DEBUG = True
# GRAPEVINE_ENABLED = False
# IRC_ENABLED = False
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#DRASTICAL_NOTIFY_URL = "http://we-dont.41o.vpn:8065"
DRASTICAL_NOTIFY_URL = "http://10.10.0.190:8065"
DRASTICAL_NOTIFY_HOOK = "oobp9pmejb8y9qf37ocxexnu5w"



######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
