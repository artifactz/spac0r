#!/usr/bin/env python

import pygame
from pygame.locals import *
import random
#import numpy
import math

surf_alpha = {}
surf_scale = {}

def blit_alpha(target, source, location, alpha):
    temp = get_alpha_surface(source.get_width(), source.get_height()) #pygame.Surface(source.get_size()).convert()
    # blit background
    temp.blit(target, (-location[0], -location[1]))
    # blit actual image
    temp.blit(source, (0, 0))
    temp.set_alpha(alpha)
    target.blit(temp, location)

def draw_line_alpha(target, color, start, end, alpha):
    w = int(max(start[0], end[0]) - min(start[0], end[0]) + 2)
    h = int(max(start[1], end[1]) - min(start[1], end[1]) + 2)
    temp = get_alpha_surface(w, h)
    off = (min(start[0], end[0]), min(start[1], end[1]))
    # blit background
    temp.blit(target, (-off[0] + 1, -off[1] + 1))
    # draw line
    pygame.draw.line(temp, color, (start[0] - off[0] + 1, start[1] - off[1] + 1), (end[0] - off[0] + 1, end[1] - off[1] + 1))
    temp.set_alpha(alpha)
    target.blit(temp, (off[0] - 1, off[1] - 1))

def get_alpha_surface(width, height):
    key = (width, height)
    if not surf_alpha.has_key(key):
        temp = pygame.Surface((width, height)).convert()
        surf_alpha[key] = temp
    return surf_alpha[key]

def get_scale_surface(surface, width, height):
    width = int(width)
    height = int(height)
    key = (surface, width, height)
    if not surf_scale.has_key(key):
        temp = pygame.transform.scale(surface, (width, height))
        surf_scale[key] = temp
    return surf_scale[key]

def count_overlapping_pixels(rect1, rect2):
    rect3 = (max(rect1[0], rect2[0]), max(rect1[1], rect2[1]), min(rect1[2], rect2[2]), min(rect1[3], rect2[3]))
    if rect3[0] > rect3[2] or rect3[1] > rect3[3]:
        return 0
    else:
        return (rect3[2] - rect3[0]) * (rect3[3] - rect3[1])
