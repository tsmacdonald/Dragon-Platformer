import pygame
import os

import constants
import utils

from creatures import *
from things import *

class BaseLevel():
    def __init__(self, filename=None):
        #self.background = Thing(filename, "backgrounds")
        self.width = 0
        self.height = 0
        self.platforms = pygame.sprite.Group()
        self.creatures = pygame.sprite.Group()
        self.powerups  = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.exit = None
        self.starting_pos = None
        self.bg_name = Utils.get_background_name(filename)
    
    def make_walls(self, color=pygame.color.Color("black")):
        #Bottom
        self.platforms.add(ColoredPlatform(color, (0, self.height), (self.width, constants.VERT_BUFFER)))
        #Top
        self.platforms.add(ColoredPlatform(color, (0, 0 - constants.VERT_BUFFER), (self.width, constants.VERT_BUFFER)))
        #Left
        self.platforms.add(ColoredPlatform(color, (0 - constants.HOR_BUFFER, 0), (constants.HOR_BUFFER, self.height)))
        #Right
        self.platforms.add(ColoredPlatform(color, (self.width, 0), (constants.HOR_BUFFER, self.height)))

    def set_starting_position(self, player):
        if self.starting_pos is not None:
            player.position.topleft = self.starting_pos
        else:
            player.position.x, player.position.y = 5, self.height - 5
        
class Parser():
    def __init__(self, level, filename, tilesize = 32):
        self.level = level
        self.filename = filename
        self.tilesize = tilesize
        self.map = {"@" : None,
                    "!" : Exit,
                    "z" : P100,
                    "x" : P200,
                    "c" : P500,
                    "v" : P1000,
                    "b" : P2000,
                    "n" : P5000,
                    "m" : Gun5,
                    "," : Gun10,
                    "/" : Life,
                    "Z" : P100_2,
                    "X" : P200_2,
                    "C" : P500_2,
                    "V" : P1000_2,
                    "B" : P2000_2,
                    "N" : P5000_2,
                    "M" : Gun5_2,
                    "<" : Gun10_2,
                    "?" : Life_2,
                    "a" : M1,
                    "s" : M2,
                    "d" : M3,
                    "f" : M4,
                    "g" : M5,
                    "h" : M6,
                    "j" : M7,
                    "k" : M8,
                    "l" : M9,
                    ";" : M10,
                    "'" : M11,
                    "A" : T1,
                    "S" : T2,
                    "D" : T3,
                    "F" : T4,
                    "G" : T5,
                    "H" : T6,
                    "J" : T7,
                    "K" : T8,
                    "L" : T9,
                    "Q" : InvisiblePlatform,
                    "W" : HiddenPlatform,
                    "q" : Plat_Black,
                    "w" : Plat_Red,
                    "e" : Plat_Green,
                    "r" : Plat_Blue,
                    "t" : Plat_Yellow,
                    "y" : Plat1,
                    "u" : Plat2,
                    "i" : Plat3,
                    "o" : Plat4,
                    "p" : Plat5,
                    "[" : Plat6,
                    "]" : Plat7}
   
    def parse(self):
        row, column, step = 0, 0, self.tilesize
        longest = 0
        with open(self.filename) as file:
            for line in file.readlines():
                column = 0
                if len(line) > longest: longest = len(line)
                for char in line:
                    position = (column * step, (row + 0) * step)
                    if char == "\n":
                        break
                    if char not in (".", "#"):
                        x = self.map[char]
                        if char == "@":
                            self.level.starting_pos = position
                        elif issubclass(x, Exit):
                            self.level.exit = Exit(position)
                        elif issubclass(x, Creature):
                            self.level.creatures.add(x(position))
                        elif issubclass(x, Platform):
                            self.level.platforms.add(x(position, self.tilesize))
                        elif issubclass(x, Powerup):
                            self.level.powerups.add(x(position))
                    if column % 2 == row % 2 == 0:#elif issubclass(x, Tile):
                        self.level.tiles.add(Tile(position, self.level.bg_name))
                    column += 1
                row += 1
        for i in range(0, row, 2):
            self.level.tiles.add(Tile(((column + 0) * step, i * step), self.level.bg_name))
        self.level.width = (longest - 1) * self.tilesize
        self.level.height = (row + 0) * self.tilesize
         
class Level(BaseLevel):
    def __init__(self, filename):
        BaseLevel.__init__(self, filename + ".png")
        self.creatures.empty()
        self.platforms.empty()
        self.powerups.empty()
        Parser(self, os.path.join("levels", filename + ".level")).parse()
        BaseLevel.make_walls(self)
        self.bg_name = Utils.get_background_name(filename)

class LevelList():
    def __init__(self):
        self.list = ["level%d"%i for i in xrange(1, 10)]
        self.pointer = 0

    def next_level(self):
        level = Level(self.list[self.pointer])
        self.pointer += 1 
        return level

    def same_level(self):
        self.pointer -= 1
        level = Level(self.list[self.pointer])
        self.pointer += 1
        return level

class Utils():
    @staticmethod
    def get_background_name(filename):
        if filename == None:
            print "No filename for level!"
            return "" #Garbage in, garbage out...
        try:
            number = int(filename.replace("level", "").replace(".png", ""))
        except ValueError:
            print '"%s" is an unacceptable level name!'%filename
            return ""
        if number == 1:
            return "keen5_1.png"
        elif number == 2:
            return "keen5_1.png"
        elif number == 3:
            return "keen5_2.png"
        elif number == 4:
            return "keen5_1.png"
        elif number == 5:
            return "keen5_2.png"
        else:
            print "Warning: Using default background..."
            return "keen5_1.png"
