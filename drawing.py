#!/usr/bin/env python

import pygame
import random
import math
import copy
import world
import engine

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

    def draw_background(self, background, pix_anti_alias = True):
        '''Draws the background (stars that is).
        If pix_anti_alias is set to True, real pixel anti-aliasing is used (slow),
        if set to False, the method uses short aa-lines to mimic pixels (fast).'''
        pix = pygame.PixelArray(self.surface)
        w = len(pix)
        h = len(pix[0])
        for star in background.stars:
            x = (star.position[0] - self.camera.position[0]) / float(star.position[2]) + self.camera.half_screen_size[0]
            y = (star.position[1] - self.camera.position[1]) / float(star.position[2]) + self.camera.half_screen_size[1]
            if x >= 0 and x < self.camera.screen_size[0] and y >= 0 and y < self.camera.screen_size[1]:
                # real pixel AA
                if pix_anti_alias:
                    dx = x - math.floor(x)
                    dy = y - math.floor(y)
                    dx1 = (1 - dx)
                    dy1 = (1 - dy)
                    ix = int(math.floor(x))
                    iy = int(math.floor(y))
                    c0x1 = star.color[0] * dx1
                    c0y1 = star.color[0] * dy1
                    c1x1 = star.color[1] * dx1
                    c1y1 = star.color[1] * dy1
                    c2x1 = star.color[2] * dx1
                    c2y1 = star.color[2] * dy1
                    c0x0 = star.color[0] * dx
                    c0y0 = star.color[0] * dy
                    c1x0 = star.color[1] * dx
                    c1y0 = star.color[1] * dy
                    c2x0 = star.color[2] * dx
                    c2y0 = star.color[2] * dy
                    pix[ix][iy] = ((c0x1 + c0y1) / 2, (c1x1 + c1y1) / 2, (c2x1 + c2x1) / 2)
                    if ix + 1 < w:
                        pix[ix + 1][iy] = ((c0x0 + c0y1) / 2, (c1x0 + c1y1) / 2, (c2x0 + c2x1) / 2)
                    else:
                        continue
                    if iy + 1 < h:
                        pix[ix][iy + 1] = ((c0x1 + c0y0) / 2, (c1x1 + c1y0) / 2, (c2x1 + c2y0) / 2)
                    else:
                        continue
                    pix[ix + 1][iy + 1] = ((c0x0 + c0y0) / 2, (c1x0 + c1y0) / 2, (c2x0 + c2y0) / 2)
                else:
                    # fake pixel AA
                    pygame.draw.aaline(self.surface, pygame.Color(star.color[0], star.color[1], star.color[2]), (x - 0.5, y), (x + 0.5, y + 0.1))
            else:
                star.reset(self.camera)
        del pix

    def draw_transformed_line(self, color, (x1, y1), (x2, y2), dx, dy, rotation):
        '''applies rotation, then translation, then draws the line.'''
        cos = math.cos(rotation)
        sin = math.sin(rotation)
        pygame.draw.aaline(self.surface, color, (cos * x1 + sin * y1 + dx, cos * y1 - sin * x1 + dy), (cos * x2 + sin * y2 + dx, cos * y2 - sin * x2 + dy))

    def draw_particles(self, particles):
        pix = pygame.PixelArray(self.surface)
        w = len(pix)
        h = len(pix[0])
        for particle in particles:
            # TODO
            pass
        del pix

    def draw_shot(self, shot):
        off = self.camera.get_offset()
        alpha = min(int(shot.ttl * 400.0), 255)
        engine.draw_line_alpha(self.surface, pygame.Color(0, 255, 0),
            (off[0] + shot.shapes[0].real_start[0], off[1] + shot.shapes[0].real_start[1]),
            (off[0] + shot.shapes[0].real_end[0], off[1] + shot.shapes[0].real_end[1]), alpha)

    def draw_spacecraft(self, spacecraft):
        off = self.camera.get_offset()
        for part in spacecraft.parts:
            for shape in part.shapes:
                if isinstance(shape, world.Line):
                    pygame.draw.aaline(self.surface, shape.color,
                        (shape.real_start[0] + off[0], shape.real_start[1] + off[1]), (shape.real_end[0] + off[0], shape.real_end[1] + off[1]))
