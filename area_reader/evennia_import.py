from evennia.utils.create import create_object
from evennia.utils.search import search_object
from evennia.utils.logger import log_info, log_err, log_warn
from . import area_reader

ROOM_TYPECLASS = "typeclasses.rooms.ImportedRoom"
EXIT_TYPECLASS = "typeclasses.exits.LegacyExit"
ITEM_TYPECLASS = "typeclasses.objects.Item"
MOB_TYPECLASS = "typeclasses.mob.LegacyMob"

AREA_TRANSLATIONS = {"pawmist": "twilight city of pawmist",
                     "erealms": "elven realms",
                     "shadval150": "kandahar shadow valley",
                     "shadval45": "shadow valley",
                     "sdearth": "south dearthwood",
                     "edearth": "east dearthwood",
                     "wdearth": "west dearthwood",
                     "avalonch": "avalon",
                     "talonvle": "gilda and the dragon",
                     "takshrin": "shrine of tahkien",
                     "dawn": "city of dawn",
                     "tisland": "treasure island",
                     "amazon": "the amazon jungle",
                     "partbody": "body parts castle",
                     "north": "northern road",
                     'river': 'durgas river',
                     'island': 'island of illusion',
                     'east': 'eastern road',
                     'demise': 'death room',
                     'path': 'the hidden path',
                     'gstrong': 'goblin stronghold',
                     'plains': 'plains of the north',
                     'pyramid': 'the great pyramid',
                     'weaverei': 'the dreamweaver\'s path',
                     'marsh': 'generic old marsh',
                     'tree': 'yggdrasil',
                     'zoology': 'mudschool fieldtrip',
                     'dock': 'calinth docks',
                     'water': 'blizzard water nymphs',
                     'chessbrd': 'chessboard',
                     'drmscp': 'dreamscape',
                     'under2': 'underdark',
                     'newbie2': 'newbie zone'}

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

FIX_DOUBLESPACE = ["the bazaar", "sesame street"]


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

        if self.areaname.lower() in AREA_TRANSLATIONS.keys():
            self.areaname = AREA_TRANSLATIONS[self.areaname]

        self.rooms_created = False
        self.rooms_enumerated = False
        self.exits_created = False
        self.objects_created = False
        self.objects_enumerated = False
        self.mobs_created = False
        self.mobs_enumerated = False

        self.enumerateRooms()
        self.enumerateMobs()
        self.enumerateMobLocations()
        self.enumerateObjects()
        self.enumerateObjectLocations()

        self.entries = {}

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

    def enumerateMobs(self):
        areaname = self.areaname
        for i in self.area_file.area.mobs.keys():
            m = self.area_file.area.mobs[i]
            vnum = m.vnum
            name = m.short_desc.replace("{","|")
            aliases = str(name).replace("|","").split(' ')
            desc = m.description if areaname not in FIX_DOUBLESPACE else m.description.replace("\n\n", "\n")
            ext = m.long_desc.replace("{","|")
            size = m.size
            alignment = m.alignment
            race = m.race

            self.mobs[vnum] = {'name': name,
                               'desc': desc,
                               'ext': ext,
                               'race': race,
                               'size': size,
                               'alignment': alignment,
                               'aliases': aliases,
                               'area': areaname}
        self.mobs_enumerated = True

    def enumerateMobLocations(self):
        for r in self.area_file.area.resets:
            if r.command == 'M':
                try:
                    mob = r.arg1
                    room = r.arg3
                    self.mob_location[mob] = room
                except Exception as e:
                    log_err(
                        "! enumerateMobLocations(): " + str(e) + "\n\targ1=" + str(r.arg1) + " arg3=" + str(r.arg3))

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
            # O - Object into room
            # P - Object into object
            # E - Object into mob
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
            entries = []
            firstRoom = True
            count = 0
            for vnum in sorted(self.rooms):
                room = self.rooms[vnum]
                if (self.last_area != room['area']):
                    self.last_area = room['area']
                    firstRoom = True
                newroom = create_object(typeclass=ROOM_TYPECLASS,
                                        key=room['name'].replace("{","|"),
                                        locks=['puppet:false()', 'get:false()'],
                                        attributes=[('desc', room['desc'].replace("{","|")),
                                                    ('vnum', vnum),
                                                    ('value', 100),
                                                    ('area', room['area'])],
                                        tags=[(room['area'], 'area'),
                                              (room['area'], 'room'),
                                              ('imported'),
                                              ('random_spawn', 'room'),
                                              ('random_growth', 'room')])

                self.room_translate[vnum] = newroom.id
                # log_info(
                #     "spawnRooms(): Area:%s Room:'%s' Vnum:%s Evid:%s" % (room['area'], room['name'], vnum, newroom.id))
                if (firstRoom):
                    log_warn("* Entry to " + room['area'] + ' - #' + str(newroom.id) + " = " + room['name'])
                    if room['area'] in self.entries.keys():
                        self.entries[room['area']].append(newroom.id)
                    else:
                        entries.append(newroom.dbref)
                        self.entries[room['area']] = [newroom.id]
                    firstRoom = False
                count += 1
            self.rooms_created = True
            log_info("%s rooms created." % count)
            self._spawnRooms_exits()
        return entries

    def _spawnRooms_exits(self):
        if self.exits_created:
            log_err("Exits already created!")
        else:
            for vnum in sorted(self.rooms):
                room = self.rooms[vnum]
                count = 0
                for exitDir, exitData in room['exits'].items():
                    evid = "#" + str(self.room_translate[vnum])
                    loc = search_object(evid, use_dbref=True)[0]
                    if loc is None:
                        loc = search_object(room['name'])[0]
                        if loc is None:
                            log_err('! missing source: ' + str(loc))
                            continue
                    if exitData['dest'] not in self.room_translate.keys():
                        log_err('! no source: ' + room['area'] + ": Exit " + exitDir + " in EVid " + str(
                            evid) + " skipped, " + str(exitData['dest']) + " not found.")
                        continue
                    evdestid = "#" + str(self.room_translate[exitData['dest']])
                    dest = search_object(evdestid, use_dbref=True)[0]
                    if dest is None:
                        log_err('! no destination: ' + room['area'] + ": Exit " + exitDir + " in EVid " + str(
                            evid) + " skipped, " + str(exitData['dest']) + " not found.")
                        continue
                    create_object(typeclass=EXIT_TYPECLASS,
                                  key=exitDir, location=loc, destination=dest, aliases=[DIRALIAS[exitDir]],
                                  tags=[(room['area'], 'area'),
                                        (room['area'], 'exit'),
                                        ('imported')],
                                  locks=['puppet:false()', 'get:false()'],
                                  attributes=[('area', room['area']),
                                              ('vnum', vnum)])
                    count += 1
                if count == 0:
                    log_err("! blackhole detected - vnum %s, EvId %s" % (vnum, self.room_translate[vnum]))
                    # TODO: check IDs listed in self.entries and remove if present
            self.exits_created = True

    def spawnMobs(self):
        if self.mobs_created:
            log_err("Mobs already created!")
        else:
            for vnum in sorted(self.mobs):
                if vnum not in self.mobs.keys():
                    log_err("spawnMobs():300: %s not found" % vnum)
                    continue
                ob = self.mobs[vnum]
                if vnum not in self.mob_location.keys():
                    # mob location could not be found
                    log_err("! %s - vnum not found in mob_location: %s" % (ob['name'], vnum))
                    continue

                if self.mob_location[vnum] not in self.room_translate.keys():
                    log_err("! %s - vnum not found in room_translate: %s" % (ob['name'], vnum))
                    continue

                evid = "#" + str(self.room_translate[self.mob_location[vnum]])
                try:
                    loc = search_object(evid, use_dbref=True)[0]
                except Exception as e:
                    # TODO: try vnum
                    log_err("! spawnMobs:317: vnum %s - location %s - %s" % (vnum, evid, str(e)))
                    continue

                newmob = create_object(key=ob['name'], location=loc, home=loc, aliases=ob['aliases'],
                                       typeclass=MOB_TYPECLASS,
                                       locks=['get:false()'],
                                       attributes=[('desc', ob['desc']),
                                                   ('ext_desc', ob['ext']),
                                                   ('race', ob['race']),
                                                   ('size', ob['size']),
                                                   ('alignment', ob['alignment']),
                                                   ('area', ob['area']),
                                                   ('vnum', vnum)],
                                       tags=[("imported"),
                                             (self.areaname, 'area'),
                                             (self.areaname, 'mob')])
                self.mob_translate[vnum] = newmob.id
            self.mobs_created = True

    def spawnObjects(self):
        if self.objects_created:
            log_err("Objects already created!")
        else:
            for vnum in sorted(self.objects):
                ob = self.objects[vnum]
                if vnum not in self.object_location.keys():
                    log_err("! vnum %s not found in object_location table for %s" % (vnum, ob['name']))
                    continue
                else:
                    if self.room_translate[self.object_location[vnum]]:
                        evid = "#" + str(self.room_translate[self.object_location[vnum]])
                    elif self.room_translate[self.mob_location[vnum]]:
                        evid = "#" + str(self.room_translate[self.mob_location[vnum]])
                    loc = search_object(evid, use_dbref=True)
                    if len(loc) > 1:
                        loc = loc.filter(db_tags__db_key=self.objects[vnum]['area'])
                    if loc is None:
                        if vnum in self.mob_location.keys():
                            loc = self.mob_location[vnum]
                        else:
                            log_err("! spawnObjects(): vnum %s - location %s not found" % (vnum, evid))
                            continue
                    if loc is not None:
                        if 'QuerySet' in str(loc.__class__):
                            loc = loc[0]
                        if 'weight' in ob.keys():
                            weight = ob['weight']
                        else:
                            weight = 5
                        if 'cost' in ob.keys():
                            cost = ob['cost']
                        else:
                            cost = 10
                        newob = create_object(key=ob['name'].replace("{", "|"), location=loc, home=loc,
                                              aliases=ob['aliases'],
                                              typeclass=ITEM_TYPECLASS,
                                              attributes=[('desc', ob['desc']),
                                                          ('ext_desc', ob['ext']),
                                                          ('item_type', ob['type']),
                                                          ('area', ob['area']),
                                                          ('vnum', vnum),
                                                          ('quality', weight),
                                                          ('resources', {'trash': cost}),
                                                          ('respawn', True),
                                                          ('respawn_time', 60)],
                                              tags=[("imported"),
                                                    (self.areaname, 'area'),
                                                    (self.areaname, 'item')])
                        # log_info("%s created in %s:%s - #%s" % (ob['name'], loc.id, loc.name, newob.id))
