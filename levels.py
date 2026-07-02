import pygame
import os

import constants
import tilemerge

from creatures import *
from things import *

class BaseLevel():
    """Basic level class. Defines the width, height, platforms, and such."""
    def __init__(self, filename=None):
        self.width = 0
        self.height = 0
        self.platforms = pygame.sprite.Group()
        self.creatures = pygame.sprite.Group()
        self.powerups  = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.exit = None
        self.starting_pos = None
        self.bg_name = get_background_name(filename)
    
    def make_walls(self, color=pygame.color.Color("black")):
        """Surround the level with walls to prevent things from falling out
           and getting lost."""
        #Bottom
        self.platforms.add(ColoredPlatform(color, (0, self.height), (self.width, constants.VERT_BUFFER)))
        #Top
        self.platforms.add(ColoredPlatform(color, (0, 0 - constants.VERT_BUFFER), (self.width, constants.VERT_BUFFER)))
        #Left
        self.platforms.add(ColoredPlatform(color, (0 - constants.HOR_BUFFER, 0), (constants.HOR_BUFFER, self.height)))
        #Right
        self.platforms.add(ColoredPlatform(color, (self.width, 0), (constants.HOR_BUFFER, self.height)))

    def set_starting_position(self, player):
        """Positions the player in the starting position of the level. If that
           doesn't exist, puts the player near the bottom-left corner."""
        if self.starting_pos is not None:
            player.position.topleft = self.starting_pos
        else:
            player.position.bottomleft = (5, self.height - 5)
        
class Parser():
    """Parses a given level file and constructs a Level object from it."""
    def __init__(self, level, filename, tilesize = 32):
        self.level = level
        self.filename = filename
        self.tilesize = tilesize
        self.ignore = (".", "#")

        # This associates characters found in level files with classes to be
        # instantiated.
        self.map = {"@" : None,
                    "!" : Exit,
                    "z" : P100,#Points
                    "x" : P200,
                    "c" : P500,
                    "n" : P5000,
                    "m" : Gun5,#Ammo pickups
                    "," : Gun10,
                    "a" : M1, #Monsters
                    "s" : M2,
                    "d" : M3,
                    "A" : T1, #Traps
                    "Q" : InvisiblePlatform, #Platforms
                    "W" : HiddenPlatform,
                    "q" : Plat_Black,
                    "w" : Plat_Red,
                    "e" : Plat_Green,
                    "r" : Plat_Blue,
                    "t" : Plat_Yellow}
   
    def parse(self):
        """Performs the actual parsing, mutating self.level with the results."""
        row, column, step = 0, 0, self.tilesize
        longest = 0
        platform_cells = {} #Maps platform classes to sets of (column, row)
        with open(self.filename) as file:
            for line in file.readlines():
                column = 0
                if len(line) > longest: longest = len(line)
                for char in line:
                    position = (column * step, (row + 0) * step)
                    if char == "\n":
                        break
                    if char not in self.ignore:
                        x = self.map[char]
                        if char == "@":
                            self.level.starting_pos = position
                        elif issubclass(x, Exit):
                            self.level.exit = Exit(position)
                        elif issubclass(x, Creature):
                            #Anchor feet to the marker tile's bottom edge, since
                            #most creatures are taller than one tile
                            critter = x(position)
                            critter.position.bottomleft = (position[0], position[1] + step)
                            self.level.creatures.add(critter)
                        elif issubclass(x, Platform):
                            platform_cells.setdefault(x, set()).add((column, row))
                        elif issubclass(x, Powerup):
                            self.level.powerups.add(x(position))
                    if column % 2 == row % 2 == 0:#elif issubclass(x, Tile):
                        self.level.tiles.add(Tile(position, self.level.bg_name))
                    column += 1
                row += 1
        #Merge each platform type's tiles into rectangles, so that a run of
        #adjacent tiles becomes one big Platform instead of many small ones.
        for x, cells in platform_cells.items():
            for tile_x, tile_y, tile_w, tile_h in tilemerge.merge_cells(cells):
                self.level.platforms.add(x((tile_x * step, tile_y * step),
                                           (tile_w * step, tile_h * step)))
        for i in range(0, row, 2):
            self.level.tiles.add(Tile(((column + 0) * step, i * step), self.level.bg_name))
        self.level.width = (longest - 1) * self.tilesize
        self.level.height = (row + 0) * self.tilesize
         
class Level(BaseLevel):
    """Glue between Parser and BaseLevel. A BaseLevel subclass that constructs
       itself from a given .level file."""
    def __init__(self, filename):
        BaseLevel.__init__(self, filename + ".png")
        self.creatures.empty()
        self.platforms.empty()
        self.powerups.empty()
        Parser(self, os.path.join("levels", filename + ".level")).parse()
        BaseLevel.make_walls(self)
        self.bg_name = get_background_name(filename)

class LevelList():
    """Iterator that controls the order of levels."""
    def __init__(self):
        self.list = ["level%d"%i for i in range(1, 10)]
        self.pointer = 0

    def next_level(self):
        level = Level(self.list[self.pointer])
        self.pointer += 1 
        return level

    def same_level(self):
        level = Level(self.list[self.pointer - 1])
        return level

def get_background_name(filename):
    try:
        number = int(filename.replace("level", "").replace(".png", ""))
    except (AttributeError, ValueError):
        return ""
    return {3: "keen5_2.png", 5: "keen5_2.png"}.get(number, "keen5_1.png")
