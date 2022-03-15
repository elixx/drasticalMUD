from evennia import create_object, search_object
from evennia.utils.logger import log_info, log_err, log_warn
from . import area_reader

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
    def __init__(self, filename=False):
        self.rooms = {}
        self.room_translate = {}
        self.rooms_enumerated = False
        self.rooms_created = False
        self.exits_created = False

        self.objects = {}
        self.object_translate = {}
        self.objects_enumerated = False
        self.objects_created = False

        self.mobs = {}
        self.mob_translate = {}
        self.mobs_enumerated = False
        self.mobs_created = False

        self.object_location = {}
        self.mob_location = {}

        self.last_area = ""

        if (filename):
            self.load(filename)

    def load(self, filename):
        self.area_file = area_reader.RomAreaFile(filename)
        self.area_file.load_sections()
        self.areaname = self.area_file.area.name
        if self.areaname == "":
            s = filename.split("/")[-1].lower()
            s = s.replace(".are", "")
            s = s.replace("/", "")
            s = s.replace(".", "")
            self.areaname = s
        self.areaname = self.areaname.lower()
        self.areaname = self.areaname.replace("mud-areas\\", '')

        self.rooms_created = False
        self.rooms_enumerated = False
        self.exits_created = False
        self.objects_created = False
        self.objects_enumerated = False
        self.mobs_created = False
        self.mobs_enumerated = False

        self.enumerateRooms()
        self.enumerateObjects()
        self.enumerateObjectLocations()

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
                                  'area': areaname}
        self.rooms_enumerated = True

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
            self.objects[vnum] = {'name': name, 'desc': desc, 'ext': ext, 'type': itype, 'aliases': aliases,
                                  'area': areaname}
        self.objects_enumerated = True

    def enumerateObjectLocations(self):
        for r in self.area_file.area.resets:
            if r.command == 'O':
                try:
                    object = r.arg1
                    room = r.arg3
                    self.object_location[object] = room
                except Exception as e:
                    log_err(
                        "! enumerateObjectLocations(): " + str(e) + "\n\targ1=" + str(r.arg1) + " arg3=" + str(r.arg3))

    def spawnRooms(self):
        if self.rooms_created:
            log_err("! Rooms already created!")
        else:
            firstRoom = True
            for vnum, room in self.rooms.items():
                if (self.last_area != room['area']):
                    self.last_area = room['area']
                    firstRoom = True
                newroom = create_object(typeclass="typeclasses.rooms.LegacyRoom",
                                        key=room['name'])
                newroom.db.desc = room['desc']
                newroom.tags.add(room['area'], category='area')
                newroom.db.area = room['area']
                self.room_translate[vnum] = newroom.id
                # log_info(
                #     "spawnRooms(): Area:%s Room:'%s' Vnum:%s Evid:%s" % (room['area'], room['name'], vnum, newroom.id))
                if (firstRoom):
                    log_warn("* " + room['area'] + ': ' + str(newroom.id) + " = " + room['name'])
                    firstRoom = False
            self.rooms_created = True
            self._spawnRooms_exits()

    def _spawnRooms_exits(self):
        if self.exits_created:
            log_err("Exits already created!")
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
                    except Exception as e:
                        log_err('! spawnRooms_exits(): ' + room['area'] + ": Exit " + exitDir + " in EVid " + str(
                            evid) + " skipped " + str(exitData['dest']) + " not found." + str(e))
                        continue
            self.exits_created = True

    def spawnObjects(self):
        if self.objects_created:
            log_err("Objects already created!")
        else:
            log_info("spawning items")
            for vnum, ob in self.objects.items():
                if vnum not in self.object_location.keys():
                    log_err("! Object vnum not found in object_location table: %s" % vnum)
                    continue
                else:
                    evid = "#" + str(self.room_translate[self.object_location[vnum]])
                    try:
                        loc = search_object(evid)[0]
                    except Exception as e:
                        log_err("! spawnObjects(): location for object vnum %s not found: %s - %s" % (vnum, evid, e))
                        continue

                    try:
                        newob = create_object(key=ob['name'], location=loc, home=loc, aliases=ob['aliases'],
                                              typeclass="typeclasses.objects.LegacyObject",
                                              attributes=[('desc', ob['desc']),
                                                          ('ext_desc', ob['ext']),
                                                          ('type', ob['type']),
                                                          ('area', ob['area'])])
                        log_info("%s created in %s - #%s" % (ob['name'], loc.name, newob.id))
                    except Exception as e:
                        log_err("! Error creating %s, vnum: %s location: %s -- " + str(e) % (ob['name'], vnum, loc.id))
