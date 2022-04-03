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

######################################################################
# Evennia base server config
######################################################################
from evennia.settings_default import *

from core.color_markups import color_markups

AREA_IMPORT_PATH = "C:\\_SRC\\drasticalMUD\\area_reader\\areas\\*.are"

COLOR_ANSI_EXTRA_MAP = color_markups.CURLY_COLOR_ANSI_EXTRA_MAP
COLOR_XTERM256_EXTRA_FG = color_markups.CURLY_COLOR_XTERM256_EXTRA_FG
COLOR_XTERM256_EXTRA_BG = color_markups.CURLY_COLOR_XTERM256_EXTRA_BG
COLOR_XTERM256_EXTRA_GFG = color_markups.CURLY_COLOR_XTERM256_EXTRA_GFG
COLOR_XTERM256_EXTRA_GBG = color_markups.CURLY_COLOR_XTERM256_EXTRA_GBG
COLOR_ANSI_BRIGHT_BG_EXTRA_MAP = color_markups.CURLY_COLOR_ANSI_BRIGHT_BG_EXTRA_MAP

RSS_ENABLED = True
IMC2_ENABLED = True

MULTISESSION_MODE = 0
#TIME_FACTOR = 1.0
TIME_FACTOR = 5
TIME_GAME_EPOCH = None
TIME_IGNORE_DOWNTIMES = True

MONTHS_PER_YEAR = 12
SEASONAL_BOUNDARIES = (3 / 12.0, 6 / 12.0, 9 / 12.0)
HOURS_PER_DAY = 24
DAY_BOUNDARIES = (0, 6 / 24.0, 12 / 24.0, 18 / 24.0)

ADMINS = ('elixx', 'elixx@drastical.net')

BASE_GUEST_TYPECLASS = "typeclasses.accounts.Guest"
BASE_OBJECT_TYPECLASS = "typeclasses.objects.Object"
COMMAND_DEFAULT_CLASS = "commands.muxcommand.MuxCommand"

GUEST_ENABLED = True
GUEST_COLORS = ['Amaranth','Amber','Amethyst','Apricot','Aquamarine','Azure','Baby','Beige','Black','Blue','Blush','Bronze','Brown','Burgundy','Byzantium','Carmine','Cerise','Cerulean','Champagne','Chartreuse','Chocolate','Cobalt','Coffee','Copper','Coral','Crimson','Cyan','Desert','Electric','Emerald','Erin','Gold','Gray','Green','Harlequin','Indigo','Ivory','Jade','Jungle','Lavender','Lemon','Lilac','Lime','Magenta','Magenta','Maroon','Mauve','Navy','Ochre','Olive','Orange','Orchid','Peach','Pear','Periwinkle','Persian','Pink','Plum','Prussian','Puce','Purple','Raspberry','Red','Rose','Ruby','Salmon','Sangria','Sapphire','Scarlet','Silver','Slate','Spring','Spring','Tan','Taupe','Teal','Turquoise','Ultramarine','Violet','Viridian','White','Yellow']
GUEST_LIST = [str(s) + "_Guest" for s in GUEST_COLORS ]

CMDSET_UNLOGGEDIN = "core.menu_login.UnloggedinCmdSet"


# # Dev
SERVERNAME = "devsandbox"
GAME_SLOGAN = "foo"*5
SERVER_LOG_DAY_ROTATION = 2
SERVER_LOG_MAX_SIZE = 1000000
PORTAL_LOG_DAY_ROTATION = 2
PORTAL_LOG_MAX_SIZE = 1000000
IDLE_TIMEOUT = -1
IN_GAME_ERRORS = True
DEBUG = True
GRAPEVINE_ENABLED = False
IRC_ENABLED = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
DRASTICAL_SEND_WEBHOOK = False
IRC_ENABLED = False

WEBCLIENT_OPTIONS = {
    "gagprompt": True,  # Gags prompt from the output window and keep them
    # together with the input bar
    "helppopup": True,  # Shows help files in a new popup window
    "notification_popup": True,  # Shows notifications of new messages as
    # popup windows
    "notification_sound": False  # Plays a sound for notifications of new
    # messages
}



######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
