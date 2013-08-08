#!/usr/bin/env python

import pygame
from pygame.locals import *
import random
import math
import time
import copy
import lightning
import world
import drawing
import engine


SCREEN_SIZE = [1024, 700] # [1366, 768]

pygame.init()
pygame.display.set_caption('Spac0r')
fps_clock = pygame.time.Clock()
surf_display = pygame.display.set_mode(SCREEN_SIZE, DOUBLEBUF, 32) # FULLSCREEN
surf_display.set_alpha(None)
surf_fps = None
w = world.World(SCREEN_SIZE)
camera = drawing.Camera(SCREEN_SIZE, 0.0, 0.0)
drawer = drawing.Drawer(surf_display, camera)

mouse_pos = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
key_pressed = [False for x in xrange(0, 512)]
mouse_pressed = [False for x in xrange(0, 6)]

processing_tick = time.time()

while True:
    # calculate camera position and player rotation from mouse position
    v = [mouse_pos[0] - SCREEN_SIZE[0] / 2.0, mouse_pos[1] - SCREEN_SIZE[1] / 2.0]
    drawer.camera.position[0] = w.player.position[0] + v[0] * 0.9
    drawer.camera.position[1] = w.player.position[1] + v[1] * 0.9
    w.player.rotate(math.atan2(-v[1], v[0]))

    # draw things that don't need to be processed further
    surf_display.fill(drawer.col_black)
    drawer.draw_background(w.background, False)     # True for perfect anti-alias, False for performance
    for planet in w.planets:
        drawer.draw_planet(planet)

    # processing
    current_time = time.time()
    timespan = current_time - processing_tick
    processing_tick = current_time
    for mutable in w.mutable:
        mutable.process(timespan)
    # check if decayed
    for decayable in w.decayable:
        if decayable.ttl == 0:
            w.remove_entity(decayable)
    # collision detection
    processed = []
    for collidable1 in w.collidable:
        processed.append(collidable1)
        for collidable2 in w.collidable:
            if not collidable2 in processed:
                pos = world.collides(collidable1.shapes, collidable2.shapes)
                if pos:
                    if isinstance(collidable1, world.Spacecraft) and isinstance(collidable2, world.Shot):
                        if not collidable2.origin == collidable1:
                            w.spacecraft_hit_by_shot(collidable1, collidable2, pos)
                    if isinstance(collidable1, world.Shot) and isinstance(collidable2, world.Spacecraft):
                        if not collidable1.origin == collidable2:
                            w.spacecraft_hit_by_shot(collidable2, collidable1, pos)
    # check if spacecraft's still living
    for spacecraft in w.spacecrafts:
        if spacecraft.stats.hit_points <= 0:
            spacecraft.explode(w)

    # draw processed things
    for spacecraft in w.spacecrafts:
        drawer.draw_spacecraft(spacecraft)
    for shot in w.shots:
        drawer.draw_shot(shot)
    drawer.draw_particles(w.particles)

    drawer.draw_lens_flares()

    # render fps and update display
    surf_fps = drawer.font_sans.render('%.1f' % fps_clock.get_fps(), True, drawer.col_red)
    surf_display.blit(surf_fps, (1, -2))
    surf_info = drawer.font_sans.render('engine surfaces: ' + str(len(engine.surf_alpha) + len(engine.surf_scale)), True, drawer.col_red)
    surf_display.blit(surf_info, (1, 10))
    pygame.display.update()

    # events
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
            pygame.quit()
            exit(0)
        if event.type == KEYDOWN:
            key_pressed[event.key] = True
        if event.type == KEYUP:
            key_pressed[event.key] = False
        if event.type == MOUSEMOTION:
            mouse_pos = copy.deepcopy(event.pos)
        if event.type == MOUSEBUTTONDOWN:
            mouse_pressed[event.button] = True
        if event.type == MOUSEBUTTONUP:
            mouse_pressed[event.button] = False
    # controls
    if key_pressed[K_w]:
        w.player.steer_straight()
    if key_pressed[K_s]:
        w.player.steer_back()
    if key_pressed[K_a]:
        w.player.steer_left()
    if key_pressed[K_d]:
        w.player.steer_right()

    if mouse_pressed[1]:
        w.player.shoot(w)

    fps_clock.tick(100)
