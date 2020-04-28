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

