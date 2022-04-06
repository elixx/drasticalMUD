"""
File-based help entries. These complements command-based help and help entries
added in the database using the `sethelp` command in-game.

Control where Evennia reads these entries with `settings.FILE_HELP_ENTRY_MODULES`,
which is a list of python-paths to modules to read.

A module like this should hold a global `HELP_ENTRY_DICTS` list, containing
dicts that each represent a help entry. If no `HELP_ENTRY_DICTS` variable is
given, all top-level variables that are dicts in the module are read as help
entries.

Each dict is on the form
::

    {'key': <str>,
     'text': <str>}``     # the actual help text. Can contain # subtopic sections
     'category': <str>,   # optional, otherwise settings.DEFAULT_HELP_CATEGORY
     'aliases': <list>,   # optional
     'locks': <str>       # optional, 'view' controls seeing in help index, 'read'
                          #           if the entry can be read. If 'view' is unset,
                          #           'read' is used for the index. If unset, everyone
                          #           can read/view the entry.

"""

HELP_ENTRY_DICTS = [
    {
        "key": "drasticalMUD",
        "aliases": ["drastical", "dr"],
        "category": "General",
        "locks": "read:true",
        "text": """
            ** DrasticalMUD working docs **
            _this might be outdated by the time you find it_

            # subtopics

            ## Foraging

            Random items and resource bundles will spawn around the world. These can be collected, combined into other
            resources / items, or recycled for gold.
            
            ## Resources
            
            Gold is the form of currency. Resources types are Wood, Stone, and Trash. Other special resource types will 
            include gems and essences. 

            ## Property

            DrasticalMUD players can 'claim' ownership of almost any room in any area. Taking ownership costs 100 gold
            to start, but will increase each time it is claimed. With enough gold, any property can be taken from
            another player (although there will be additional ways to defend against this. Players will also be able to
            consensually trade land for other land, items, gold, etc.

            ### Movement

            A minor delay is incurred on moving from room-to-room, to lessen the impact of speedwalking. Special items and
            buffs can increases a player's movement speed.

            ### Farming
            
            On a claimed plot of land, tress and other plants can be planted from seeds. Over time, these will grow in size
            and be able to be harvested for resources. These will eventually be season dependant.

            ### Quality
            
            All items and bundles have an inherent 'quality' that provides a bonus percentage on rewards and production
            
            Quality Ranking
            0       trash
            9-45    poor
            45-60   average
            60-70   good
            70-80   great
            80-85   impressive
            85-95   exceptional   
            95-100  legendary
            
            
            ### Credits
            
            Credits go to:
             - Evennia - https://github.com/evennia/evennia/
             - Area_Reader - https://github.com/ctoth/area_reader
             - windows-95-ui-kit - https://github.com/themesberg/windows-95-ui-kit
             
             Public source is available at https://gitlab.drastical.net/elixx/drasticalmud

        """,
    },
]
