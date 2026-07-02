import pygame
from copy import copy
from creatures import Player
from things import InvisiblePlatform

def _hit(a, b):
    """Pixel-perfect collision on absolute positions. (The default rect
       collision is both too coarse and stale for off-screen sprites.)"""
    if not a.position.colliderect(b.position):
        return False
    offset = (b.position.x - a.position.x, b.position.y - a.position.y)
    return a.mask.overlap(b.mask, offset) is not None

class Engine():
    """The physics engine, responsible for moving things in a sensible way."""
    def __init__(self, player, level, friendly_projectiles, enemy_projectiles):
        self.player = player
        self.level = level
        self.friendly_projectiles = friendly_projectiles
        self.enemy_projectiles = enemy_projectiles

    def move_everyone(self):
        """Sets everyone's position to their desired position. This should be called
           after the desired position has been modified to deal with platform
           collisions."""
        for c in (self.level.creatures.sprites() +
                [self.player] + self.enemy_projectiles.sprites() + self.friendly_projectiles.sprites()):
            c.position = copy(c.desired_position)

    def update(self, time):
        """Advances everything by the given time (in milliseconds)."""
        self.kinematics(time)
        self.do_collisions()
        self.move_everyone()
    
    def kinematicize(self, critter, time):
        """Sets the critter's desired position and actual velocity, according
           to the Laws of Motion."""
        critter.desired_position.x = critter.position.x + (critter.velocity.x * time)
        critter.desired_position.y = critter.position.y + (critter.velocity.y * time)
        critter.velocity.x += critter.acceleration.x * time
        critter.velocity.y += critter.acceleration.y * time
            
    def kinematics(self, time):
        """Advances everyone's velocity and desired position."""
        time /= 1000.0 #milliseconds to seconds
        for critter in (self.level.creatures.sprites() +
                        self.enemy_projectiles.sprites() + self.friendly_projectiles.sprites() + [self.player]):
            self.kinematicize(critter, time)
    
    def do_collisions(self):
        """Checks collisions with projectiles, platforms, traps, and enemies."""
        self.projectile_collisions()
        self.platform_collisions()
        self.player_death_collision()

    def player_death_collision(self):
        """Checks if the player has run into anything that kills him."""
        #Bad encapsulation! I shouldn't mix game logic with physics
        for critter in self.level.creatures:
            if _hit(self.player, critter):
                self.player.dead = True
                return

    def projectile_collisions(self):
        """Checks if anyone has run into a projectile."""
        for critter in self.level.creatures:
            if pygame.sprite.spritecollide(critter, self.friendly_projectiles, True, _hit):
                critter.take_a_hit()
        if pygame.sprite.spritecollide(self.player, self.enemy_projectiles, True, _hit):
            self.player.dead = True

    def platform_collisions(self):
        """Ensures everyone is stopped by a platform (and doesn't go through it)."""
        platforms = self.level.platforms.sprites()
        positions = [p.position for p in platforms]
        for critter in self.level.creatures.sprites() + [self.player]:
            #Search everything the critter could touch along this frame's
            #whole movement, so that fast movers can't tunnel through thin
            #platforms. inflate(2, 2) grows the search area by one pixel per
            #side so platforms the critter is resting flush against count too.
            swept = critter.position.union(critter.desired_position).inflate(2, 2)
            nearby = [platforms[i] for i in swept.collidelistall(positions)]
            self._perform_collisions(critter, nearby)

    def _perform_collisions(self, critter, platforms):
        """Clamps the critter's desired position so that it stops flush
           against any platform in its way, resolving the horizontal axis
           first and then the vertical axis."""
        pos = critter.position
        des = critter.desired_position
        solid = [p.position for p in platforms
                 if not (isinstance(critter, Player) and
                         isinstance(p, InvisiblePlatform))]
        critter.landed = False

        for plat in solid:
            if pos.colliderect(plat):
                #Already overlapping (e.g. spawned inside a wall) -- rescue it
                #rather than trying to resolve its movement normally.
                self._unstick(critter, plat)
                return

        #Horizontal
        dx = des.x - pos.x
        hit_wall = False
        for plat in solid:
            if plat.top >= pos.bottom or plat.bottom <= pos.top:
                continue #Not level with the critter; can't block it sideways
            if dx > 0 and pos.right <= plat.left and des.right > plat.left:
                des.right = plat.left
                hit_wall = True
            elif dx < 0 and pos.left >= plat.right and des.left < plat.right:
                des.left = plat.right
                hit_wall = True
        if hit_wall:
            critter.hitwall()

        #Vertical (using the already-clamped horizontal extent)
        dy = des.y - pos.y
        for plat in solid:
            if plat.left >= des.right or plat.right <= des.left:
                continue #Not above or below the critter; can't block it
            if dy > 0 and pos.bottom <= plat.top and des.bottom > plat.top:
                des.bottom = plat.top
                critter.velocity.y = 0
                critter.landed = True
                critter.jumping = False
            elif dy < 0 and pos.top >= plat.bottom and des.top < plat.bottom:
                des.top = plat.bottom
                critter.velocity.y = 0
            elif dy >= 0 and pos.bottom == plat.top:
                #Resting exactly on top of the platform; stay "landed" even on
                #frames where gravity rounds to zero pixels of movement.
                critter.landed = True
                critter.jumping = False

    def _unstick(self, critter, platform):
        """Pushes a critter that is already inside a platform back out, along
           the axis of least penetration."""
        pos = critter.position
        des = critter.desired_position
        penetration = {"up"   : pos.bottom - platform.top,
                       "down" : platform.bottom - pos.top,
                       "left" : pos.right - platform.left,
                       "right": platform.right - pos.left}
        direction = min(penetration, key=penetration.get)
        if direction == "up":
            des.bottom = platform.top
            critter.velocity.y = 0
            critter.landed = True
            critter.jumping = False
        elif direction == "down":
            des.top = platform.bottom
            critter.velocity.y = 0
        elif direction == "left":
            des.right = platform.left
        else:
            des.left = platform.right

