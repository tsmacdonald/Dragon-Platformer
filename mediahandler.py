import os
import pygame
from pygame.locals import *

def load_image(filename, directory = "images", colorkey = None, return_rect = True):
    """Constructs and returns an image object from the given file."""
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
    """Constructs and returns a sound object from the given file."""
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
