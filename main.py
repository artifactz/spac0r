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


SCREEN_SIZE = [1024, 700]

#class Star:
#    def __init__(self):
#        self.position = map(int, [random.random() * SCREEN_SIZE[0], random.random() * SCREEN_SIZE[1]])
#        self.randomize_speed()
#
#    def randomize_speed(self):
#        self.speed = random.random() * random.random() * random.random() * 0.5 + 0.03
#
#    def reset(self):
#        self.randomize_speed()
#        self.position[1] = -1
#
#    def draw(self, surf):
#        c = int(255.0 * self.speed / 0.53)
#        pygame.draw.line(surf, pygame.Color(c, c, c), self.position, self.position, 1)

#class Planet(Star):
#    def __init__(self):
#        Star.__init__(self)
#        self.image = surf_planet1
#        self.randomize_speed()
#
#    def randomize_speed(self):
#        self.speed = random.random() * random.random() * random.random() * 2 + 1
#        self.image = pygame.transform.rotozoom(surf_planet1, 0, self.speed / 3 * 0.1)
#
#    def reset(self):
#        self.randomize_speed()
#        self.position[0] = random.random() * (SCREEN_SIZE[0] - self.image.get_width()) - self.image.get_width()
#        self.position[1] = -100 - random.random() * 200
#
#    def draw(self, surf):
#        # size of object image
#        w = self.image.get_width()
#        h = self.image.get_height()
#        # draw object itself
#        surf.blit(self.image, (self.position[0] - w / 2, self.position[1] - h / 2))
#        # draw lens flare
#        visibility = count_overlapping_pixels((self.position[0] - w / 2, self.position[1] - h / 2, self.position[0] + w / 2, self.position[1] + h / 2), (0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]))
#        visibility /= 1000
#        visibility = min(visibility, 1)
#        lighter.draw_lens_flare(surf, self.position[0], self.position[1], visibility, True)

def count_overlapping_pixels(rect1, rect2):
    rect3 = (max(rect1[0], rect2[0]), max(rect1[1], rect2[1]), min(rect1[2], rect2[2]), min(rect1[3], rect2[3]))
    if rect3[0] > rect3[2] or rect3[1] > rect3[3]:
        return 0
    else:
        return (rect3[2] - rect3[0]) * (rect3[3] - rect3[1])


pygame.init()
pygame.display.set_caption('Spac0r')
fps_clock = pygame.time.Clock()
surf_display = pygame.display.set_mode(SCREEN_SIZE)
surf_fps = None
#surf_planet1 = pygame.image.load('img/planet1.png')
w = world.World(SCREEN_SIZE)
camera = drawing.Camera(SCREEN_SIZE, 0.0, 0.0)
drawer = drawing.Drawer(surf_display, camera)
#lighter = lightning.Lightning()

mouse_pos = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
key_pressed = [False for x in xrange(0, 512)]

#planets = []
#planets.append(Planet())

while True:
    # calculate camera position and player rotation from mouse position
    v = [mouse_pos[0] - SCREEN_SIZE[0] / 2.0, mouse_pos[1] - SCREEN_SIZE[1] / 2.0]
    drawer.camera.position[0] = w.player.position[0] + v[0] * 0.9
    drawer.camera.position[1] = w.player.position[1] + v[1] * 0.9
    w.player.rotation = math.atan2(-v[1], v[0])

    surf_display.fill(drawer.col_black)

    drawer.draw_background(w.background)

    drawer.draw_spacecraft(w.player)

    if key_pressed[K_w]:
        w.player.speed[0] += math.cos(w.player.rotation)
        w.player.speed[1] -= math.sin(w.player.rotation)

    if key_pressed[K_s]:
        w = world.World(SCREEN_SIZE)

    w.player.process()

#    for planet in planets:
#        planet.draw(surf_display)
#        planet.position[1] += planet.speed
#        if planet.position[1] > SCREEN_SIZE[1]:
#            planet.reset()

    surf_fps = drawer.font_sans.render('%.1f' % fps_clock.get_fps(), False, drawer.col_red)
    surf_display.blit(surf_fps, (1, -2))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit(0)
        if event.type == KEYDOWN:
            key_pressed[event.key] = True
        if event.type == KEYUP:
            key_pressed[event.key] = False
        if event.type == MOUSEMOTION:
            mouse_pos = copy.deepcopy(event.pos)

    pygame.display.update()
    fps_clock.tick(500)
