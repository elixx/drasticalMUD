from evennia import create_object, search_object
from area_reader import area_reader

DIRS = {0: "north",
        1: "east",
        2: "south",
        3: "west",
        4: "up",
        5: "down",
        6: "northeast",
        7: "northwest",
        8: "southeast",
        9: "southwest",
        10: "somewhere"}


class AreaImporter(object):
    def __init__(self, filename):
        self.area = {}
        self.translate = {}
        area_file = area_reader.RomAreaFile(filename)
        area_file.load_sections()
        for i, v in area_file.area.rooms.items():
            name = v.name
            desc = v.description
            exits = {}
            for x in v.exits:
                exits[DIRS[x.door]] = {'desc': x.description,
                                       'dest': x.destination}

            self.area[v.vnum] = {'name': name,
                                 'desc': desc,
                                 'exits': exits}

    def spawnRooms(self):
        for vnum, room in enumerate(self.area):
            newroom = create_object(typeclass="typeclasses.rooms.LegacyRoom",
                          key=room['name'])
            newroom.db.desc = room['desc']
            self.translate[vnum] = newroom.id

    def spawnExits(selfs):
        for vnum, room in enumerate(self.area):
            for dir, exit in room['exits'].items():
                evid = self.translate[vnum]
                try:
                    loc = search_object(evid)[0]
                except:
                    raise
                try:
                    dest = search_object(self.translate[exit['destination']])[0]
                except:
                    raise
                newexit = create_object(typeclass="typeclasses.exits.LegacyExit",
                                        key=dir, location=loc, destination=dest)

