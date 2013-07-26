#!/usr/bin/env python

import random
import pygame
import math

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

class Part(Mutable):
    def __init__(self, stats, look, x, y, rotation = .0):
        Mutable.__init__(self, x, y, rotation)
        self.stats = stats
        self.look = look

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

    def shoot(self, world):
        for weapon in filter(lambda x: x.stats.attack > 0 and x.stats.attack_cooldown <= 0, self.parts):
            shot = Shot(weapon.stats.attack, self.position[0], self.position[1], math.cos(self.rotation) * weapon.stats.attack_speed, -math.sin(self.rotation) * weapon.stats.attack_speed)
            world.drawable.append(shot)
            world.mutable.append(shot)
            world.collidable.append(shot)
            world.shots.append(shot)
            #w.gen_shot(weapon.stats.attack, w.player.position[0], w.player.position[1], 0.1, 0)


class Background(Drawable):
    def __init__(self, screen_size):
        self.star_gradient = Gradient([(0, 0, 0, 0), (.4, 16, 16, 96), (1, 255, 255, 255)])
        self.stars = []
        for z in xrange(102, 10, -1):
            for i in range(z**2 / 100 + 1):
                self.stars.append(Star((random.random() - .5) * z * screen_size[0], (random.random() - .5) * z * screen_size[1], z, self.star_gradient))

class World:
    def __init__(self, screen_size):
        self.background = Background(screen_size)
        # parts
        self.player = Spacecraft(
            [Part(Stats(hit_points_max = 100, hit_heal = 1), 'Chassis One', 0, 0, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .75, attack_speed = .5), 'Laser One', 2, 6, 0),
             Part(Stats(attack = 2.5, attack_cooldown_max = .75, attack_speed = .5), 'Laser One', 2, -6, 0)])
        self.drawable = [self.player]
        self.mutable = [self.player]
        self.collidable = [self.player]
        self.shots = []
