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
        self.areaname = self.area_file.area.name.lower()
        if self.areaname == "" or (".are" in self.areaname):
            if "\\" in filename:
                s = filename.split("\\")[-1].lower()
            else:
                s = filename.split("/")[-1].lower()
            s = s.replace(".are", "")
            s = s.replace("/", "")
            s = s.replace("\\", "")
            s = s.replace(".", "")
            self.areaname = s

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
        count = 0
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
            count += 1
        log_info("enumerateRooms(): %s rooms" % count)
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
            entries = {}
            count = 0
            for vnum in sorted(self.rooms):
                room = self.rooms[vnum]
                if (self.last_area != room['area']):
                    self.last_area = room['area']
                    firstRoom = True
                newroom = create_object(typeclass="typeclasses.rooms.ImportedRoom",
                                        key=room['name'],locks="puppet:false()")
                newroom.db.desc = room['desc']
                newroom.tags.add(room['area'], category='area')
                newroom.tags.add(room['area'], category='room')
                newroom.tags.add('imported', category='room')
                newroom.db.area = room['area']
                self.room_translate[vnum] = newroom.id
                # log_info(
                #     "spawnRooms(): Area:%s Room:'%s' Vnum:%s Evid:%s" % (room['area'], room['name'], vnum, newroom.id))
                if (firstRoom):
                    log_warn("* Entry to "+ room['area'] + ' - #' + str(newroom.id) + " = " + room['name'])
                    if room['area'] in entries.keys():
                        entries[room['area']].append(newroom.id)
                    else:
                        entries[room['area']] = [newroom.id]
                    firstRoom = False
                count += 1
            self.rooms_created = True
            log_info("%s rooms created." % count)
            self._spawnRooms_exits()
            return(entries)

    def _spawnRooms_exits(self):
        if self.exits_created:
            log_err("Exits already created!")
        else:
            for vnum in sorted(self.rooms):
                room = self.rooms[vnum]
                for exitDir, exitData in room['exits'].items():
                    evid = "#" + str(self.room_translate[vnum])
                    loc = search_object(evid)[0]
                    if loc is None:
                        loc = search_object(room['name'])[0]
                        if loc is None:
                            log_err('! missing source: ' + str(loc))
                            continue
                    evdestid = "#" + str(self.room_translate[exitData['dest']])
                    dest = search_object(evdestid)[0]
                    if dest is None:
                        log_err('! deadend: ' + room['area'] + ": Exit " + exitDir + " in EVid " + str(evid) + " skipped " + str(exitData['dest']) + " not found.")
                        continue
                    newexit = create_object(typeclass="typeclasses.exits.LegacyExit",
                                            key=exitDir, location=loc, destination=dest)
                    newexit.aliases.add(DIRALIAS[exitDir])
                    newexit.tags.add(room['area'], category='area')
                    newexit.tags.add('imported', category='exit')
                    newexit.db.area = room['area']
            self.exits_created = True

    def spawnObjects(self):
        if self.objects_created:
            log_err("Objects already created!")
        else:
            log_info("spawning items")
            for vnum in sorted(self.objects):
                ob = self.objects[vnum]
                if vnum not in self.object_location.keys():
                    #log_err("! %s - vnum not found in object_location table: %s" % (ob.name, vnum))
                    continue
                else:
                    evid = "#" + str(self.room_translate[self.object_location[vnum]])
                    try:
                        loc = search_object(evid)[0]
                    except Exception as e:
                        log_err("! spawnObjects(): vnum %s - location %s not found - %s" % (vnum, evid, e))
                        continue

                    try:
                        newob = create_object(key=ob['name'], location=loc, home=loc, aliases=ob['aliases'],
                                              typeclass="typeclasses.objects.LegacyObject",
                                              attributes=[('desc', ob['desc']),
                                                          ('ext_desc', ob['ext']),
                                                          ('type', ob['type']),
                                                          ('area', ob['area'])])
                        newob.tags.add('imported', category='object')
                        #log_info("%s created in %s - #%s" % (ob['name'], loc.name, newob.id))
                    except Exception as e:
                        log_err("! Error creating object %s, vnum: %s location: %s -- " + str(e) % (ob['name'], vnum, loc.id))
