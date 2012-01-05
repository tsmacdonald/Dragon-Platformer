import pygame
import constants
import utils
import mediahandler


class Thing(pygame.sprite.Sprite):
    """Wrapper class around PyGame's sprite, which adds a few game-specific
       methods required for any game object drawn on-screen."""
    def __init__(self, filename=None, directory="images", colorkey = -1):
        pygame.sprite.Sprite.__init__(self)
        if filename is not None:
            self.image, self.rect = mediahandler.load_image(filename, directory, colorkey = colorkey)
            self.position = pygame.rect.Rect(self.rect)
               
        
    def set_relative_position(self, window):
        self.rect.x = self.position.x - window.x
        self.rect.y = self.position.y - window.y
        
    def update(self, window, projectiles=None):
        Thing.set_relative_position(self, window)

class Tile(Thing):
    """A background, er, tile. (That is, an image.)"""
    def __init__(self, position, filename):
        Thing.__init__(self, filename, "tiles", None)
        self.position = pygame.rect.Rect(self.rect)
        self.position.topleft = position

class Exit(Thing):
    """The door that marks the end of the level."""
    def __init__(self, position):
        Thing.__init__(self, "exit.png")
        self.position = pygame.rect.Rect(self.rect)
        self.position.topleft = position


class Powerup(Thing):
    """Something to be run into for points or other enhancements."""
    def __init__(self, position, filename):
        Thing.__init__(self, filename, "powerups")
        self.position = pygame.rect.Rect(self.rect)
        self.position.topleft = position
    

class Ammo(Powerup):
    """Powerup for adding ammunition."""
    def __init__(self, position, amount):
        Powerup.__init__(self, position, "fireweed.png")
        self.amount = amount

    def use(self, player):
        player.shots += self.amount

##############################################################################
# Almost all of the classes that follow are just very thin wrappers around
# some Ammo or Points that hardcode certain values. This is because the level
# parser does not have the ability to add arbitrary arguments when it
# instantiates things.
###############################################################################

class Gun5(Ammo):
    def __init__(self, position):
        Ammo.__init__(self, position, 5)

class Gun10(Ammo):
    def __init__(self, position):
        Ammo.__init__(self, position, 10)

class Gun5_2(Ammo):
    def __init__(self, position):
        Ammo.__init__(self, position, 5)

class Gun10_2(Ammo):
    def __init__(self, position):
        Ammo.__init__(self, position, 10)

class Points(Powerup):
    """Powerup for adding points."""
    def __init__(self, position, points):
        possible = (100, 200, 500, 1000, 2000, 5000)
        if points not in possible:
            raise Exception("Your level designer is an idiot.")
        self.points = points
        if points == possible[0]:
            filename = "coins"
        elif points == possible[1]:
            filename = "spikefruit"
        elif points == possible[2]:
            filename = "spacemouse"
        elif points == possible[5]:
            filename = "many_coins"
        else:
            print "Bad point value, somehow"
            import sys; sys.exit(1)
        filename += ".png"
        Powerup.__init__(self, position, filename)
    
    def use(self, player):
        player.points += self.points

class P100(Points):
    def __init__(self, position):
        Points.__init__(self, position, 100)

class P200(Points):
    def __init__(self, position):
        Points.__init__(self, position, 200)

class P500(Points):
    def __init__(self, position):
        Points.__init__(self, position, 500)

class P1000(Points):
    def __init__(self, position):
        Points.__init__(self, position, 1000)

class P2000(Points):
    def __init__(self, position):
        Points.__init__(self, position, 2000)

class P5000(Points):
    def __init__(self, position):
        Points.__init__(self, position, 5000)

class Life(Points):
    pass #TODO

# Eventually all the _2 classes will take up a different sector of the tile
# (so that some powerups can be left-aligned and some right-aligned). TODO

class P100_2(Points):
    def __init__(self, position):
        Points.__init__(self, position, 100)

class P200_2(Points):
    def __init__(self, position):
        Points.__init__(self, position, 200)

class P500_2(Points):
    def __init__(self, position):
        Points.__init__(self, position, 500)

class P1000_2(Points):
    def __init__(self, position):
        Points.__init__(self, position, 1000)

class P2000_2(Points):
    def __init__(self, position):
        Points.__init__(self, position, 2000)

class P5000_2(Points):
    def __init__(self, position):
        Points.__init__(self, position, 5000)

class Life_2(Points):
    pass

###############################################################################

class Projectile(Thing):
    """A fireball, laserbeam, or whatever else that flies through the air and
       damages things."""
    def __init__(self, starting_pos, velocity, filename, direction):
        Thing.__init__(self)
        self.image, self.rect = mediahandler.load_image(filename, "projectiles", -1)
        self.rect.topleft = starting_pos
        self.position = pygame.rect.Rect(self.rect)
        self.desired_position = pygame.rect.Rect(self.position)
        self.velocity = utils.Vector(velocity if direction != "down" else 0, abs(velocity * 1.5) if direction == "down" else 0)
        self.acceleration = utils.Vector(0, constants.GRAVITY if direction == "down" else 0)
        
class Trap:
    """A stationary enemy."""
    def take_a_hit(self):
        pass

class Platform(Thing):
    """A solid surface on which Creatures can stand."""
    def __init__(self, filename, position):
        Thing.__init__(self)
        self.image, self.rect = mediahandler.load_image(filename, "platforms")
        self.rect.topleft = position
        self.position = pygame.rect.Rect(self.rect)
        self.type = "Platform"
    
    def update(self, window):
        Thing.set_relative_position(self, window)

        
class ColoredPlatform(Platform):
    """Platform subclass that makes it easy to specify solid color fills."""
    def __init__(self, color, position, size, transparent=False):
        Thing.__init__(self)
        self.image = pygame.Surface(size)
        self.image.fill(color)
        if transparent:
            self.image.set_colorkey(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.position = pygame.rect.Rect(self.rect)

class InvisiblePlatform(ColoredPlatform):
    """A platform not seen or felt by the player. Used to control NPC
       movement."""
    def __init__(self, position, tilesize):
        ColoredPlatform.__init__(self, pygame.Color("white"), position, (tilesize, tilesize), True)

class HiddenPlatform(ColoredPlatform):
    """A platform that can be felt but not seen by the player. Used to make
       levels harder."""
    def __init__(self, position, tilesize):
        ColoredPlatform.__init__(self, pygame.Color("white"), position, (tilesize, tilesize), True)

# The next few classes are required by the parser. See above note.
class Plat_Black(ColoredPlatform):
    def __init__(self, position, tilesize):
        ColoredPlatform.__init__(self, pygame.Color("black"), position, (tilesize, tilesize))

class Plat_Red(ColoredPlatform):
    def __init__(self, position, tilesize):
        ColoredPlatform.__init__(self, pygame.Color("red"), position, (tilesize, tilesize))

class Plat_Green(ColoredPlatform):
    def __init__(self, position, tilesize):
        ColoredPlatform.__init__(self, pygame.Color("green"), position, (tilesize, tilesize))

class Plat_Blue(ColoredPlatform):
    def __init__(self, position, tilesize):
        ColoredPlatform.__init__(self, pygame.Color("blue"), position, (tilesize, tilesize))

class Plat_Yellow(ColoredPlatform):
    def __init__(self, position, tilesize):
        ColoredPlatform.__init__(self, pygame.Color("yellow"), position, (tilesize, tilesize))


#TODO
class Plat1:
    pass

class Plat2:
    pass

class Plat3:
    pass

class Plat4:
    pass

class Plat5:
    pass

class Plat6:
    pass

class Plat7:
    pass


