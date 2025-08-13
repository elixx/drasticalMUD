from evennia.utils.create import create_object
from evennia.utils.logger import log_info, log_err, log_warn
from evennia.utils.search import search_object
from .area_reader import *

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
        self.mob_equipment_enumerated = False

        self.mobs = {}
        self.mob_translate = {}
        self.mobs_enumerated = False
        self.mobs_created = False

        self.object_location = {}
        self.mob_location = {}
        self.mob_equipment = {}  # Maps object vnum to mob vnum for equipment
        self.container_objects = {}  # Maps object vnum to container vnum for P commands

        self.last_area = ""

        if (filename):
            self.load(filename)

    def load(self, filename):
        try_other_classes = False
        self.area_file = RomAreaFile(filename)
        try:
            self.area_file.load_sections()
        except Exception as e:
            try_other_classes = True
            print(str(e))
            pass
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
        self.mob_equipment_enumerated = False
        self.mobs_created = False
        self.mobs_enumerated = False

        # Reset location tracking dictionaries
        self.object_location = {}
        self.mob_location = {}
        self.mob_equipment = {}
        self.container_objects = {}

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
                exits[x.door] = {'desc': x.description,
                                 'dest': x.destination}

            self.rooms[v.vnum] = {'name': name,
                                  'desc': desc,
                                  'exits': exits,
                                  'area': areaname}
            count += 1
        log_info(f"enumerateRooms(): {areaname} - {count} rooms")
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
                        "! enumerateMobLocations(): " + str(e) + "\n\tmob_vnum=v" + str(r.arg1) + " room_vnum=v" + str(
                            r.arg3))

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
        last_mob_vnum = None
        for r in self.area_file.area.resets:
            # O - Object into room
            # P - Object into object (container)
            # E - Object into mob (equipment)
            # G - Object into mob inventory
            # M - Mobile (track for subsequent E/G commands)
            if r.command == 'M':
                last_mob_vnum = r.arg1
            elif r.command == 'O':
                try:
                    object = r.arg1
                    room = r.arg3
                    self.object_location[object] = room
                    log_info(f"enumerateObjectLocations(O): Object v{object} placed in room v{room}")
                except Exception as e:
                    log_err(
                        "! enumerateObjectLocations(O): " + str(e) + "\n\tobject_vnum=v" + str(
                            r.arg1) + " room_vnum=v" + str(r.arg3))
            elif r.command == 'E':
                try:
                    object = r.arg1
                    wear_loc = r.arg3
                    if last_mob_vnum is not None:
                        # Store that this object should be equipped on the last spawned mob
                        self.mob_equipment[object] = last_mob_vnum
                        log_info(
                            f"enumerateObjectLocations(E): Object v{object} equipped on mob v{last_mob_vnum} at wear_loc {wear_loc}")
                    else:
                        log_err(
                            f"! enumerateObjectLocations(E): Object v{object} has E command but no previous M command")
                except Exception as e:
                    log_err(
                        "! enumerateObjectLocations(E): " + str(e) + "\n\tobject_vnum=v" + str(
                            r.arg1) + " wear_location=" + str(r.arg3))
            elif r.command == 'G':
                try:
                    object = r.arg1
                    if last_mob_vnum is not None:
                        # Store that this object should be given to the last spawned mob's inventory
                        self.mob_equipment[object] = last_mob_vnum
                        log_info(
                            f"enumerateObjectLocations(G): Object v{object} given to mob v{last_mob_vnum} inventory")
                    else:
                        log_err(
                            f"! enumerateObjectLocations(G): Object v{object} has G command but no previous M command")
                except Exception as e:
                    log_err(
                        "! enumerateObjectLocations(G): " + str(e) + "\n\tobject_vnum=v" + str(r.arg1))
            elif r.command == 'P':
                try:
                    object = r.arg1
                    container = r.arg3
                    # Store container relationship for P commands
                    self.container_objects[object] = container
                    log_info(f"enumerateObjectLocations(P): Object v{object} put inside container v{container}")
                except Exception as e:
                    log_err(
                        "! enumerateObjectLocations(P): " + str(e) + "\n\tobject_vnum=v" + str(
                            r.arg1) + " container_vnum=v" + str(r.arg3))

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
                                        #locks=['puppet:false()', 'get:false()'],
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
                #     "spawnRooms(): Area:%s Room:'%s' Vnum:v%s Evid:#%s" % (room['area'], room['name'], vnum, newroom.id))
                if (firstRoom):
                    log_warn(
                        "* Entry to " + room['area'] + ' - #' + str(newroom.id) + " (v" + str(vnum) + ") = " + room[
                            'name'])
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
            # Track exit statistics
            total_exits = 0
            successful_exits = 0
            nowhere_exits = 0
            cross_area_exits = 0
            blackhole_rooms = 0
            for vnum in sorted(self.rooms):
                room = self.rooms[vnum]
                count = 0
                for exit, exitData in room['exits'].items():
                    total_exits += 1
                    exitDir = exit.name.lower()
                    evid = "#" + str(self.room_translate[vnum])
                    loc = search_object(evid, use_dbref=True)[0]
                    if loc is None:
                        loc = search_object(room['name'])[0]
                        if loc is None:
                            log_err('! missing source: ' + str(loc))
                            continue
                    if exitData['dest'] not in self.room_translate.keys():
                        # Handle special cases for one-way exits and cross-area connections
                        if exitData['dest'] == -1:
                            # -1 is a common "nowhere" destination for one-way traps or dead ends
                            log_info(
                                f"Creating one-way exit '{exitDir}' in {room['area']} room v{vnum} (nowhere destination)")
                            create_object(typeclass=EXIT_TYPECLASS,
                                          key=exitDir, location=loc, destination=None, aliases=[DIRALIAS[exitDir]],
                                          tags=[(room['area'], 'area'),
                                                (room['area'], 'exit'),
                                                ('imported'),
                                                ('one_way_trap', 'exit')],
                                          attributes=[('area', room['area']),
                                                      ('vnum', vnum),
                                                      ('dest_vnum', exitData['dest']),
                                                      ('exit_type', 'nowhere')])
                            count += 1
                            nowhere_exits += 1
                            continue
                        else:
                            # This is likely a cross-area exit - create a one-way exit with stored destination info
                            log_warn(
                                f"Creating one-way exit '{exitDir}' in {room['area']} room v{vnum} -> cross-area destination v{exitData['dest']}")
                            create_object(typeclass=EXIT_TYPECLASS,
                                          key=exitDir, location=loc, destination=None, aliases=[DIRALIAS[exitDir]],
                                          tags=[(room['area'], 'area'),
                                                (room['area'], 'exit'),
                                                ('imported'),
                                                ('cross_area', 'exit')],
                                          attributes=[('area', room['area']),
                                                      ('vnum', vnum),
                                                      ('dest_vnum', exitData['dest']),
                                                      ('exit_type', 'cross_area')])
                            count += 1
                            cross_area_exits += 1
                            continue
                    evdestid = "#" + str(self.room_translate[exitData['dest']])
                    try:
                        dest = search_object(evdestid, use_dbref=True)[0]
                        if dest is None:
                            log_err(
                                '! no destination object: ' + room['area'] + ": Exit " + exitDir + " in EVid " + str(
                                    evid) + " (v" + str(vnum) + ") skipped, v" + str(exitData['dest']) + " not found.")
                            continue
                    except Exception as e:
                        log_err(
                            f"! destination lookup failed: {room['area']}: Exit {exitDir} in EVid {evid} (v{vnum}) -> v{exitData['dest']}: {str(e)}")
                        continue
                    create_object(typeclass=EXIT_TYPECLASS,
                                  key=exitDir, location=loc, destination=dest, aliases=[DIRALIAS[exitDir]],
                                  tags=[(room['area'], 'area'),
                                        (room['area'], 'exit'),
                                        ('imported')],
                                  #locks=['puppet:false()', 'get:false()'],
                                  attributes=[('area', room['area']),
                                              ('vnum', vnum)])
                    count += 1
                    successful_exits += 1
                if count == 0:
                    # Blackhole detection - room has no valid exits
                    # This could be intentional (dead end, special room) or an error
                    log_warn(
                        f"Blackhole room detected - vnum v{vnum}, EvId #{self.room_translate[vnum]} in {room['area']} - '{room['name']}'")
                    # Add a tag to identify blackhole rooms for potential special handling
                    evid_obj = "#" + str(self.room_translate[vnum])
                    try:
                        room_obj = search_object(evid_obj, use_dbref=True)[0]
                        room_obj.tags.add('blackhole', category='room')
                        room_obj.tags.add('dead_end', category='room')
                    except Exception as e:
                        log_err(f"! Failed to tag blackhole room v{vnum}: {str(e)}")
                    # TODO: check IDs listed in self.entries and remove if present
                    blackhole_rooms += 1
            
            self.exits_created = True
            log_info(
                f"Exit creation summary for {self.areaname}: {successful_exits}/{total_exits} successful, {nowhere_exits} nowhere, {cross_area_exits} cross-area, {blackhole_rooms} blackhole rooms")

    def spawnMobs(self):
        if self.mobs_created:
            log_err("Mobs already created!")
        else:
            for vnum in sorted(self.mobs):
                if vnum not in self.mobs.keys():
                    log_err("spawnMobs():300: v%s not found" % vnum)
                    continue
                ob = self.mobs[vnum]
                if vnum not in self.mob_location.keys():
                    # mob location could not be found
                    log_err("! %s - vnum v%s not found in mob_location" % (ob['name'], vnum))
                    continue

                if self.mob_location[vnum] not in self.room_translate.keys():
                    log_err("! %s - vnum v%s not found in room_translate" % (ob['name'], vnum))
                    continue

                evid = "#" + str(self.room_translate[self.mob_location[vnum]])
                try:
                    loc = search_object(evid, use_dbref=True)[0]
                except Exception as e:
                    # TODO: try vnum
                    log_err("! spawnMobs:317: vnum v%s - location %s - %s" % (vnum, evid, str(e)))
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
                loc = None

                # Check if this object should be equipped on a mob
                if vnum in self.mob_equipment:
                    mob_vnum = self.mob_equipment[vnum]
                    if mob_vnum in self.mob_translate:
                        mob_evid = "#" + str(self.mob_translate[mob_vnum])
                        try:
                            loc = search_object(mob_evid, use_dbref=True)[0]
                            # Determine if this is equipment or inventory based on the reset command type
                            # This is a simplified approach - in a full implementation you'd track the command type
                            log_info(
                                f"spawnObjects(): Giving object v{vnum} ({ob['name']}) to mob v{mob_vnum} evid:{mob_evid}")
                        except Exception as e:
                            log_err(f"! spawnObjects(): Failed to find mob v{mob_vnum} for equipment v{vnum}: {str(e)}")
                            continue
                    else:
                        log_err(f"! spawnObjects(): Mob v{mob_vnum} not found in mob_translate for equipment v{vnum}")
                        continue

                # Check if this object should be placed in a container
                elif vnum in self.container_objects:
                    container_vnum = self.container_objects[vnum]
                    if container_vnum in self.object_translate:
                        container_evid = "#" + str(self.object_translate[container_vnum])
                        try:
                            loc = search_object(container_evid, use_dbref=True)[0]
                            log_info(
                                f"spawnObjects(): Placing object v{vnum} ({ob['name']}) inside container v{container_vnum} evid:{container_evid}")
                        except Exception as e:
                            log_err(
                                f"! spawnObjects(): Failed to find container v{container_vnum} for object v{vnum}: {str(e)}")
                            continue
                    else:
                        log_err(
                            f"! spawnObjects(): Container v{container_vnum} not found in object_translate for object v{vnum}")
                        continue

                # Check if this object should be placed in a room
                elif vnum in self.object_location:
                    room_vnum = self.object_location[vnum]
                    if room_vnum in self.room_translate:
                        evid = "#" + str(self.room_translate[room_vnum])
                        try:
                            loc = search_object(evid, use_dbref=True)[0]
                        except Exception as e:
                            log_err(f"! spawnObjects(): Failed to find room v{room_vnum} for object v{vnum}: {str(e)}")
                            continue
                    else:
                        log_err(f"! spawnObjects(): Room v{room_vnum} not found in room_translate for object v{vnum}")
                        continue
                else:
                    log_err(
                        "! vnum v%s not found in object_location, mob_equipment, or container_objects for %s" % (vnum,
                                                                                                                 ob[
                                                                                                                     'name']))
                    continue

                if loc is not None:
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
                    self.object_translate[vnum] = newob.id
                    # log_info("%s (v%s) created in #%s:%s - #%s" % (ob['name'], vnum, loc.id, loc.name, newob.id))
            self.objects_created = True
