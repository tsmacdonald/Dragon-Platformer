import pygame
from pygame.locals import *

class Animator():
    def __init__(self, image_list):
        self.image_list = image_list
        self.pointer = 0
        self.direction = "right"
    def next(self):
        temp_pointer = self.pointer
        self.pointer += 1
        self.pointer %= len(self.image_list)
        return self.image_list[temp_pointer]
    def turn(self, direction):
        if direction == self.direction:
            return
        else:
          for i in xrange(len(self.image_list)):
              self.image_list[i] = pygame.transform.flip(self.image_list[i], True, False)
          self.direction = direction
    
