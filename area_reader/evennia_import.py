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
        self.area_file = area_reader.RomAreaFile(filename)
        self.area_file.load_sections()
        self.areaname = self.area_file.area.name
        if self.areaname == "":
            self.areaname = self.area_file.area.original_filename
        for i, v in self.area_file.area.rooms.items():
            name = v.name
            desc = v.description
            exits = {}
            for x in v.exits:
                exits[DIRS[x.door]] = {'desc': x.description,
                                       'dest': x.destination}

            self.area[v.vnum] = {'name': name,
                                 'desc': desc,
                                 'exits': exits}

        self.objects = {}
        for i in self.area_file.area.objects.keys():
            o = self.area_file.area.objects[i]
            vnum = o.vnum
            aliases = str(o.name).split(' ')
            name = o.short_desc
            desc = o.description
            ext = o.extra_descriptions
            itype = o.item_type
            self.objects[vnum] = {'name': name, 'desc': desc, 'ext': ext, 'type': itype, 'aliases': aliases}

    def spawnRooms(self):
        firstRoom = True
        for vnum, room in self.area.items():
            newroom = create_object(typeclass="typeclasses.rooms.LegacyRoom",
                          key=room['name'])
            newroom.db.desc = room['desc']
            newroom.tags.add(self.areaname, category='area')
            newroom.db.area = self.areaname
            self.translate[vnum] = newroom.id
            if(firstRoom):
                print(str(newroom.id) + " = " + room['name'])
                firstRoom = False
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
                    newexit.tags.add(self.areaname, category='area')
                    newexit.db.area = self.areaname
                except:
                    print("Exit " + exitDir + " in " + str(evid) + " skipped - vloc " + str(exitData['dest']) + " not found.")
                    continue

    def spawnTranslation(self):
        self.object_location = {}
        for r in self.area_file.area.resets:
            if r.command == 'O':
                try:
                    self.object_location[r.arg1] = self.translate[r.arg3]
                except Exception as e:
                    print(str(e) + "arg1=" + str(r.arg1) + " arg3=" + str(r.arg3))

    def spawnItems(self):
        print("spawning items")
        for vnum,ob in self.objects.items():
            try:
                evloc = "#" + str(self.object_location[vnum])
            except Exception as e:
                print("vnum not in translation: #" + str(vnum) + str(e))

            try:
                loc = search_object(evloc)[0]
            except:
                loc = None
            newob = create_object(key=ob['name'], location=loc, home=loc, aliases=ob['aliases'],
                                  attributes=[('desc', ob['desc']),
                                              ('ext_desc', ob['ext']),
                                              ('type', ob['type'])])
            self.translate[vnum] = newob.id



