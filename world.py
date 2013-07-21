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
                i +=1
            if self.color_list[i][0] == ratio:
                return self.color_list[i][1:]
            else:
                length = float(self.color_list[i - 1][0] - self.color_list[i][0])
                pos = float(ratio - self.color_list[i][0])
                r = int((self.color_list[i][1] * pos / length + self.color_list[i - 1][1] * (1 - pos / length)) / 2)
                g = int((self.color_list[i][2] * pos / length + self.color_list[i - 1][2] * (1 - pos / length)) / 2)
                b = int((self.color_list[i][3] * pos / length + self.color_list[i - 1][3] * (1 - pos / length)) / 2)
                return (r, g, b)

class Drawable:
    def __init__(self, x, y):
        self.position = [x, y]

    def draw(self, drawer):
        pass

class Mutable(Drawable):
    def __init__(self, x, y):
        Drawable.__init__(self, x, y)

    def process(self):
        pass

class Movable(Mutable):
    def __init__(self, x, y):
        Mutable.__init__(self, x, y)
        self.speed = [0.0, 0.0]

class Star(Mutable):
    def __init__(self, x, y, z, star_gradient):
        Drawable.__init__(self, x, y)
        self.position.append(z)
        self.color = star_gradient.get_color_at(z / 101.0)

    def draw(self, drawer):
        drawer.draw_star(self)

    def reset(self, camera):
        v = (camera.position[0] - self.position[0], camera.position[1] - self.position[1])
        self.position[0] += v[0] * 2
        self.position[1] += v[1] * 2

class Background(Drawable):
    def __init__(self, screen_size):
        star_gradient = Gradient([(0, 0, 0, 0), (0.4, 32, 32, 128), (1, 255, 255, 255)])
        self.stars = []
        for z in xrange(1, 102):
            for i in range(z**2 / 100):
                self.stars.append(Star((random.random() - 0.5) * z * screen_size[0], (random.random() - 0.5) * z * screen_size[1], z, star_gradient))

    def draw(self, drawer):
        for star in self.stars:
            if not drawer.draw_star(star):
                star.reset(drawer.camera)

class World:
    def __init__(self, screen_size):
        self.background = Background(screen_size)
        self.drawable = [self.background]
