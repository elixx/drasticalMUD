# mygame/world/map.py

# These are keys set with the Attribute sector_type on the room.
# The keys None and "you" must always exist.
SYMBOLS = {None:           ' . ',  # for rooms without a sector_type attr
           'owned-self':   ' |g,|n ',   # owned by self
           'self-growing': ' |G%|n ',  # owned by self and growing
           'owned-other':  ' |R.|n ',  # owned by other player
           'other-growing': ' |R%|n ',  # owned by other and growing
           'you':          ' |r@|n ',   # self
           'SECT_INSIDE':    '[.]',
           'attention':    ' |y*|n ',   # this will take precedence if set as sector_type
           'important':     ' |C*|n ',
           'warning':      ' |r!|n '}   # this too


class Map(object):

    def __init__(self, caller, max_width=7, max_length=7):
        self.caller = caller
        self.max_width = max_width
        self.max_length = max_length
        self.worm_has_mapped = {}
        self.curX = None
        self.curY = None

        if self.check_grid():
            # we actually have to store the grid into a variable
            self.grid = self.create_grid()
            self.draw_room_on_map(caller.location,
                                  ((min(max_width, max_length) - 1) / 2))

    def update_pos(self, room, exit_name):
        # this ensures the pointer variables always
        # stays up to date to where the worm is currently at.
        self.curX, self.curY = \
            self.worm_has_mapped[room][0], self.worm_has_mapped[room][1]

        # now we have to actually move the pointer
        # variables depending on which 'exit' it found
        if exit_name == 'east':
            self.curY += 1
        elif exit_name == 'west':
            self.curY -= 1
        elif exit_name == 'north':
            self.curX -= 1
        elif exit_name == 'south':
            self.curX += 1

    def draw_room_on_map(self, room, max_distance):
        self.draw(room)

        if max_distance == 0:
            return

        for exit in room.exits:
            if exit.name not in ("north", "east", "west", "south"):
                # we only map in the cardinal directions. Mapping up/down would be
                # an interesting learning project for someone who wanted to try it.
                continue
            if self.has_drawn(exit.destination):
                # we've been to the destination already, skip ahead.
                continue

            self.update_pos(room, exit.name.lower())
            self.draw_room_on_map(exit.destination, max_distance - 1)

    def draw(self, room):
        # draw initial caller location on map first!
        if room == self.caller.location:
            self.start_loc_on_grid()
            self.worm_has_mapped[room] = [self.curX, self.curY]
        else:
            # map all other rooms
            self.worm_has_mapped[room] = [self.curX, self.curY]
            # this will use the sector_type Attribute or None if not set.
            if room.db.sector_type in ['attention', 'warning']:                 # override sector for these
                self.grid[self.curX][self.curY] = SYMBOLS[room.db.sector_type]
            elif room.owner:                                                 # show sector based on ownership
                growing = False
                for i in room.contents:
                    if 'growable' in i.typeclass_path and i.db.planted:
                        growing = True
                if room.owner == str(self.caller.id):
                    if growing:
                        self.grid[self.curX][self.curY] = SYMBOLS['self-growing']
                    else:
                        self.grid[self.curX][self.curY] = SYMBOLS['owned-self']
                else:
                    if growing:
                        self.grid[self.curX][self.curY] = SYMBOLS['other-growing']
                    else:
                        self.grid[self.curX][self.curY] = SYMBOLS['owned-other']
            else:
                self.grid[self.curX][self.curY] = SYMBOLS[room.db.sector_type]   # or the room-defined property

            for i in room.contents:                  # show up and down exits on top of existing symbol
                if 'exit' in i.typeclass_path:
                    if i.key == 'up' or i.key == 'leave mine':
                        sym = self.grid[self.curX][self.curY][1:]    # up exits go on the left
                        self.grid[self.curX][self.curY] = "<" + sym
                    if i.key == 'down' or i.key == 'enter mine':
                        sym = self.grid[self.curX][self.curY][:-1]   # down exits on the right
                        self.grid[self.curX][self.curY] = sym + ">"
                    # log_err(self.grid[self.curX][self.curY])

    def median(self, num):
        lst = sorted(range(0, num))
        n = len(lst)
        m = n - 1
        return (lst[n // 2] + lst[m // 2]) / 2.0

    def start_loc_on_grid(self):
        x = self.median(self.max_width)
        y = self.median(self.max_length)
        # x and y are floats by default, can't index lists with float types
        x, y = int(x), int(y)

        self.grid[x][y] = SYMBOLS['you']
        self.curX, self.curY = x, y  # updating worms current location

    def has_drawn(self, room):
        return True if room in self.worm_has_mapped.keys() else False

    def create_grid(self):
        # This method simply creates an empty grid
        # with the specified variables from __init__(self):
        board = []
        for row in range(self.max_width):
            board.append([])
            for column in range(self.max_length):
                board[row].append('   ')
        return board

    def check_grid(self):
        # this method simply checks the grid to make sure
        # both max_l and max_w are odd numbers
        return True if self.max_length % 2 != 0 or \
                       self.max_width % 2 != 0 else False

    def show_map(self):
        if self.caller.db.OPTION_NOMAP:
            return ""
        map_string = ""
        for row in self.grid:
            map_string += " ".join(row)
            map_string += "\n"

        return map_string
