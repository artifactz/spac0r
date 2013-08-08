#!/usr/bin/env python
'''Module for generating lens flare textures.'''

import pygame
from pygame.locals import *
import random
#import numpy
import math

OUTERBLUR = 1
INNERBLUR1 = 2
INNERBLUR2 = 3
INNERBLUR3 = 4
RING = 5

SMOOTHING = 0.1

def gen_texture(size, type, color, alpha):
    '''Generates a single lens flare texture of given size: size x size, color: (r, g, b),
    type: OUTERBLUR | INNERBLUR1 | INNERBLUR2 | INNERBLUR3 and opacity: alpha.'''
    surf = pygame.Surface((size, size), SRCALPHA | HWSURFACE, 32)
    surf = surf.convert_alpha()
    _draw_texture(surf, type, color, alpha)
    return surf

def _draw_texture(surf, type, color, alpha):
    '''The actual drawing.'''
    size = surf.get_size()
    R = min(size[0], size[1]) / 2
    pix = pygame.PixelArray(surf)
    for x in xrange(0, len(pix)):
        for y in xrange(0, len(pix[0])):
            vx = x - R
            vy = y - R
            r = min(math.sqrt(vx**2 + vy**2) / R, 1.0)
            result = int(_get_alpha(r, type) * alpha)
            pix[x][y] = pygame.Color(color[0], color[1], color[2], result)
    del pix

def _get_alpha(radius, type):
    '''Returns an alpha value depending on a distance to the image center: radius
    and the lens flare type.'''
    if type == OUTERBLUR:
        return (1.0 - radius**2)
    if type == INNERBLUR1:
        return _smooth_edge(radius) if radius >= 1 - SMOOTHING else radius**6
    if type == INNERBLUR2:
        return _smooth_edge(radius) if radius >= 1 - SMOOTHING else radius
    if type == INNERBLUR3:
        return _smooth_edge(radius) if radius >= 1 - SMOOTHING else (radius + 0.65) / 1.65
    if type == RING:
        c = 1 - abs(radius - 0.9) * 10
        if c < 0:
            return 0.0
        else:
            return c**3

def _smooth_edge(radius):
    '''Returns alternate alpha values on flare edges to give a smoother look.'''
    if radius >= 1:
        return 0
    return (1 - (SMOOTHING - 1 + radius) / SMOOTHING)**2
