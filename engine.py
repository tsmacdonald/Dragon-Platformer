import pygame, constants
from copy import copy
from creatures import Creature, Player
from things import InvisiblePlatform, Trap

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
        if self.player.position.collidelist([x.position for x in self.level.creatures.sprites()]) != -1:
            self.player.dead = True

    def projectile_collisions(self):
        """Checks if anyone has run into an enemy projectile."""
        for critter in self.level.creatures:
            if pygame.sprite.spritecollide(critter, self.friendly_projectiles, True):
                critter.take_a_hit()
        if pygame.sprite.spritecollide(self.player, self.enemy_projectiles, True):
            self.player.dead = True
            

    def platform_collisions(self):
        """Ensures everyone is stopped by a platform (and doesn't go through it)."""
        platform_positions = []
        for x in self.level.platforms: platform_positions.append(x.position)
        for critter in self.level.creatures.sprites() + [self.player]:
            plat_indices = critter.desired_position.collidelistall(platform_positions)
            plats = [self.level.platforms.sprites()[i] for i in plat_indices]
            if len(plats) > 0:
                self._perform_collisions(critter, plats)
            else:
                critter.landed = False

    def _perform_collisions(self, critter, platforms):
        """Determines if the given critter is intersecting any platforms, and sets
           the desired position appropriately."""
        des_x = pygame.rect.Rect(critter.desired_position)
        des_x.top = critter.position.top
        des_y = pygame.rect.Rect(critter.desired_position)
        des_y.right = critter.position.right
        for platform in platforms:
            if (isinstance(critter, Player) and
                isinstance(platform, InvisiblePlatform)):
                continue #Player can't get stopped by invisible platforms
            if des_x.colliderect(platform.position):    
                critter.desired_position.x = critter.position.x
                critter.hitwall()
            if des_y.colliderect(platform.position):
               if critter.down_p():
                    critter.landed = True
               critter.desired_position.top = critter.position.top
               critter.velocity.y = 0
               critter.jumping = False

