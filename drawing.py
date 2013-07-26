#!/usr/bin/env python

import pygame
import random
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
        self.col_green = pygame.Color(0, 255, 0)

    def draw_star(self, star, pix):
        (x, y, z) = tuple(star.position)
        x = (x - self.camera.position[0]) / float(z) + self.camera.half_screen_size[0]
        y = (y - self.camera.position[1]) / float(z) + self.camera.half_screen_size[1]
        if x >= 0 and x < self.camera.screen_size[0] and y >= 0 and y < self.camera.screen_size[1]:
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

    def draw_transformed_line(self, color, (x1, y1), (x2, y2), dx, dy, rotation):
        '''applies rotation, then translation, then draws the line.'''
        cos = math.cos(rotation)
        sin = math.sin(rotation)
        pygame.draw.aaline(self.surface, color, (cos * x1 + sin * y1 + dx, cos * y1 - sin * x1 + dy), (cos * x2 + sin * y2 + dx, cos * y2 - sin * x2 + dy))

    def draw_shot(self, shot):
        off = self.camera.get_offset()
        self.draw_transformed_line(self.col_green, (0, 0), (shot.speed[0] * 100, shot.speed[1] * 100), shot.position[0] + off[0], shot.position[1] + off[1], 0)

    def draw_spacecraft(self, spacecraft):
        off = self.camera.get_offset()
        for part in spacecraft.parts:
            for shape in part.shapes:
                if isinstance(shape, world.Line):
                    pygame.draw.aaline(self.surface, shape.color,
                        (shape.real_start[0] + off[0], shape.real_start[1] + off[1]), (shape.real_end[0] + off[0], shape.real_end[1] + off[1]))
