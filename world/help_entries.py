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
        "key": "drastical",
        "aliases": ["drasticalmud", "game", "intro", "dr"],
        "category": "General",
        "locks": "read:true",
        "text": """
        
            * DrasticalMUD working docs *
            
            _this might be outdated by the time you find it_

            # subtopics

            ## Foraging

            Random items and resource bundles will spawn around the world. These can be collected, combined into other
            resources / items, and / or recycled for gold.
                        
            ## Resources
            
            Gold is the form of currency. Resources types are Wood, Stone, and Trash. Other special resource types will 
            include gems and essences. Many items can be broken down for resources with a deconstructor.

            ## Property

            DrasticalMUD players can 'claim' ownership of almost any room in any area. Taking ownership costs 100 gold
            to start, but will increase each time it is claimed. With enough gold, any property can be taken from
            another player (although there will be additional ways to defend against this). Players will be able to build
            structures that inhibit the capture or traversal of their property. 
            Players will also be able to consensually trade land for other land, items, gold, etc.

            ## Movement

            A minor delay is incurred on moving from room-to-room to lessen the impact of speedwalking. Special items and
            buffs can increases a player's movement speed, providing an advantage in claiming or defending territory.

            ## Farming
            
            On a claimed plot of land, trees and other plants can be planted from seeds. Over time, these will grow in size
            and be able to be harvested for resources. These will eventually be season dependant. Fruit trees will produce
            fruit on a repeating basis, while more regular types of trees will be chopped down when harvested. The older a tree
            is, the more resources it produces, so rooms that have long-growing plants will be valuable!
            
            ## Mining
            
            There are entries to the mines spread out around the world. With a mining tool, one can mine for stone and other, 
            rarer gems by chipping away at the walls in the mines. As new ground is broken, the various mining entry-points
            can be connected, uncovering distant, unseen areas of the world.  Mining tools will wear out after some use,
            at which point will require either replacement or repair. Enhancements to mining equipment will also become
            available. 

            ## Quality
            
            All items and bundles have an inherent 'quality' that provides a bonus percentage on rewards and production.
            
            Quality Ranking
            ------- -------
            0       trash
            9-45    poor
            45-60   average
            60-70   good
            70-80   great
            80-85   impressive
            85-95   exceptional   
            95-100  legendary
                        
            ## Credits
            
            Credits go to the maintainers of and contributors to:
            
             - Evennia - https://github.com/evennia/evennia/
             - Area_Reader - https://github.com/ctoth/area_reader
             - Mud-Areas - https://github.com/vedicveko/Mud-Areas
             - windows-95-ui-kit - https://github.com/themesberg/windows-95-ui-kit
            
         The DrasticalMUD Public source is available at: https://gitlab.drastical.net/elixx/drasticalmud


        """,
    },
]
