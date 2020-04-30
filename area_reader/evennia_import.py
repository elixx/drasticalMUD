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
        self.rooms = {}
        self.room_translate = {}
        self.rooms_created = False
        self.exits_created = False
        self.objects = {}
        self.object_translate = {}
        self.objects_created = False
        self.mobs = {}
        self.mob_translate = {}
        self.mobs_created = False

        self.object_location = {}
        self.mob_location = {}

        self.load(filename)

    def load(self, filename):
        self.area_file = area_reader.RomAreaFile(filename)
        self.area_file.load_sections()
        self.areaname = self.area_file.area.name
        if self.areaname == "":
            self.areaname = self.area_file.area.original_filename
        self.rooms_created = False
        self.exits_created = False
        self.objects_created = False
        self.mobs_created = False

    def enumerateRooms(self):
        areaname = self.areaname
        for i, v in self.area_file.area.rooms.items():
            name = v.name
            desc = v.description
            exits = {}
            for x in v.exits:
                exits[DIRS[x.door]] = {'desc': x.description,
                                       'dest': x.destination}

            self.rooms[v.vnum] = {'name': name,
                                 'desc': desc,
                                 'exits': exits,
                                 'area': areaname }

    def enumerateObjects(self):
        areaname = self.areaname
        for i in self.area_file.area.objects.keys():
            o = self.area_file.area.objects[i]
            vnum = o.vnum
            aliases = str(o.name).split(' ')
            name = o.short_desc
            desc = o.description
            ext = o.extra_descriptions
            itype = o.item_type
            self.objects[vnum] = {'name': name, 'desc': desc, 'ext': ext, 'type': itype, 'aliases': aliases, 'area': areaname }

    def spawnRooms(self):
        if self.rooms_created:
            print("Rooms already created!")
        else:
            firstRoom = True
            for vnum, room in self.rooms.items():
                newroom = create_object(typeclass="typeclasses.rooms.LegacyRoom",
                                        key=room['name'])
                newroom.db.desc = room['desc']
                newroom.tags.add(room['area'], category='area')
                newroom.db.area = room['area']
                self.room_translate[vnum] = newroom.id
                if(firstRoom):
                    print(str(newroom.id) + " = " + room['name'])
                    firstRoom = False
            self.rooms_created = True
            self._spawnRooms_exits()

    def _spawnRooms_exits(self):
        if self.exits_created:
            print("Exits already created!")
        else:
            for vnum, room in self.rooms.items():
                for exitDir, exitData in room['exits'].items():
                    evid = "#" + str(self.room_translate[vnum])
                    try:
                        loc = search_object(evid)[0]
                    except:
                        loc = search_object(room['name'])[0]

                    try:
                        evdestid = "#" + str(self.room_translate[exitData['dest']])
                        dest = search_object(evdestid)[0]
                        newexit = create_object(typeclass="typeclasses.exits.LegacyExit",
                                                key=exitDir, location=loc, destination=dest)
                        newexit.aliases.add(DIRALIAS[exitDir])
                        newexit.tags.add(room['area'], category='area')
                        newexit.db.area = room['area']
                    except:
                        print("Exit " + exitDir + " in " + str(evid) + " skipped - vloc " + str(exitData['dest']) + " not found.")
                        continue
            self.exits_created = True

    def enumerateObjectLocations(self):
        if self.rooms_created:
            for r in self.area_file.area.resets:
                if r.command == 'O':
                    try:
                        self.object_location[r.arg1] = self.room_translate[r.arg3]
                    except Exception as e:
                        print("spawnTranslation: " + str(e) + " arg1=" + str(r.arg1) + " arg3=" + str(r.arg3))
        else:
            print("Rooms not created, can't create object-location table yet.")

    def spawnObjects(self):
        print("spawning items")
        for vnum, ob in self.objects.items():
            if vnum not in self.object_location.keys():
                pass
            else:
                evid = "#" + str(self.object_location[vnum])
                try:
                    loc = search_object(evid)[0]
                except Exception as e:
                    print("location for object %s not found: %s" % (vnum, evid))
                    print(str(e))
                    break

                try:
                    newob = create_object(key=ob['name'], location=loc, home=loc, aliases=ob['aliases'],
                                          attributes=[('desc', ob['desc']),
                                                      ('ext_desc', ob['ext']),
                                                      ('type', ob['type']),
                                                      ('area', ob['area'])])
                    print("%s created in %s - #%s" % (ob['name'], loc.name, newob.id))
                except Exception as e:
                    print("Error creating %s, vnum: %s location: %s" % (ob['name'],vnum,loc.name))

