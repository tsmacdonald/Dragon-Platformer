#/usr/bin/env python

#    Copyright 2011 Tim Macdonald <tsmacdonald@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

profiling = False

import os, pygame, creatures, levels, engine, controls, things
from utils import Vector
from pygame.locals import *
from constants import *
if DEBUG: import pdb

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

def deal_with_keys(key, player, projectiles):
    window_offset = 0

    #Movement
    if key[controls.RIGHT]:
        player.go_right()
    elif key[controls.LEFT]:
        player.go_left()
    else:
        player.stand_still()

    #Shooting
    if key[controls.SHOOT]:
        player.fire(projectiles, "down" if key[controls.DOWN] else None)
        player.reload_wait = .45
    else:
        player.reload_wait = .16

    #Jumping
    if key[controls.JUMP]:
        player.jump()
    if key[controls.FLAP]:
        player.flap()
    else:
        player.unflap()

    #Looking
    if player.velocity.x == 0 and player.landed:
        if key[controls.LOOK_DOWN]:
            window_offset += 12
        if key[controls.LOOK_UP]:
            window_offset -= 11
    else:
        window_offset = 0
    return window_offset

def message(text, color, size, font, position, screen, point = "topleft"):
    if pygame.font:
        font = pygame.font.Font(font, size)
        text = font.render(text, True, color)
        rect = text.get_rect()
        exec("rect.%s = position"%point)
        screen.blit(text, rect)
    else: print "No font! Can't display text in HUD.\nMessage was:", text

def draw_HUD(screen, player, clock):
    elements = (player.points, player.shots, player.lives, int(clock.get_fps()))
    offset = 20
    for msg, y in zip(elements, range(0, offset * len(elements), offset)):
        message(str(msg), (255, 0, 0), 36, None, (0, y), screen)

def kill_player(player, level, level_list, active_things, engine, window, screen):
    level = level_list.same_level()
    engine.level = level
    engine.player = player
    player.position.topleft = level.starting_pos
    player.velocity.x = player.velocity.y = 0
    player.jumping = False
    player.lives -= 1
    if player.lives < 0:
        message("Game Over!",
                (255, 0, 0), 36, None, (window.width / 2, window.height / 2),
                screen, "center")
        pygame.display.flip()
        pygame.time.wait(1 * 3000)
        import sys; sys.exit(0)
    else:
        message("You have died!",
                (255, 0, 0), 36, None, (window.width / 2, window.height / 2),
                 screen, "center")
        pygame.display.flip()
        pygame.time.wait(1 * 2000)
        player.dead = False #Resurrection!
    return level


    

def main():
    """Main loop. Initializes everything and runs continuously until the game ends or is quit.""" 
    pygame.init()
    screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    pygame.mouse.set_visible(False)

    
    #Game Objects:
    window = pygame.Rect(0, 0, WIDTH, HEIGHT)
    clock = pygame.time.Clock()
    
    player = creatures.Player("new_dragon.png", position = [0, HEIGHT], velocity = [0, 0])
    
    active_things = pygame.sprite.Group(player)
    friendly_projectiles = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()

    level_list = levels.LevelList()
    level = level_list.next_level()
    level = levels.Level("level1")
    level.set_starting_position(player)
    eng = engine.Engine(player, level, friendly_projectiles, enemy_projectiles)
    active_tiles = pygame.sprite.Group()
    motion_counter = 0
    creatures_moving = False

    pygame.display.flip()

    window = pygame.Rect(max(player.position.x - (WIDTH / 2), 0), #x
                         player.position.bottom - HEIGHT + VERT_BUFFER, #y
                         WIDTH, HEIGHT)
#Main Loop
    while True:
        clock.tick(FPS)
        
        #Fix window / active creatures/things
        active_things.empty()

        if creatures_moving == False and motion_counter < 10:
            motion_counter += 1
        if motion_counter >= 9 and creatures_moving == False:
            for creature in level.creatures:
                creature.velocity.x = creature.default_velocity.x
                creature.velocity.y = creature.default_velocity.y
                creature.acceleration.y = GRAVITY
            creatures_moving = True
 
        window_offset = deal_with_keys(pygame.key.get_pressed(), player, friendly_projectiles)        
        window.y += window_offset
       
        potential_bottom = player.position.bottom + VERT_BUFFER
        window.bottom = max(potential_bottom, window.bottom)

        window.left = max(player.position.centerx - (WIDTH / 2), 0)
        window.right = min(window.right, level.width)
        window.top = min(window.top, player.position.top - (HEIGHT / 6))
        window.top = max(window.top, 0)
        window.bottom = min(window.bottom, level.height + VERT_BUFFER)
        
        for thing in (level.creatures.sprites() + [player] + friendly_projectiles.sprites() +
                      enemy_projectiles.sprites() + level.powerups.sprites() + [level.exit]):
             if thing.position.colliderect(window):
                active_things.add(thing)

       # Collision with powerups
        for thing in level.powerups.sprites():
            if thing.position.colliderect(player.position):
                thing.use(player)
                level.powerups.remove(thing)
        for projectiles in friendly_projectiles, enemy_projectiles:
            for bullet in projectiles.sprites():
                for platform in level.platforms.sprites():
                    if bullet.position.colliderect(platform.position) and not isinstance(platform, things.InvisiblePlatform):
                        projectiles.remove(bullet)
 
        #Check for death / completion
        level.creatures.remove(filter(lambda x: x.dead, level.creatures))
        if player.dead:
            level = kill_player(player, level, level_list, active_things, eng, window, screen)
            creatures_moving = False
            motion_counter = 0
            clock.tick()
            continue
        key = pygame.key.get_pressed()
        if (key[controls.QUIT]):
            return
        if (key[controls.SKIP] and not skipping) or player.position.colliderect(level.exit.position):
            skipping = True
            active_things.empty()
            active_things.add(player)
            level.creatures.empty()
            level.platforms.empty()
            player.velocity.x = player.velocity.y = 0
            player.jumping = False
            creatures_moving = False
            level = level_list.next_level()
            eng.level = level
            eng.player = player
            player.position.topleft = level.starting_pos
            motion_counter = 0
            clock.tick()
            continue
        else:
            skipping = False

        #Input
        for event in pygame.event.get():
            if event.type == QUIT:
                return
        

        #Update
        # Gives the creatures and platforms a chance to do something cool.
        # Currently, all that means is that they set their relative position
        active_things.update(window, enemy_projectiles)
        level.platforms.update(window)
        #level.background.set_relative_position(window)
        
        #Collision detection / physics / etc.
        time = clock.get_time()
        eng.update(time) 

        player.tick(time)

       #Draw Everything
        #pygame.sprite.Group(level.background).draw(screen)
        active_tiles.empty()
        for tile in level.tiles.sprites():
            if tile.position.colliderect(window):
                active_tiles.add(tile)
        active_tiles.update(window)
        active_tiles.draw(screen)
        #print clock.get_fps()
        level.platforms.draw(screen)
        active_things.draw(screen)
        draw_HUD(screen, player, clock)
        pygame.display.flip()

#Game Over


if __name__ == '__main__':
    if profiling:
        import cProfile as profile
        profile.run("main()", "profile_output.cprof", sort=1)
    else:
        main()
