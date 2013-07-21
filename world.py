#!/usr/bin/env python

import random
import pygame

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
    def __init__(self, x, y, z):
        Drawable.__init__(self, x, y)
        self.position.append(z)

    def draw(self, drawer):
        drawer.draw_star(self)

    def reset(self, camera):
        v = (camera.position[0] - self.position[0], camera.position[1] - self.position[1])
        self.position[0] += v[0] * 2
        self.position[1] += v[1] * 2

class Background(Drawable):
    def __init__(self, screen_size):
        self.stars = []
        for z in xrange(1, 101):
            for i in range(z):
                self.stars.append(Star((random.random() - 0.5) * z * screen_size[0], (random.random() - 0.5) * z * screen_size[1], z))

    def draw(self, drawer):
        for star in self.stars:
            if not drawer.draw_star(star):
                #print star.position
                star.reset(drawer.camera)
                #print star.position

class World:
    def __init__(self, screen_size):
        self.background = Background(screen_size)
        self.drawable = [self.background]
