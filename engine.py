#!/usr/bin/env python

import pygame
from pygame.locals import *
import random
import numpy
import math

# TODO performance boost dict w x h
def blit_alpha(target, source, location, alpha):
    temp = pygame.Surface(source.get_size()).convert()
    # blit background
    temp.blit(target, (-location[0], -location[1]))
    # blit actual image
    temp.blit(source, (0, 0))
    temp.set_alpha(alpha)
    target.blit(temp, location)

def draw_line_alpha(target, color, start, end, alpha):
    w = max(start[0], end[0]) - min(start[0], end[0]) + 2
    h = max(start[1], end[1]) - min(start[1], end[1]) + 2
    temp = pygame.Surface((w, h)).convert()
    off = (min(start[0], end[0]), min(start[1], end[1]))
    # blit background
    temp.blit(target, (-off[0] + 1, -off[1] + 1))
    # draw line
    pygame.draw.line(temp, color, (start[0] - off[0] + 1, start[1] - off[1] + 1), (end[0] - off[0] + 1, end[1] - off[1] + 1))
    temp.set_alpha(alpha)
    target.blit(temp, (off[0] - 1, off[1] - 1))
