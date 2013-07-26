#!/usr/bin/env python

import random
import pygame
import math
import copy

class Gradient:
    def __init__(self, color_list):
        '''color_list is [(position, r, g, b), ...]'''
        # sort by position
        self.color_list = sorted(color_list)

    def get_color_at(self, ratio):
        if ratio >= 0 and ratio <= 1:
            i = 0
            while self.color_list[i][0] < ratio:
                i += 1
            if self.color_list[i][0] == ratio:
                return self.color_list[i][1:]
            # self.color_list[i - 1][0] < ratio < self.color_list[i][0]
            else:
                length = float(self.color_list[i][0] - self.color_list[i - 1][0])
                pos = float(ratio - self.color_list[i - 1][0])
                ratio2 = pos / length
                r = int((self.color_list[i - 1][1] * (1 - ratio2) + self.color_list[i][1] * ratio2))
                g = int((self.color_list[i - 1][2] * (1 - ratio2) + self.color_list[i][2] * ratio2))
                b = int((self.color_list[i - 1][3] * (1 - ratio2) + self.color_list[i][3] * ratio2))
                return (r, g, b)

class Drawable:
    def __init__(self, x, y, rotation = .0):
        self.position = [x, y]
        self.rotation = rotation

class Mutable(Drawable):
    def __init__(self, x, y, rotation = .0):
        Drawable.__init__(self, x, y, rotation)

    def process(self): # probably will get something like a timespan since last frame, too
        pass

class Movable(Mutable):
    def __init__(self, x, y, rotation = .0, sx = .0, sy = .0):
        Mutable.__init__(self, x, y, rotation)
        self.speed = [sx, sy]

    def process(self):
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]

class Star(Mutable):
    def __init__(self, x, y, z, star_gradient):
        Mutable.__init__(self, x, y)
        self.position.append(z)
        self.color = star_gradient.get_color_at(1 - (z + 15.0) / (102.0 + 15.0))

    def reset(self, camera):
        v = (camera.position[0] - self.position[0], camera.position[1] - self.position[1])
        self.position[0] += v[0] * 2
        self.position[1] += v[1] * 2

class Collidable(Movable):
    def __init__(self, x, y, rotation = .0, sx = .0, sy = .0):
        Movable.__init__(self, x, y, rotation, sx, sy)

    def process(self):
        Movable.process(self)

class Shot(Collidable):
    def __init__(self, attack, x, y, sx = .0, sy = .0):
        Collidable.__init__(self, x, y, .0, sx, sy)
        self.attack = attack

    def process(self):
        Collidable.process(self)

class Stats:
    def __init__(self, hit_points_max = 0, hit_heal = 0, attack = 0, attack_cooldown_max = 0, attack_speed = 0, shield_points = 0, shield_heal = 0):
        self.hit_points_max = float(hit_points_max)
        self.hit_points = self.hit_points_max
        self.hit_heal = float(hit_heal)
        self.attack = float(attack)
        self.attack_cooldown_max = float(attack_cooldown_max)
        self.attack_cooldown = .0
        self.attack_speed = float(attack_speed)
        self.shield_points = float(shield_points)
        self.shield_heal = float(shield_heal)

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

class Part(Mutable):
    def __init__(self, stats, shapes, x, y, rotation = .0):
        Mutable.__init__(self, x, y, rotation)
        self.stats = stats
        self.shapes = shapes

    def process(self):
        pass

class Spacecraft(Movable):
    def __init__(self, parts):
        Movable.__init__(self, .0, .0)
        self.parts = parts

    def process(self):
        Movable.process(self)
        for part in self.parts:
            part.process()
        self.translate_shapes()

    def translate_shapes(self):
        cos = math.cos(self.rotation)
        sin = math.sin(self.rotation)
        for i in xrange(0, len(self.parts)):
            dx = self.position[0] + cos * self.parts[i].position[0] + sin * self.parts[i].position[1]
            dy = self.position[1] + cos * self.parts[i].position[1] - sin * self.parts[i].position[0]
            for shape in self.parts[i].shapes:
                if isinstance(shape, Line):
                    cos2 = math.cos(self.rotation + self.parts[i].rotation)
                    sin2 = math.sin(self.rotation + self.parts[i].rotation)
                    shape.real_start = (cos2 * shape.start[0] + sin2 * shape.start[1] + dx, cos2 * shape.start[1] - sin2 * shape.start[0] + dy)
                    shape.real_end = (cos2 * shape.end[0] + sin2 * shape.end[1] + dx, cos2 * shape.end[1] - sin2 * shape.end[0] + dy)

    def shoot(self, world):
        for weapon in filter(lambda x: x.stats.attack > 0 and x.stats.attack_cooldown <= 0, self.parts):
            shot = Shot(weapon.stats.attack, self.position[0], self.position[1], math.cos(self.rotation) * weapon.stats.attack_speed, -math.sin(self.rotation) * weapon.stats.attack_speed)
            #world.drawable.append(shot)
            world.mutable.append(shot)
            #world.collidable.append(shot)
            world.shots.append(shot)

class Background(Drawable):
    def __init__(self, screen_size):
        self.star_gradient = Gradient([(0, 0, 0, 0), (.4, 16, 16, 96), (1, 255, 255, 255)])
        self.stars = []
        for z in xrange(102, 10, -1):
            for i in range(z**2 / 100 + 1):
                self.stars.append(Star((random.random() - .5) * z * screen_size[0], (random.random() - .5) * z * screen_size[1], z, self.star_gradient))

class World:
    def __init__(self, screen_size):
        self.col_black = pygame.Color(0, 0, 0)
        self.col_white = pygame.Color(255, 255, 255)
        self.col_red   = pygame.Color(255, 0, 0)
        self.col_green = pygame.Color(0, 255, 0)

        self.background = Background(screen_size)
        # shapes
        chassis_one = [Line(self.col_green, (10, 0), (-10, 10)), Line(self.col_green, (-10, 10), (-10, -10)), Line(self.col_green, (-10, -10), (10, 0))]
        laser_one = [Line(self.col_green, (-3, 0), (3, 0))]

        self.player = Spacecraft(
            [Part(Stats(hit_points_max = 100, hit_heal = 1), copy.deepcopy(chassis_one), 0, 0, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .75, attack_speed = .5), copy.deepcopy(laser_one), 2, 6, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .75, attack_speed = .5), copy.deepcopy(laser_one), 2, -6, 0)])

        self.hostile = Spacecraft(
            [Part(Stats(hit_points_max = 100), copy.deepcopy(chassis_one), 0, 0, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .75, attack_speed = .5), copy.deepcopy(laser_one), 2, 6, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .75, attack_speed = .5), copy.deepcopy(laser_one), 2, -6, 0)])
        self.hostile.position = [100.0, 10.0]
        self.hostile.rotation = 1.0

        self.spacecrafts = [self.player, self.hostile]
        self.mutable = [self.player, self.hostile]
        self.shots = []
