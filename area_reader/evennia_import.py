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

DIRALIAS = {"north": 'n',
            "south": 's',
            "east": 'e',
            "west": 'w',
            "up": 'u',
            "down": 'd',
            "northwest": 'nw',
            "southwest": 'sw',
            "northeast": 'ne',
            "southeast": 'se',
            "somewhere": 'xyzzy'}

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
        for vnum, room in self.area.items():
            newroom = create_object(typeclass="typeclasses.rooms.LegacyRoom",
                          key=room['name'])
            newroom.db.desc = room['desc']
            self.translate[vnum] = newroom.id
        self.spawnExits()

    def spawnExits(self):
        for vnum, room in self.area.items():
            for exitDir, exitData in room['exits'].items():
                evid = "#" + str(self.translate[vnum])
                try:
                    loc = search_object(evid)[0]
                except:
                    loc = search_object(room['name'])[0]

                try:
                    evdestid = "#" + str(self.translate[exitData['dest']])
                    dest = search_object(evdestid)[0]
                    newexit = create_object(typeclass="typeclasses.exits.LegacyExit",
                                            key=exitDir, location=loc, destination=dest)
                    newexit.aliases.add(DIRALIAS[exitDir])
                except:
                    print("Exit " + exitDir + " in " + str(evid) + " skipped - vloc " + str(exitData['dest']) + " not found.")
                    continue


