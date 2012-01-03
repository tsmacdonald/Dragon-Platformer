import pygame, constants
from copy import copy
from creatures import Creature, Player
from things import InvisiblePlatform, Trap

class Engine():
    def __init__(self, player, level, friendly_projectiles, enemy_projectiles):
        self.player = player
        self.level = level
        self.friendly_projectiles = friendly_projectiles
        self.enemy_projectiles = enemy_projectiles

    def move_everyone(self):
        for c in (self.level.creatures.sprites() +
                [self.player] + self.enemy_projectiles.sprites() + self.friendly_projectiles.sprites()):
            c.position = copy(c.desired_position)

    def update(self, time):
        self.kinematics(time)
        self.do_collisions()
        self.move_everyone()
    
    def kinematicize(self, critter, time):
        critter.desired_position.x = critter.position.x + (critter.velocity.x * time)
        critter.desired_position.y = critter.position.y + (critter.velocity.y * time)
        critter.velocity.x += critter.acceleration.x * time
        critter.velocity.y += critter.acceleration.y * time
            
    def kinematics(self, time):
        time /= 1000.0 #milliseconds to seconds
        for critter in (self.level.creatures.sprites() +
                        self.enemy_projectiles.sprites() + self.friendly_projectiles.sprites() + [self.player]):
            self.kinematicize(critter, time)
    
    def do_collisions(self):
        self.projectile_collisions()
        self.platform_collisions()
        self.player_death_collision()

    def player_death_collision(self):
        if self.player.position.collidelist([x.position for x in self.level.creatures.sprites()]) != -1:
            self.player.dead = True
        #x = pygame.sprite.spritecollide(self.player, self.level.creatures, False)
        #if x:
        #    print x[0].rect.bottom, self.player.rect.top
        #    self.player.dead = True

    def projectile_collisions(self):
        for critter in self.level.creatures:
            if pygame.sprite.spritecollide(critter, self.friendly_projectiles, True):
                critter.take_a_hit()
        if pygame.sprite.spritecollide(self.player, self.enemy_projectiles, True):
            self.player.dead = True
            

    def platform_collisions(self):
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
        #x_mask = pygame.mask.from_surface(critter)
        #y_mask = pygame.mask.from_surface(critter)
        des_x = pygame.rect.Rect(critter.desired_position)
        des_x.top = critter.position.top
        des_y = pygame.rect.Rect(critter.desired_position)
        des_y.right = critter.position.right
        for platform in platforms:
            if isinstance(critter, Player) and isinstance(platform, InvisiblePlatform):
                continue
            if des_x.colliderect(platform.position):    
                if True: #pygame.sprite.collide_mask(critter, platform):
                    critter.desired_position.x = critter.position.x
                    #critter.velocity.x = 0
                    critter.hitwall()
            if des_y.colliderect(platform.position):
                if True: #pygame.sprite.collide_mask(critter, platform):
                   if critter.down_p():
                        critter.landed = True
                   critter.desired_position.top = critter.position.top
                   critter.velocity.y = 0
                   critter.jumping = False

