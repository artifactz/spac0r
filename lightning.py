#!/usr/bin/env python
'''Lightning engine.'''

import pygame
from pygame.locals import *
import random
#import numpy
import math
import flaregen
import engine
import time

class Lightning:
    def __init__(self):
        '''Loads and generates needed textures.'''
        self.surf_nova = pygame.image.load('img/nova.png')
        self.surf_flare1 = pygame.image.load('img/flare1.png')
        self.surf_flare2 = flaregen.gen_texture(64, flaregen.INNERBLUR2, (128, 255, 0), 32)
        self.surf_flare3 = flaregen.gen_texture(115, flaregen.INNERBLUR3, (58, 100, 240), 20)
        self.surf_flare4 = flaregen.gen_texture(30, flaregen.INNERBLUR3, (145, 45, 240), 25)
        self.surf_flare5 = flaregen.gen_texture(38, flaregen.INNERBLUR3, (50, 85, 255), 20)
        self.surf_flare6 = flaregen.gen_texture(35, flaregen.INNERBLUR3, (255, 115, 0), 32)
        self.surf_flare7 = flaregen.gen_texture(7, flaregen.OUTERBLUR, (100, 255, 190), 60)
        self.surf_flare8 = flaregen.gen_texture(17, flaregen.OUTERBLUR, (100, 255, 190), 58)
        self.surf_flare9 = flaregen.gen_texture(128, flaregen.INNERBLUR2, (255, 146, 0), 27)
        self.surf_flare10 = flaregen.gen_texture(50, flaregen.INNERBLUR3, (255, 100, 0), 24)
        self.surf_flare11 = flaregen.gen_texture(22, flaregen.INNERBLUR3, (255, 146, 0), 20)
        self.surf_flare12 = flaregen.gen_texture(45, flaregen.INNERBLUR3, (80, 255, 167), 30)
        self.surf_flare13 = flaregen.gen_texture(32, flaregen.OUTERBLUR, (0, 0, 255), 24)
        self.surf_flare14 = flaregen.gen_texture(140, flaregen.INNERBLUR2, (134, 255, 0), 23)
        self.surf_flare15 = flaregen.gen_texture(300, flaregen.RING, (255, 0, 0), 12)
        self.surf_flare16 = flaregen.gen_texture(292, flaregen.RING, (0, 255, 0), 11)
        self.surf_flare17 = flaregen.gen_texture(284, flaregen.RING, (0, 0, 255), 13)
        self.surf_flare18 = flaregen.gen_texture(47, flaregen.OUTERBLUR, (255, 185, 255), 20)
        self.surf_flare19 = flaregen.gen_texture(10, flaregen.OUTERBLUR, (128, 185, 255), 20)
        self.surf_flare20 = flaregen.gen_texture(20, flaregen.OUTERBLUR, (100, 255, 215), 50)
        self.surf_flare21 = flaregen.gen_texture(21, flaregen.INNERBLUR3, (255, 100, 130), 48)

    def draw_lens_flare(self, surf, x, y, intensity, flicker = True):
        '''Draws a lens flare on a given surface: surf at position: x, y with intensity: intensity.
        If flicker is set to True, intensity will be slightly modified by some sine functions.'''

        intensity = float(intensity)
        
        # TODO flicker multiplicative!

        # display size
        disp_size = surf.get_size()
        # vector from center to object
        vx = x - disp_size[0] / 2
        vy = y - disp_size[1] / 2
        # ratio of visible pixels
        #visibility = count_overlapping_pixels((self.position[0] - w / 2, self.position[1] - h / 2, self.position[0] + w / 2, self.position[1] + h / 2), (0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1])) / (w * h)
        visibility = intensity
        # angle from center
        at2 = math.atan2(vy, vx) #numpy.arctan2(vy, vx)
        if at2 < 0:
            at2 += math.pi * 2
        deg = at2 * 180.0
        # NOVA
        n = pygame.transform.rotozoom(self.surf_nova, deg, visibility / 4)
        s = n.get_size()
        surf.blit(n, (x - s[0] / 2, y - s[1] / 2))
        # LENS FLARE
        # a lil sine flicker
        flicker = math.sin(time.time() * 20.0) + math.sin(time.time() * 17.0) + math.sin(time.time() * 24.37) * visibility * 10.0
        visibility = int(visibility * 255.0 + flicker - 15.0)
        visibility = max(0, visibility)
        s = self.surf_flare1.get_size()
        engine.blit_alpha(surf, self.surf_flare1, (x - s[0] / 2, y - s[1] / 2), visibility)
        s = self.surf_flare2.get_size()
        engine.blit_alpha(surf, self.surf_flare2, (disp_size[0] / 2 + vx * 1.3 - s[0] / 2, disp_size[1] / 2 + vy * 1.3 - s[1] / 2), visibility)
        s = self.surf_flare3.get_size()
        engine.blit_alpha(surf, self.surf_flare3, (disp_size[0] / 2 + vx * 0.4 - s[0] / 2, disp_size[1] / 2 + vy * 0.4 - s[1] / 2), visibility)
        s = self.surf_flare4.get_size()
        engine.blit_alpha(surf, self.surf_flare4, (disp_size[0] / 2 + vx * 0.45 - s[0] / 2, disp_size[1] / 2 + vy * 0.45 - s[1] / 2), visibility)
        s = self.surf_flare5.get_size()
        engine.blit_alpha(surf, self.surf_flare5, (disp_size[0] / 2 + vx * 0.35 - s[0] / 2, disp_size[1] / 2 + vy * 0.35 - s[1] / 2), visibility)
        s = self.surf_flare6.get_size()
        engine.blit_alpha(surf, self.surf_flare6, (disp_size[0] / 2 + vx * 0.19 - s[0] / 2, disp_size[1] / 2 + vy * 0.19 - s[1] / 2), visibility)
        s = self.surf_flare7.get_size()
        engine.blit_alpha(surf, self.surf_flare7, (disp_size[0] / 2 + vx * 0.06 - s[0] / 2, disp_size[1] / 2 + vy * 0.06 - s[1] / 2), visibility)
        s = self.surf_flare8.get_size()
        engine.blit_alpha(surf, self.surf_flare8, (disp_size[0] / 2 - vx * 0.18 - s[0] / 2, disp_size[1] / 2 - vy * 0.18 - s[1] / 2), visibility)
        s = self.surf_flare9.get_size()
        engine.blit_alpha(surf, self.surf_flare9, (disp_size[0] / 2 - vx * 0.35 - s[0] / 2, disp_size[1] / 2 - vy * 0.35 - s[1] / 2), visibility)
        s = self.surf_flare10.get_size()
        engine.blit_alpha(surf, self.surf_flare10, (disp_size[0] / 2 - vx * 0.30 - s[0] / 2, disp_size[1] / 2 - vy * 0.30 - s[1] / 2), visibility)
        s = self.surf_flare11.get_size()
        engine.blit_alpha(surf, self.surf_flare11, (disp_size[0] / 2 - vx * 0.37 - s[0] / 2, disp_size[1] / 2 - vy * 0.37 - s[1] / 2), visibility)
        s = self.surf_flare12.get_size()
        engine.blit_alpha(surf, self.surf_flare12, (disp_size[0] / 2 - vx * 0.58 - s[0] / 2, disp_size[1] / 2 - vy * 0.58 - s[1] / 2), visibility)
        s = self.surf_flare13.get_size()
        engine.blit_alpha(surf, self.surf_flare13, (disp_size[0] / 2 - vx * 0.61 - s[0] / 2, disp_size[1] / 2 - vy * 0.61 - s[1] / 2), visibility)
        s = self.surf_flare14.get_size()
        engine.blit_alpha(surf, self.surf_flare14, (disp_size[0] / 2 - vx * 0.9 - s[0] / 2, disp_size[1] / 2 - vy * 0.9 - s[1] / 2), visibility)
        s = self.surf_flare15.get_size()
        engine.blit_alpha(surf, self.surf_flare15, (disp_size[0] / 2 - vx * 1.2 - s[0] / 2, disp_size[1] / 2 - vy * 1.2 - s[1] / 2), visibility)
        s = self.surf_flare16.get_size()
        engine.blit_alpha(surf, self.surf_flare16, (disp_size[0] / 2 - vx * 1.2 - s[0] / 2, disp_size[1] / 2 - vy * 1.2 - s[1] / 2), visibility)
        s = self.surf_flare17.get_size()
        engine.blit_alpha(surf, self.surf_flare17, (disp_size[0] / 2 - vx * 1.2 - s[0] / 2, disp_size[1] / 2 - vy * 1.2 - s[1] / 2), visibility)
        s = self.surf_flare18.get_size()
        engine.blit_alpha(surf, self.surf_flare18, (disp_size[0] / 2 - vx * 1.85 - s[0] / 2, disp_size[1] / 2 - vy * 1.85 - s[1] / 2), visibility)
        s = self.surf_flare19.get_size()
        engine.blit_alpha(surf, self.surf_flare19, (disp_size[0] / 2 - vx * 1.80 - s[0] / 2, disp_size[1] / 2 - vy * 1.80 - s[1] / 2), visibility)
        s = self.surf_flare20.get_size()
        engine.blit_alpha(surf, self.surf_flare20, (disp_size[0] / 2 - vx * 3.1 - s[0] / 2, disp_size[1] / 2 - vy * 3.1 - s[1] / 2), visibility)
        s = self.surf_flare21.get_size()
        engine.blit_alpha(surf, self.surf_flare21, (disp_size[0] / 2 + vx * 1.75 - s[0] / 2, disp_size[1] / 2 + vy * 1.75 - s[1] / 2), visibility)
