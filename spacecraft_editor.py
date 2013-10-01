#!/usr/bin/env python

import pyperclip
import pygame
from pygame.locals import *

### INIT AND GLOBALS ###

pygame.init()
pygame.display.set_caption('spacecraft editor')
surf_display = pygame.display.set_mode((600, 450), DOUBLEBUF, 32) # FULLSCREEN
surf_spacecraft = pygame.Surface((600, 450))
col_black = pygame.Color(0, 0, 0)
col_green = pygame.Color(0, 255, 0)
shapez = []
sel_shape = -1
sel_mode = ''

### SHAPE CLASSES ###

class Shape:
    def __init__(self, color):
        self.color = color

class Line(Shape):
    def __init__(self, color, start, end):
        Shape.__init__(self, color)
        self.start = start
        self.end = end
        self.real_start = [.0, .0]
        self.real_end = [.0, .0]

class Circle(Shape):
    def __init__(self, color, center, radius):
        Shape.__init__(self, color)
        self.center = center
        self.radius = radius
        self.real_center = [.0, .0]

class Poly(Shape):
    def __init__(self, color, pointlist):
        Shape.__init__(self, color)
        self.pointlist = pointlist
        self.real_pointlist = [[.0, .0] for x in pointlist]

### PARSING SHAPES FROM CODE ###

def tokenize(string):
    x = 0
    start = 0
    end = -1
    count = 0
    while x < len(string):
        if string[x] == '(':
            start = x
            break
        x += 1
    while x < len(string):
        if string[x] == '(':
            count += 1
        if string[x] == ')':
            count -= 1
            if count == 0:
                end = x
                break
        x += 1
    lst = string[start:end+1].replace('(', ',').replace(')', ',').split(',')
    lst = filter(lambda a: a != ' ' and a != '', lst)
    return lst

def parse_shapes(data):
    shapez = []
    if data != None:
        for x in xrange(0, len(data)):
            if data[x:x+5] == 'Line(':
                t = tokenize(data[x:])
                if len(t) == 5:
                    shapez.append(Line(t[0] if isinstance(t[0], pygame.Color) else col_green, [int(t[1]), int(t[2])], [int(t[3]), int(t[4])]))
            if data[x:x+7] == 'Circle(':
                t = tokenize(data[x:])
                if len(t) == 4:
                    shapez.append(Circle(t[0] if isinstance(t[0], pygame.Color) else col_green, [int(t[1]), int(t[2])], int(t[3])))
            if data[x:x+5] == 'Poly(':
                t = tokenize(data[x:])
                if len(t) % 2 == 1:
                    plst = []
                    for x in xrange(1, len(t), 2):
                        plst.append((int(t[x]), int(t[x + 1])))
                    shapez.append(Poly(t[0] if isinstance(t[0], pygame.Color) else col_green, plst))
    return shapez

### DRAWING ###

def draw_shapez(off, shapez, sel_shape, sel_mode):
    surf_spacecraft.fill(col_black)
    for x in xrange(0, len(shapez)):
        if isinstance(shapez[x], Line):
            if sel_shape == x:
                color = pygame.Color(255 - shapez[x].color.r, 255 - shapez[x].color.g, 255 - shapez[x].color.b)
                pygame.draw.line(surf_spacecraft, color, (shapez[x].start[0] + off[0], -shapez[x].start[1] + off[1]), (shapez[x].end[0] + off[0], -shapez[x].end[1] + off[1]), 5)
                if sel_mode == 'start':
                    pygame.draw.circle(surf_spacecraft, color, (shapez[x].start[0] + off[0], -shapez[x].start[1] + off[1]), 5, 1)
                if sel_mode == 'end':
                    pygame.draw.circle(surf_spacecraft, color, (shapez[x].end[0] + off[0], -shapez[x].end[1] + off[1]), 5, 1)
            pygame.draw.line(surf_spacecraft, shapez[x].color, (shapez[x].start[0] + off[0], -shapez[x].start[1] + off[1]), (shapez[x].end[0] + off[0], -shapez[x].end[1] + off[1]))
        if isinstance(shapez[x], Circle):
            if sel_shape == x:
                color = pygame.Color(255 - shapez[x].color.r, 255 - shapez[x].color.g, 255 - shapez[x].color.b)
                pygame.draw.circle(surf_spacecraft, color, (shapez[x].center[0] + off[0], -shapez[x].center[1] + off[1]), shapez[x].radius, 3)
                if sel_mode == 'center':
                    pygame.draw.line(surf_spacecraft, color, (shapez[x].center[0] + off[0] - 1, -shapez[x].center[1] + off[1] - 1), (shapez[x].center[0] + off[0] + 1, -shapez[x].center[1] + off[1] + 1))
                    pygame.draw.line(surf_spacecraft, color, (shapez[x].center[0] + off[0] - 1, -shapez[x].center[1] + off[1] + 1), (shapez[x].center[0] + off[0] + 1, -shapez[x].center[1] + off[1] - 1))
                if sel_mode == 'radius':
                    pygame.draw.line(surf_spacecraft, color, (shapez[x].center[0] + off[0], -shapez[x].center[1] + off[1]), (shapez[x].center[0] + off[0] + shapez[x].radius, -shapez[x].center[1] + off[1]))
            pygame.draw.circle(surf_spacecraft, shapez[x].color, (shapez[x].center[0] + off[0], -shapez[x].center[1] + off[1]), shapez[x].radius, 1)

def blit_spacecraft(zoom):
    d = surf_display.get_size()
    s = surf_spacecraft.get_size()
    temp = pygame.transform.scale(surf_spacecraft, (int(s[0] * zoom), int(s[1] * zoom)))
    z = temp.get_size()
    surf_display.blit(temp, ((d[0] - z[0]) / 2, (d[1] - z[1]) / 2)) # align: center

### MISC ###

def select_shape(index):
    global sel_shape
    global sel_mode
    if len(shapez) == 0 or index == -1:
        sel_shape = -1
        sel_mode = ''
    else:
        sel_shape = index % len(shapez)
        if isinstance(shapez[sel_shape], Line): sel_mode = 'start'
        if isinstance(shapez[sel_shape], Circle): sel_mode = 'center'

def get_insert_position():
    if sel_shape > -1:
        if isinstance(shapez[sel_shape], Line):
            if sel_mode == 'start': return shapez[sel_shape].start[:]
            if sel_mode == 'end': return shapez[sel_shape].end[:]
        if isinstance(shapez[sel_shape], Circle):
            return shapez[sel_shape].center[:]
    else:
        return [0, 0]

def get_shapes_as_code():
    code = '['
    for shape in shapez:
        if isinstance(shape, Line):
            code += 'Line(col_green, (' + str(shape.start[0]) + ', ' + str(shape.start[1]) + '), (' + str(shape.end[0]) + ', ' + str(shape.end[1]) + '))'
        if isinstance(shape, Circle):
            code += 'Line(col_green, (' + str(shape.center[0]) + ', ' + str(shape.center[1]) + '), ' + shape.radius + ')'
        code += ', '
    return code[:-2] + ']'

### PROGRAM START ###

print 'looking for shape data in clipboard...'
shapez = parse_shapes(pyperclip.paste())
if len(shapez) == 0:
    print 'none'
else:
    print 'ok. ' + str(len(shapez)) + ' shapez found.'
    select_shape(0)

fps_clock = pygame.time.Clock()
surf_display.set_alpha(None)

off = [300, 225]
zoom = 1.

while True:
    surf_display.fill(col_black)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
            pygame.quit()
            exit(0)
        if event.type == KEYDOWN:
            # ZOOM:
            if (event.key == K_PLUS):
                zoom *= 2
            if (event.key == K_MINUS):
                zoom /= 2
            # SELECTING:
            if (event.key == K_TAB and shapez != None and len(shapez) > 0):
                if pygame.key.get_mods() == 0:
                    select_shape(sel_shape + 1)
                if pygame.key.get_mods() == 1:
                    if sel_shape == 0:
                        select_shape(len(shapez) - 1)
                    else:
                        select_shape(sel_shape - 1)
            if (event.key == K_RETURN and sel_shape >= 0):
                if isinstance(shapez[sel_shape], Line):
                    if sel_mode == '' or sel_mode == 'end':
                        sel_mode = 'start'
                    else:
                        sel_mode = 'end'
                if isinstance(shapez[sel_shape], Circle):
                    if sel_mode == '' or sel_mode == 'radius':
                        sel_mode = 'center'
                    else:
                        sel_mode = 'radius'
            if event.key == K_ESCAPE:
                select_shape(-1)
            # REPOSITIONING:
            if (event.key == K_UP or event.key == K_DOWN or event.key == K_LEFT or event.key == K_RIGHT) and sel_shape > -1:
                if pygame.key.get_mods() == 1: # SHIFT
                    step = 5
                else:
                    step = 1
                if event.key == K_UP: d = [0, step]
                elif event.key == K_DOWN: d = [0, -step]
                elif event.key == K_LEFT: d = [-step, 0]
                else: d = [step, 0]
                if isinstance(shapez[sel_shape], Line):
                    if sel_mode == 'start':
                        shapez[sel_shape].start[0] += d[0]
                        shapez[sel_shape].start[1] += d[1]
                    if sel_mode == 'end':
                        shapez[sel_shape].end[0] += d[0]
                        shapez[sel_shape].end[1] += d[1]
                if isinstance(shapez[sel_shape], Circle):
                    if sel_mode == 'center':
                        shapez[sel_shape].center[0] += d[0]
                        shapez[sel_shape].center[1] += d[1]
                    if sel_mode == 'radius':
                        shapez[sel_shape].radius += d[1]
            # DELETE
            if event.key == K_DELETE and sel_shape > -1:
                del shapez[sel_shape]
                if sel_shape >= len(shapez):
                    select_shape(sel_shape - 1)
                else:
                    select_shape(sel_shape)
            # NEW
            if event.key == K_l:
                pos = get_insert_position()
                shapez.append(Line(col_green, pos[:], pos[:]))
                select_shape(len(shapez) - 1)
            if event.key == K_c and pygame.key.get_mods() == 0:
                shapez.append(Circle(col_green, get_insert_position(), 6))
                select_shape(len(shapez) - 1)
            # EXPORT TO CLIPBOARD
            if event.key == K_c and pygame.key.get_mods() == 64:
                pyperclip.copy(get_shapes_as_code())

    draw_shapez(off, shapez, sel_shape, sel_mode)
    blit_spacecraft(zoom)

    pygame.display.update()
    fps_clock.tick(50)
