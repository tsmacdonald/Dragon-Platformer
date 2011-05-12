import os, pygame
from pygame.locals import *

def load_image(filename, directory = "images", colorkey = None, return_rect = True):
    fullname = os.path.join(directory, filename)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    if return_rect:
        return image, image.get_rect()
    else:
        return image
    
def load_sound(name, directory = "sounds"):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(directory, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound
    
#class Vector():
#	def __init__(self, x, y):
#		self.x = x
#		self.y = y

class Vector(object):
    def __init__(self, x, y, x_max = None, x_min = None, y_max = None, y_min = None):
        self._x = x
        self._y = y
        self.x_max = x_max
        self.x_min = x_min
        self.y_max = y_max
        self.y_min = y_min

    def getx(self):
        return self._x

    def gety(self):
        return self._y
    
    def setx(self, x):
        if self.x_max is not None:
            x = min(x, self.x_max)
        if self.x_min is not None:
            x = max(x, self.x_min)
        self._x = x

    def sety(self, y):
        if self.y_max is not None:
            y = min(y, self.y_max)
        if self.y_min is not None:
            y = max(y, self.y_min)
        self._y = y

    x = property(getx, setx)
    y = property(gety, sety)

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
    
