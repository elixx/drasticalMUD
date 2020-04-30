# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function `connection_screen()`, taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from django.conf import settings
from evennia import utils

CONNECTION_SCREEN = """
|B==============================================================|n
 Welcome to |g{}|n !
 {}
|x                                                           _..._                   
|x_______                                                 .-'_..._''.           .---.
|x\\  ___ `'.                                      .--.  .' .'      '.\\          ||   ||
|w ' ||--.\\  \\                                     ||__|| / .'                     ||   ||
|w || ||  |x  \\  ' .-,.--.      |w                  .||  .--.. '        |x               ||   ||
|w || ||   |x  ||  '||  .-. || |w  __                .' ||_ ||  |||| || |x                __    ||   ||
|w || ||   |x  ||  |||| ||  || |w||.:--.'.     _____  .'     ||||  |||| ||    |x          .:--.'.  ||   ||
|W || ||     ' .'|| ||  || / ||   \\ ||  /'     \\'--.  .-'||  ||. '             / ||   \\ || ||   ||
|W || ||___.' /' || ||  '-`" __ || || (    __,'   ||  ||  ||  || \\ '.          .`" __ || || ||   ||
|w/_______.'/  || ||     .'.''|| || ,`\\_______  ||  ||  ||__||  '. `._____.-'/ .'.''|| || ||   ||
|x\\_______||/   | ||    / /   || ||_; _____   \\ ||  '.'        `-.______ / / /   || ||_'---'
|x             ||_||    \\ \\._,\\ '/'         / ||   /                  `  \\ \\._,\\ '/     
|x                     `--'  `"  \\_______/' `'-'                       `--'  `"      |x

 
 If you have an existing account, connect to it by typing:
      |wconnect <username> <password>|x
 If you need to create an account, type (without the <>'s):
      |wcreate <username> <password>|x
 You can also log in to just look around:
      |wconnect guest|x

 If you have spaces in your username, enclose it in quotes.
 Enter |whelp|x for more info. |wlook|x will re-show this screen.
|B==============================================================|n""".format(
    settings.SERVERNAME, settings.GAME_SLOGAN)

CONNECTION_SCREEN = """
 Welcome to...

|n▓█████▄  ██▀███   ▄▄▄        ██████ ▄▄▄█████▓ ██▓ ▄████▄   ▄▄▄       ██▓    
|x▒██▀ ██▌▓██ ▒ ██▒▒████▄    ▒██    ▒ ▓  ██▒ ▓▒▓██▒▒██▀ ▀█  ▒████▄    ▓██▒    
|r░██   █▌|R▓|r██ ░▄|R█|r ▒|R▒|r██  ▀█▄  ░ |R▓██|r▄   ▒ ▓|R██|r░ ▒░▒|R█|r█▒▒▓█    ▄ ▒|R█|r█  ▀█▄  ▒██░    
|r░▓█▄  |R ▌▒██|r▀|R▀█▄ |r ░██▄▄|R▄▄██ |r  ▒   ██|R▒░ ▓██|r▓ ░ ░██░|R▒▓▓▄|r ▄██▒░█|R█▄▄▄|r▄██ ▒██░    
|R░▒████▓ ░██▓ ▒██▒ ▓█   ▓██▒▒██████▒▒  ▒██▒ ░ ░██░▒ ▓███▀ ░ ▓█   ▓██▒░██████▒
|R ▒▒▓  ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░  ▒ ░░   ░▓  ░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░▓  ░
|R ░ ▒  ▒   ░▒ ░ ▒░  ▒   ▒▒ ░░ ░▒  ░ ░    ░     ▒ ░  ░  ▒     ▒   ▒▒ ░░ ░ ▒  ░
|R ░ ░  ░   ░░   ░   ░   ▒   ░  ░  ░    ░       ▒ ░░          ░   ▒     ░ ░   
|R   ░       ░           ░  ░      ░            ░  ░ ░            ░  ░    ░  ░
|R ░             
|R                                   ░                          
{} - |g{}|n 
 If you have an existing account, connect to it by typing:
      |wconnect <username> <password>|x
 If you need to create an account, type (without the <>'s):
      |wcreate <username> <password>|x
 You can also log in to just look around:
      |wconnect guest|x

 If you have spaces in your username, enclose it in quotes.
 Enter |whelp|x for more info. |wlook|x will re-show this screen.\n
""".format(settings.SERVERNAME, settings.GAME_SLOGAN)