#!/usr/bin/env python

import random
import pygame

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
    def __init__(self, x, y, rotation = 0.0):
        self.position = [x, y]
        self.rotation = rotation

class Mutable(Drawable):
    def __init__(self, x, y):
        Drawable.__init__(self, x, y)

    def process(self): # probably will get something like a timespan since last frame, too
        pass

class Movable(Mutable):
    def __init__(self, x, y):
        Mutable.__init__(self, x, y)
        self.speed = [0.0, 0.0]

class Star(Mutable):
    def __init__(self, x, y, z, star_gradient):
        Drawable.__init__(self, x, y)
        self.position.append(z)
        self.color = star_gradient.get_color_at(1 - (z + 15.0) / (102.0 + 15.0))

    def reset(self, camera):
        v = (camera.position[0] - self.position[0], camera.position[1] - self.position[1])
        self.position[0] += v[0] * 2
        self.position[1] += v[1] * 2

class Stats:
    def __init__(self, hit_points = 0, hit_heal = 0, attack = 0, shield_points = 0, shield_heal = 0):
        self.hit_points = float(hit_points)
        self.hit_heal = float(hit_heal)
        self.attack = float(attack)
        self.shield_points = float(shield_points)
        self.shield_heal = float(shield_heal)

class Part(Mutable):
    def __init__(self, stats, look):
        self.stats = stats
        self.look = look

    def process(self):
        pass

class Spacecraft(Mutable):
    def __init__(self, parts_list):
        '''parts_list: (part, phi, r, rotation)'''
        self.parts = [part for (part, phi, r, rotation) in parts_list]
        self.draw_hints = [(phi, r, rotation) for (part, phi, r, rotation) in parts_list]

    def process(self):
        for part in self.parts:
            part.process()

class Background(Drawable):
    def __init__(self, screen_size):
        self.star_gradient = Gradient([(0, 0, 0, 0), (0.4, 16, 16, 96), (1, 255, 255, 255)])
        self.stars = []
        for z in xrange(102, 10, -1):
            for i in range(z**2 / 100 + 1):
                self.stars.append(Star((random.random() - 0.5) * z * screen_size[0], (random.random() - 0.5) * z * screen_size[1], z, self.star_gradient))

class World:
    def __init__(self, screen_size):
        self.background = Background(screen_size)
        # parts
        chassis_one = Part(Stats(hit_points = 100, hit_heal = 1, attack = 0), 'Chassis One')
        player = Spacecraft([(chassis_one, 0, 0, 0)])
