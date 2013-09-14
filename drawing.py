#!/usr/bin/env python

import pygame
import random
import math
import copy
import world
import engine
import lightning

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
        self.surf_planet1 = pygame.image.load('img/planet1.png')
        self.surf_planet1_small = pygame.transform.scale(self.surf_planet1, (48, 48))
        self.lighter = lightning.Lightning()
        self.lens_flares = []

    def place_lens_flare(self, x, y, intensitiy):
        if intensitiy > 0:
            self.lens_flares.append((x, y, intensitiy))

    def draw_lens_flares(self):
        for flare in self.lens_flares:
            self.lighter.draw_lens_flare(self.surface, flare[0], flare[1], flare[2], True)
        self.lens_flares = []

    def draw_background(self, background, pix_anti_alias = True):
        '''Draws the background (stars that is).
        If pix_anti_alias is set to True, real pixel anti-aliasing is used (slow),
        if set to False, the method uses short aa-lines to mimic pixels (fast).'''
        if pix_anti_alias:
            pix = pygame.PixelArray(self.surface)
            w = len(pix)
            h = len(pix[0])
        else:
            (w, h) = self.surface.get_size()
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
        if pix_anti_alias:
            del pix

    def draw_planet(self, planet):
        w = self.surf_planet1_small.get_width() * planet.size
        h = self.surf_planet1_small.get_height() * planet.size
        surf = engine.get_scale_surface(self.surf_planet1_small, w, h)
        x = (planet.position[0] - w / 2 - self.camera.position[0]) * .5 + self.camera.half_screen_size[0]
        y = (planet.position[1] - h / 2 - self.camera.position[1]) * .5 + self.camera.half_screen_size[1]
        # draw planet itself
        rect = self.surface.blit(surf, (x, y))
        intensitiy = rect.width * rect.height / float(self.surf_planet1_small.get_width() * self.surf_planet1_small.get_height())
        intensitiy = 1 - (1 - intensitiy)**2
        self.place_lens_flare(rect.left + rect.width / 2, rect.top + rect.height / 2, intensitiy)

    def draw_transformed_line(self, color, (x1, y1), (x2, y2), dx, dy, rotation):
        '''applies rotation, then translation, then draws the line.'''
        cos = math.cos(rotation)
        sin = math.sin(rotation)
        pygame.draw.aaline(self.surface, color, (cos * x1 + sin * y1 + dx, cos * y1 - sin * x1 + dy), (cos * x2 + sin * y2 + dx, cos * y2 - sin * x2 + dy))

    def draw_particles(self, particles):
        pix = pygame.PixelArray(self.surface)
        w = len(pix)
        h = len(pix[0])
        off = self.camera.get_offset()
        for particle in particles:
            x = int(particle.position[0] + off[0])
            y = int(particle.position[1] + off[1])
            if x >= 0 and x < w and y >= 0 and y < h:
                alpha = min(particle.ttl, 1)
                col = pygame.Color(pix[x][y])
                pix[x][y] = (min(int(col.r + particle.color[0] * alpha), 255),
                    min(int(col.g + particle.color[1] * alpha), 255),
                    min(int(col.b + particle.color[2] * alpha), 255))
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
                if isinstance(shape, world.Circle):
                    #pygame.draw.circle(self.surface, shape.color, (int(shape.real_center[0] + off[0]), int(shape.real_center[1] + off[1])), int(shape.radius), 1)
                    engine.draw_aa_circle(self.surface, shape.color, (shape.real_center[0] + off[0], shape.real_center[1] + off[1]), int(shape.radius), 16)
