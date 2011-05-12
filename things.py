import pygame
import constants
import utils


class Thing(pygame.sprite.Sprite):
    def __init__(self, filename=None, directory="images", colorkey = -1):
        pygame.sprite.Sprite.__init__(self)
        if filename is not None:
            self.image, self.rect = utils.load_image(filename, directory, colorkey = colorkey)
            self.position = pygame.rect.Rect(self.rect)
               
        
    def set_relative_position(self, window):
        self.rect.x = self.position.x - window.x
        self.rect.y = self.position.y - window.y
        
    def update(self, window, projectiles=None):
        Thing.set_relative_position(self, window)
  
    def set_slices(self, p=None, size=1):
        if p == None:
            p = self.position
        self.right_slice = pygame.rect.Rect(p.right - size, p.top, size, p.height)
        self.left_slice  = pygame.rect.Rect(p.left, p.top, size, p.height)
        self.top_slice   = pygame.rect.Rect(p.left, p.top, p.width, size)
        self.bottom_slice= pygame.rect.Rect(p.left, p.bottom - size, p.width, size)

class Tile(Thing):
    def __init__(self, position, filename):
        Thing.__init__(self, filename, "tiles", None)
        self.position = pygame.rect.Rect(self.rect)
        self.position.topleft = position

class Exit(Thing):
    def __init__(self, position):
        Thing.__init__(self, "exit.png")
        self.position = pygame.rect.Rect(self.rect)
        self.position.topleft = position


class Powerup(Thing):
    def __init__(self, position, filename):
        Thing.__init__(self, filename, "powerups")
        self.position = pygame.rect.Rect(self.rect)
        self.position.topleft = position
    

class Ammo(Powerup):
    def __init__(self, position, amount):
        Powerup.__init__(self, position, "fireweed.png")
        self.amount = amount

    def use(self, player):
        player.shots += self.amount

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
    pass

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

class Projectile(Thing):
    def __init__(self, starting_pos, velocity, filename, direction):
        Thing.__init__(self)
        self.image, self.rect = utils.load_image(filename, "projectiles", -1)
        self.rect.topleft = starting_pos
        self.position = pygame.rect.Rect(self.rect)
        self.desired_position = pygame.rect.Rect(self.position)
        self.velocity = utils.Vector(velocity if direction != "down" else 0, abs(velocity * 1.5) if direction == "down" else 0)
        self.acceleration = utils.Vector(0, constants.GRAVITY if direction == "down" else 0)
        
class Trap:
    def take_a_hit(self):
        pass

class Platform(Thing):
    def __init__(self, filename, position):
        Thing.__init__(self)
        self.image, self.rect = utils.load_image(filename, "platforms")
        self.rect.topleft = position
        self.position = pygame.rect.Rect(self.rect)
        Thing.set_slices(self)
        self.type = "Platform"
    
    def update(self, window):
        Thing.set_relative_position(self, window)

        
class ColoredPlatform(Platform):
    def __init__(self, color, position, size, transparent=False):
        Thing.__init__(self)
        self.image = pygame.Surface(size)
        self.image.fill(color)
        if transparent:
            self.image.set_colorkey(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.position = pygame.rect.Rect(self.rect)
        Thing.set_slices(self)

class InvisiblePlatform(ColoredPlatform):
    def __init__(self, position, tilesize):
        ColoredPlatform.__init__(self, pygame.Color("white"), position, (tilesize, tilesize), True)

class HiddenPlatform(ColoredPlatform):
    def __init__(self, position, tilesize):
        ColoredPlatform.__init__(self, pygame.Color("white"), position, (tilesize, tilesize), True)

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


