import pygame
from pygame.locals import *
import random
import math

surf_alpha = {}
surf_scale = {}
col_transp = pygame.Color(0, 0, 255, 0)
col_key = pygame.Color(255, 0, 255)


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

def draw_aa_circle(target, color, center, radius, level):
    # temp surface size
    sz = int((radius + 2) * level * 2)
    # sub-pixel offset for drawing on anti-alias surface
    off = (int((center[0] - math.floor(center[0])) * level), int((center[1] - math.floor(center[1])) * level))
    #temp = get_alpha_surface(sz, sz)
    temp = pygame.Surface((sz, sz)).convert_alpha()
    temp.fill(col_transp)
    # draw a huge circle on a temporary surface
    draw_circle(temp, color, (int(sz / 2) + off[0], int(sz / 2) + off[1]), radius * level, level)
    # scale down to actual size
    surf_aa = pygame.transform.rotozoom(temp, 0, 1.0 / level)
    # blit on target
    target.blit(surf_aa, (int(center[0] - surf_aa.get_width() / 2), int(center[1] - surf_aa.get_height() / 2)))

def draw_circle(target, color, center, radius, width):
    sz = int(radius * 2 + 2)
    #temp = get_alpha_surface(sz, sz)
    temp = pygame.Surface((sz, sz)) #.convert_alpha()
    temp.fill(col_key)
    pygame.draw.circle(temp, color, (int(sz / 2), int(sz / 2)), radius)
    if radius - width > 0:
        pygame.draw.circle(temp, col_key, (int(sz / 2), int(sz / 2)), radius - width)
    temp.set_colorkey(col_key)
    target.blit(temp, (int(center[0] - temp.get_width() / 2), int(center[1] - temp.get_height() / 2)))

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
