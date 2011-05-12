import pygame
import utils

from time import clock, time
from constants import *
from things import Thing, Projectile, Trap
from ai import AI
import os

class Creature(Thing):
    """Generic superclass for everything that walks around."""
    def __init__(self, filename, position, default_velocity = [145.0, 0.0],
                 velocity = [0.0, 0.0], acceleration = [0.0, GRAVITY],
                 jump_amount = JUMP_AMOUNT, health = 1, max_y = None):
        # self.rect is the creature's RELATIVE position
        # self.position is the ABSOLUTE position
        Thing.__init__(self, filename)
        
        self.velocity = utils.Vector(velocity[0], velocity[1], y_max = max_y)
        self.acceleration = utils.Vector(acceleration[0], acceleration[1])
        self.default_velocity = utils.Vector(default_velocity[0], default_velocity[1])
        
        self.position = pygame.rect.Rect(self.rect)
        self.position.topleft = position
        self.rect.topleft = position
        self.desired_position = pygame.rect.Rect(self.position)
        
        self.jumping = False
        self.jump_amount = jump_amount
        self.landed = True
        self.motion = "right" if self.velocity.x >= 0 else "left"

        self.health = health
        self.dead = False

        self.reload_time = time() - 10
        self.reload_wait = .75 #This gets tampered with elsewhere

        self.AI = AI()
        
    def _turn(self, direction, reset_velocity = True):
        """ Private method that turns the Creature in the given direction. This
        is accomplished by setting the x velocity and flipping the Creature's image
        so that is is oriented in the the direction of travel"""
        if reset_velocity:
            self.velocity.x = self.default_velocity.x * (-1 if direction == "left" else 1)
        if self.motion != direction:
            self.image = pygame.transform.flip(self.image, True, False)
        self.motion = direction
    
    def turn_around(self):
        if self.motion == "left":
            self._turn("right")
        else:
            self._turn("left")
    
    def go_left(self):
        """ Sets the Creature's velocity to its default speed in the left direction,
        and flips the image such that is is facing left"""
        self._turn("left")
    
    def go_right(self):
        """ Sets the Creature's velocity to its default speed in the left direction,
        and flips the image such that is is facing left"""
        self._turn("right")
        
    def stand_still(self):
        """ Stops horizontal movement"""
        self.velocity.x = 0
        
    def jump(self):
        """ Performs the voodoo required to make the Creature jump. If the Creature
        is already jumping, there will be *no* double-jumps"""
        if self.jumping or not self.landed:
            return
        else:
            self.landed = False
            self.jumping = True
            self.velocity.y = self.jump_amount
            #self.position.y -= 9
    
    
    def make_contact(self):
        self.position.bottom = rect.bottom
        self.velocity.y = 0
        self.jumping = False

    def take_a_hit(self, damage = 1):
        self.health -= damage
        if self.health <= 0:
            self.dead = True

    def right_p(self):
        return True if self.velocity.x > 0 else False

    def left_p(self):
        return True if self.velocity.x < 0 else False

    def up_p(self):
        return True if self.velocity.y < 0 else False

    def down_p(self):
        return True if self.velocity.y > 0 else False
    
    def fire(self, projectiles, image, speed, direction, offset=0):
        time_ = time()
        if (self.reload_time + self.reload_wait) < time_:
            if self.motion == "left":
                pos = self.position.topleft
                sign = -1
            else:
                pos = self.position.topright
                sign = 1
            pos = (pos[0], pos[1] + offset)
            proj = Projectile(pos, speed * sign, image, direction)
            projectiles.add(proj)
            self.reload_time = time_
            return True
        return False

    def hitwall(self):
        self.AI.hitwall(self)


    def __str__(self):
        return """
        %s
        Position: %s, %s
        Height: %s
        Width: %s
        Relative Position: %s, %s
        Velocity: %s, %s
        """%(type(self).__name__, self.position.left, self.position.top, self.rect.height, self.rect.width, self.rect.left, self.rect.top, self.velocity.x, self.velocity.y)

class Player(Creature):
    def __init__(self, filename, position,
                default_velocity = [PLAYER_DEF_V, 0.0],
                velocity = [0.0, 0.0],
                acceleration = [0.0, GRAVITY]):
        Creature.__init__(self, filename, position, default_velocity, velocity, acceleration, max_y = 800)
        self.flapping = False
        self.flap_amount = FLAP_AMOUNT
        self.jump_amount = JUMP_AMOUNT
        
        self.shots = 10
        self._points = 0
        walking_image_names = ["%s.png"%i for i in range(1, 3)]
        walking_images = []
        for i in walking_image_names:
            walking_images += [utils.load_image(i, os.path.join("images", "player_walking"), -1, False)]

        flapping_image_names = ["%s.png"%i for i in range(1, 5)]
        flapping_images = []
        for i in flapping_image_names:
            flapping_images += [utils.load_image(i, os.path.join("images", "player_flapping"), -1, False)]
        
        normal_image = utils.load_image("1.png", os.path.join("images", "player_normal"), -1, False)
        self.image = normal_image
        
        walking_animator = utils.Animator(walking_images)
        flapping_animator = utils.Animator(flapping_images)
        self.stances = {"walking" : walking_animator,
                        "flapping": flapping_animator,
                        "normal"  : utils.Animator([normal_image])}
        
        self.anim_time = 0
        self.anim_threshold = 75
        self.lives = 3
        self.next_life = NEW_LIFE

    def get_points(self):
        return self._points
    
    def set_points(self, points):
        self._points = points
        if self._points >= self.next_life:
            self.one_up()
    
    def one_up(self):
        self.lives += 1
        self.next_life += NEW_LIFE

    def hitwall(self):
        pass
 
    def flap(self):
        if not self.flapping:
            self.flapping = True
            self.acceleration.y += self.flap_amount
    
    def make_contact(self):
        Creature.make_contact(self, rect)
        self.unflap()
        
    def unflap(self):
        if self.flapping:
            self.flapping = False
            self.acceleration.y -= self.flap_amount

    def fire(self, projectiles, direction=None, offset=0):
        if self.shots > 0:
            if Creature.fire(self, projectiles, "fireball2.bmp", 550.0, direction, offset):
                self.shots -= 1

    def get_stance(self):
        if self.flapping and not self.landed:
                return "flapping"
        elif self.landed and abs(self.velocity.x) > 0:
                return "walking"
        return "normal"

    def _turn(self, direction, reset_velocity = True):
        if reset_velocity:
            self.velocity.x = self.default_velocity.x * (-1 if direction == "left" else 1) 
        self.stances[self.get_stance()].turn(direction)
        self.motion = direction

    def tick(self, time):
        #self.fuel = min(100.0, self.fuel + self.fuel * time / 1000.0 * self.recharge_rate)
        self.anim_time += time
        if self.anim_time >= self.anim_threshold:
            self.anim_time = 0
            self.image = self.stances[self.get_stance()].next()

    points = property(get_points, set_points)
 
class NPC(Creature):
    """All non-player creatures. Aka enemies."""
    pass # :P

class M1(NPC):
    def __init__(self, position):
        NPC.__init__(self, "m1.png",
                     position = position,
                     default_velocity = (-120.0, 0.0),
                     velocity = (0.0, 0.0),
                     acceleration = (0, 0))

class M2(NPC):
    def __init__(self, position):
        NPC.__init__(self, "m2.png",
                     position = position,
                     default_velocity = (300.0, 0.0),
                     velocity = (00.0, 0.0),
                     acceleration = (0, 0))

class M3(NPC):
    def __init__(self, position):
        NPC.__init__(self, "m3.png",
                     position = position,
                     default_velocity = (350.0, 0.0),
                     velocity = (00.0, 0.0),
                     acceleration = (0, 0))
        self.reload_time = .500
        self.last_shot = time()
    
    def fire(self, projectiles, direction):
        NPC.fire(self, projectiles, "laser.png", 800.0, direction, 30)

    def update(self, window, projectiles):
        NPC.update(self, window)
        time_ = time()
        if self.last_shot + self.reload_time > time_:
            self.fire(projectiles, self.motion)
            self.last_shot = time_
        

class M4:
    pass

class M5:
    pass

class M6:
    pass

class M7:
    pass

class M8:
    pass

class M9:
    pass

class M10:
    pass

class M11:
    pass

class T1(Trap, NPC):
    def __init__(self, position):
        NPC.__init__(self, "spikes.png",
                     position = position,
                     default_velocity = (0, 0),
                     velocity = (0, 0))

class T2(NPC, Trap):
    pass
class T3(NPC, Trap):
    pass
class T4(NPC, Trap):
    pass

class T5(NPC, Trap):
    pass

class T6(NPC, Trap):
    pass

class T7(NPC, Trap):
    pass

class T8(NPC, Trap):
    pass

class T9(NPC, Trap):
    pass

class T10(NPC, Trap):
    pass

class T11(NPC, Trap):
    pass
