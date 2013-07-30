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
    '''Just an aestetic class. Every subclass has to implement process() itself.'''
    def __init__(self, x, y, rotation = .0):
        Drawable.__init__(self, x, y, rotation)

    def process(self, timespan):
        pass

class Movable(Mutable):
    def __init__(self, x, y, rotation = .0, sx = .0, sy = .0):
        Mutable.__init__(self, x, y, rotation)
        self.speed = [sx, sy]

    def process(self, timespan):
        self.position[0] += self.speed[0] * timespan
        self.position[1] += self.speed[1] * timespan

class Star(Drawable):
    def __init__(self, x, y, z, star_gradient):
        Drawable.__init__(self, x, y)
        self.position.append(z)
        a = (103 - z) / 104.0 + .1     # +.1 to make almost black stars a little lighter
        self.color = star_gradient.get_color_at(a)

    def reset(self, camera):
        v = (camera.position[0] - self.position[0], camera.position[1] - self.position[1])
        self.position[0] += v[0] * 2
        self.position[1] += v[1] * 2

class Collidable:
    def __init__(self, shapes):
        self.shapes = shapes

class Decayable:
    def __init__(self, ttl):
        self.ttl = ttl

    def process(self, timespan):
        self.ttl = max(self.ttl - timespan, 0)

class Particle(Movable, Decayable):
    def __init__(self, color, ttl, x, y, sx = .0, sy = .0):
        Movable.__init__(self, x, y, .0, sx, sy)
        Decayable.__init__(self, ttl)
        self.color = color

    def process(self, timespan):
        Movable.process(self, timespan)
        Decayable.process(self, timespan)

class Shot(Movable, Collidable, Decayable):
    def __init__(self, attack, ttl, x, y, sx = .0, sy = .0):
        Movable.__init__(self, x, y, .0, sx, sy)
        Collidable.__init__(self, [Line(None, (-2, 0), (2, 0))])
        Decayable.__init__(self, ttl)
        self.attack = attack

    def process(self, timespan):
        Movable.process(self, timespan)
        Decayable.process(self, timespan)
        self.shapes[0].real_start = [self.position[0] - self.speed[0] / 40, self.position[1] - self.speed[1] / 40]
        self.shapes[0].real_end = [self.position[0] + self.speed[0] / 40, self.position[1] + self.speed[1] / 40]

class Stats:
    def __init__(self, hit_points_max = 0, hit_heal = 0, attack = 0, attack_cooldown_max = 0, attack_speed = 0, attack_ttl = 0, shield_points = 0, shield_heal = 0):
        self.hit_points_max = float(hit_points_max)
        self.hit_points = self.hit_points_max
        self.hit_heal = float(hit_heal)
        self.attack = float(attack)
        self.attack_cooldown_max = float(attack_cooldown_max)
        self.attack_cooldown = .0
        self.attack_speed = float(attack_speed)
        self.attack_ttl = float(attack_ttl)
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

class Part(Drawable, Collidable):
    def __init__(self, stats, shapes, x, y, rotation = .0):
        Drawable.__init__(self, x, y, rotation)
        Collidable.__init__(self, shapes)
        self.stats = stats

    def process(self, timespan):
        if self.stats.attack_cooldown > 0:
            self.stats.attack_cooldown = max(self.stats.attack_cooldown - timespan, 0)

class Spacecraft(Movable, Collidable):
    def __init__(self, parts):
        Movable.__init__(self, .0, .0)
        self.parts = parts
        shapes = []
        for part in self.parts:
            shapes += part.shapes
        Collidable.__init__(self, shapes)

    def process(self, timespan):
        Movable.process(self, timespan)
        for part in self.parts:
            part.process(timespan)
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
            shot = Shot(weapon.stats.attack, weapon.stats.attack_ttl, weapon.shapes[0].real_start[0], weapon.shapes[0].real_start[1], math.cos(self.rotation) * weapon.stats.attack_speed, -math.sin(self.rotation) * weapon.stats.attack_speed)
            weapon.stats.attack_cooldown = weapon.stats.attack_cooldown_max
            world.add_entity(shot)

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
             Part(Stats(attack = 2.5, attack_cooldown_max = .5, attack_speed = 200, attack_ttl = 2.0), copy.deepcopy(laser_one), 2, 6, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .5, attack_speed = 200, attack_ttl = 2.0), copy.deepcopy(laser_one), 2, -6, 0)])

        self.hostile = Spacecraft(
            [Part(Stats(hit_points_max = 100), copy.deepcopy(chassis_one), 0, 0, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .75, attack_speed = 50, attack_ttl = 2.0), copy.deepcopy(laser_one), 2, 6, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .75, attack_speed = 50, attack_ttl = 2.0), copy.deepcopy(laser_one), 2, -6, 0)])
        self.hostile.position = [100.0, 10.0]
        self.hostile.rotation = 1.0

        # fast access lists
        self.spacecrafts = [self.player, self.hostile]
        self.shots = []
        self.particles = []
        self.mutable = [self.player, self.hostile]
        self.collidable = [self.player, self.hostile]
        self.decayable = []

    def add_entity(self, entity):
        if isinstance(entity, Spacecraft):
            self.spacecrafts.append(entity)
        if isinstance(entity, Shot):
            self.shots.append(entity)
        if isinstance(entity, Particle):
            self.particles.append(entity)
        if isinstance(entity, Mutable):
            self.mutable.append(entity)
        if isinstance(entity, Collidable):
            self.collidable.append(entity)
        if isinstance(entity, Decayable):
            self.decayable.append(entity)

    def remove_entity(self, entity):
        if isinstance(entity, Spacecraft):
            self.spacecrafts.remove(entity)
        if isinstance(entity, Shot):
            self.shots.remove(entity)
        if isinstance(entity, Particle):
            self.particles.remove(entity)
        if isinstance(entity, Mutable):
            self.mutable.remove(entity)
        if isinstance(entity, Collidable):
            self.collidable.remove(entity)
        if isinstance(entity, Decayable):
            self.decayable.remove(entity)

    def spacecraft_hit_by_shot(self, spacecraft, shot, position):
        for x in xrange(0, 10):
            angle = math.atan2(shot.speed[1], shot.speed[0]) + (random.random() + random.random()) - 1 + math.pi
            speed = math.sqrt(shot.speed[0]**2 + shot.speed[1]**2) * (random.random() * random.random() / 2 + 0.05)
            sx = math.cos(angle) * speed
            sy = math.sin(angle) * speed
            ttl = random.random() + 1
            self.add_entity(Particle((255, 255, 0), ttl, position[0], position[1], sx, sy))
        self.remove_entity(shot)

def collides(shapes1, shapes2):
    '''Takes two shape sequences and checks if they overlap. Returns (x, y) if they do, else None.'''
    for shape1 in shapes1:
        if isinstance(shape1, Line):
            line1 = shape1
            for shape2 in shapes2:
                if isinstance(shape2, Line):
                    line2 = shape2
                    # check if the two lines intersect
                    x1 = line1.real_start[0]
                    y1 = line1.real_start[1]
                    x2 = line1.real_end[0]
                    y2 = line1.real_end[1]
                    x3 = line2.real_start[0]
                    y3 = line2.real_start[1]
                    x4 = line2.real_end[0]
                    y4 = line2.real_end[1]
                    # don't calculate the intersection point if the bounding boxes don't overlap
                    if min(x1, x2) <= max(x3, x4) and min(x3, x4) <= max(x1, x2) and min(y1, y2) <= max(y3, y4) and min(y3, y4) <= max(y1, y2):
                        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                        # abort on (almost) parallel lines
                        if denominator < 5:
                            continue
                        x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
                        y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator
                        # check if the intersection point is in the overlap box
                        if x <= max(x1, x2, x3, x4) and x >= min(x1, x2, x3, x4) and y <= max(y1, y2, y3, y4) and y >= min(y1, y2, y3, y4):
                            return x, y
