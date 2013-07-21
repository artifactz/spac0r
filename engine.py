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
