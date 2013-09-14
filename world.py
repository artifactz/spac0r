#!/usr/bin/env python

import random
import pygame
import math
import copy
import pilots

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

# ABSTRACT
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

class Collidable:
    def __init__(self, shapes):
        self.shapes = shapes

class Decayable:
    def __init__(self, ttl):
        self.ttl = ttl

    def process(self, timespan):
        self.ttl = max(self.ttl - timespan, 0)

# INSTANTIABLE
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

class Planet(Drawable):
    def __init__(self, x, y, size):
        Drawable.__init__(self, x, y)
        self.size = size

class Particle(Movable, Decayable):
    def __init__(self, color, ttl, x, y, sx = .0, sy = .0):
        Movable.__init__(self, x, y, .0, sx, sy)
        Decayable.__init__(self, ttl)
        self.color = color

    def process(self, timespan):
        Movable.process(self, timespan)
        Decayable.process(self, timespan)

class Shot(Movable, Collidable, Decayable):
    def __init__(self, attack, ttl, origin, x, y, sx = .0, sy = .0):
        Movable.__init__(self, x, y, .0, sx, sy)
        Collidable.__init__(self, [Line(None, (-2, 0), (2, 0))])
        Decayable.__init__(self, ttl)
        self.attack = attack
        self.origin = origin

    def process(self, timespan):
        Movable.process(self, timespan)
        Decayable.process(self, timespan)
        self.shapes[0].real_start = [self.position[0] - self.speed[0] / 40, self.position[1] - self.speed[1] / 40]
        self.shapes[0].real_end = [self.position[0] + self.speed[0] / 40, self.position[1] + self.speed[1] / 40]

class Stats:
    def __init__(self, hit_points_max = 0, hit_heal = 0, attack = 0, attack_cooldown_max = 0, attack_speed = 0, attack_ttl = 0, shield_points_max = 0, shield_heal = 0, rotation_speed = 0, accerlation = 0, speed_max = 0):
        self.hit_points_max = float(hit_points_max)
        self.hit_points = self.hit_points_max
        self.hit_heal = float(hit_heal)
        self.attack = float(attack)
        self.attack_cooldown_max = float(attack_cooldown_max)
        self.attack_cooldown = .0
        self.attack_speed = float(attack_speed)
        self.attack_ttl = float(attack_ttl)
        self.shield_points_max = float(shield_points_max)
        self.shield_points = self.shield_points_max
        self.shield_heal = float(shield_heal)
        self.rotation_speed = float(rotation_speed)
        self.accerlation = float(accerlation)
        self.speed_max = float(speed_max)

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

class Part(Drawable, Collidable):
    def __init__(self, stats, shapes, x, y, rotation = .0, animator = None):
        Drawable.__init__(self, x, y, rotation)
        Collidable.__init__(self, shapes)
        self.stats = stats
        self.animator = animator
        if animator:
            self.animation_time = random.random() * 100

    def process(self, timespan):
        if self.animator:
            self.animation_time += timespan
            self.animator(self.shapes, self.animation_time)
        if self.stats.attack_cooldown > 0:
            self.stats.attack_cooldown = max(self.stats.attack_cooldown - timespan, 0)

class Spacecraft(Movable, Collidable):
    def __init__(self, parts):
        Movable.__init__(self, .0, .0)
        self.parts = parts
        self.stats = Stats()
        self.pilot = None
        shapes = []
        for part in self.parts:
            shapes += part.shapes
            self.stats.hit_points_max += part.stats.hit_points_max
            self.stats.hit_points += part.stats.hit_points
            self.stats.hit_heal += part.stats.hit_heal
            self.stats.shield_points_max += part.stats.shield_points_max
            self.stats.shield_points += part.stats.shield_points
            self.stats.shield_heal += part.stats.shield_heal
            self.stats.rotation_speed += part.stats.rotation_speed
            self.stats.accerlation += part.stats.accerlation
            self.stats.speed_max += part.stats.speed_max
        Collidable.__init__(self, shapes)
        self.steer = [False] * 4
        self.rotate_to = 0

    def process(self, timespan):
        # piloting
        if self.pilot:
            self.pilot.pilot()
        # steering
        if self.steer[0]:   # straight
            self.speed[0] += math.cos(self.rotation) * self.stats.accerlation * timespan
            self.speed[1] -= math.sin(self.rotation) * self.stats.accerlation * timespan
        if self.steer[1]:   # back
            self.speed[0] += math.cos(self.rotation + math.pi) * self.stats.accerlation * timespan
            self.speed[1] -= math.sin(self.rotation + math.pi) * self.stats.accerlation * timespan
        if self.steer[2]:   # left
            self.speed[0] += math.cos(self.rotation + math.pi / 2) * self.stats.accerlation * timespan
            self.speed[1] -= math.sin(self.rotation + math.pi / 2) * self.stats.accerlation * timespan
        if self.steer[3]:   # right
            self.speed[0] += math.cos(self.rotation - math.pi / 2) * self.stats.accerlation * timespan
            self.speed[1] -= math.sin(self.rotation - math.pi / 2) * self.stats.accerlation * timespan
        for x in xrange(0, 4):
            self.steer[x] = False
        # rotation
        if abs(self.rotate_to - self.rotation) <= self.stats.rotation_speed * timespan:
            self.rotation = self.rotate_to
        else:
            if self.rotation > self.rotate_to:
                self.rotation -= self.stats.rotation_speed * timespan
            else:
                self.rotation += self.stats.rotation_speed * timespan
        # respect the speed limit
        speed = math.sqrt(self.speed[0]**2 + self.speed[1]**2)
        if speed > self.stats.speed_max:
            shrink = self.stats.speed_max / speed
            self.speed[0] *= shrink
            self.speed[1] *= shrink
        # misc
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
                cos2 = math.cos(self.rotation + self.parts[i].rotation)
                sin2 = math.sin(self.rotation + self.parts[i].rotation)
                if isinstance(shape, Line):
                    shape.real_start = (cos2 * shape.start[0] + sin2 * shape.start[1] + dx, cos2 * shape.start[1] - sin2 * shape.start[0] + dy)
                    shape.real_end = (cos2 * shape.end[0] + sin2 * shape.end[1] + dx, cos2 * shape.end[1] - sin2 * shape.end[0] + dy)
                if isinstance(shape, Circle):
                    shape.real_center = (cos2 * shape.center[0] + sin2 * shape.center[1] + dx, cos2 * shape.center[1] - sin2 * shape.center[0] + dy)

    def steer_straight(self):
        self.steer[0] = True

    def steer_back(self):
        self.steer[1] = True

    def steer_left(self):
        self.steer[2] = True

    def steer_right(self):
        self.steer[3] = True

    def rotate(self, to):
        self.rotate_to = to
        self.rotation = self.rotation % (math.pi * 2)
        while self.rotate_to - self.rotation > math.pi:
            self.rotate_to -= math.pi * 2
        while self.rotate_to - self.rotation < -math.pi:
            self.rotate_to += math.pi * 2

    def shoot(self, world):
        for weapon in filter(lambda x: x.stats.attack > 0 and x.stats.attack_cooldown <= 0, self.parts):
            shot = Shot(weapon.stats.attack, weapon.stats.attack_ttl, self, weapon.shapes[0].real_start[0], weapon.shapes[0].real_start[1], math.cos(self.rotation) * weapon.stats.attack_speed, -math.sin(self.rotation) * weapon.stats.attack_speed)
            weapon.stats.attack_cooldown = weapon.stats.attack_cooldown_max
            world.add_entity(shot)

    def explode(self, world):
        # generate some particles
        for x in xrange(0, 500):
            angle = random.random() * math.pi * 2
            speed = (1 - random.random()**5) * 110
            sx = math.cos(angle) * speed
            sy = math.sin(angle) * speed
            ttl = (1 - random.random()**2) * 2
            world.add_entity(Particle((255, 232, 0), ttl, self.position[0], self.position[1], sx, sy))
        world.remove_entity(self)

class Background(Drawable):
    def __init__(self, screen_size):
        self.star_gradient = Gradient([(0, 0, 0, 0), (.4, 16, 16, 96), (1, 255, 255, 255)])
        self.stars = []
        for z in xrange(102, 10, -1):
            for i in range(z**2 / 100 + 1):
                self.stars.append(Star((random.random() - .5) * z * screen_size[0], (random.random() - .5) * z * screen_size[1], z, self.star_gradient))

class World:
    def __init__(self, screen_size):
        # stars
        self.background = Background(screen_size)
        # planets
        self.planets = [Planet(20, 50, .667)]

        self.player = Spacecraft(
            [Part(Stats(hit_points_max = 100, hit_heal = 1), get_shape('chassis_one'), 0, 0, 0),
             Part(Stats(attack = 10, attack_cooldown_max = .5, attack_speed = 200, attack_ttl = 2.0), get_shape('laser_one'), 2, 6, 0),
             Part(Stats(attack = 10, attack_cooldown_max = .5, attack_speed = 200, attack_ttl = 2.0), get_shape('laser_one'), 2, -6, 0),
             Part(Stats(rotation_speed = 2, accerlation = 50, speed_max = 100), get_shape('engine_one'), -4, 0, 0)])

        self.hostile = Spacecraft(
            [Part(Stats(hit_points_max = 100, rotation_speed = 1.25, accerlation = 50, speed_max = 60), get_shape('chassis_one'), 0, 0, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .75, attack_speed = 100, attack_ttl = 2.0), get_shape('laser_one'), 2, 6, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .75, attack_speed = 100, attack_ttl = 2.0), get_shape('laser_one'), 2, -6, 0)])
        self.hostile.position = [100.0, 10.0]
        self.hostile.rotation = 1.0
        self.hostile.pilot = pilots.AI_Pilot_Basic(self.hostile, self)

        # fast access lists
        self.spacecrafts = [self.player, self.hostile]
        self.shots = []
        self.particles = []
        self.mutable = [self.player, self.hostile]
        self.collidable = [self.player, self.hostile]
        self.decayable = []

        #print self.player.shapes
        #print self.hostile.shapes

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
        # generate some particles
        for x in xrange(0, 10):
            angle = math.atan2(shot.speed[1], shot.speed[0]) + (random.random() + random.random()) - 1 + math.pi
            speed = math.sqrt(shot.speed[0]**2 + shot.speed[1]**2) * (random.random() * random.random() / 2 + 0.05)
            sx = math.cos(angle) * speed
            sy = math.sin(angle) * speed
            ttl = random.random() + 1
            self.add_entity(Particle((255, 255, 0), ttl, position[0], position[1], sx, sy))
        # decrease spacecraft hp
        spacecraft.stats.hit_points -= shot.attack
        # remove shot
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

# PROTOTYPES
col_black = pygame.Color(0, 0, 0)
col_white = pygame.Color(255, 255, 255)
col_red   = pygame.Color(255, 0, 0)
col_green = pygame.Color(0, 255, 0)

shapes = {}
shapes['chassis_one'] = [Line(col_green, (10, 0), (-10, 10)), Line(col_green, (-10, 10), (-10, -10)), Line(col_green, (-10, -10), (10, 0))]
shapes['laser_one'] = [Line(col_green, (-3, 0), (3, 0))]
shapes['engine_one'] = [Circle(col_green, (0, 0), 6)]

def get_shape(identifier):
    return copy.deepcopy(shapes[identifier])
