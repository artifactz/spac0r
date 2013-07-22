#!/usr/bin/env python

import pygame
import random
import numpy
import math
import copy
import world

class Camera:
    def __init__(self, screen_size, x, y):
        self.screen_size = copy.deepcopy(screen_size)
        self.half_screen_size = (screen_size[0] / 2, screen_size[1] / 2)
        self.position = [x, y]

    def get_offset(self):
        return (self.half_screen_size[0] - self.position[0], self.half_screen_size[1] - self.position[1])

    def move(self, x, y):
        self.position[0] += x
        self.position[1] += y

class Drawer:
    def __init__(self, surface, camera):
        self.camera = camera
        self.surface = surface
        self.font_sans = pygame.font.Font('freesansbold.ttf', 13)
        self.col_black = pygame.Color(0, 0, 0)
        self.col_white = pygame.Color(255, 255, 255)
        self.col_red   = pygame.Color(255, 0, 0)

    def draw_star(self, star, pix):
        (x, y, z) = tuple(star.position)
        x = (x - self.camera.position[0]) / float(z) + self.camera.half_screen_size[0]
        y = (y - self.camera.position[1]) / float(z) + self.camera.half_screen_size[1]
        if x >= 0 and x < self.camera.screen_size[0] and y >= 0 and y < self.camera.screen_size[1]:
            #pygame.draw.line(self.surface, pygame.Color(star.color[0], star.color[1], star.color[2]), (x, y), (x, y), 1)
            pix[int(x)][int(y)] = (star.color[0], star.color[1], star.color[2])
            return True
        else:
            return False

    def draw_background(self, background):
        pix = pygame.PixelArray(self.surface)
        for star in background.stars:
            if not self.draw_star(star, pix):
                star.reset(self.camera)
        del pix

    def draw_part(self, part, dx, dy, rotation):
        if part.look == 'Chassis One':
            pygame.draw.lines(self.surface, )

    def draw_spacecraft(self, spacecraft):
        for i in xrange(0, len(spacecraft.parts)):
            dx = spacecraft.position[0] + numpy.cos(spacecraft.draw_hints[i][0] + spacecraft.rotation) * spacecraft.draw_hints[i][1]
            dy = spacecraft.position[1] + numpy.sin(spacecraft.draw_hints[i][0] + spacecraft.rotation) * spacecraft.draw_hints[i][1]
            self.draw_part(spacecraft.parts(i), dx, dy, spacecraft.rotation + spacecraft.draw_hints[i][2])
