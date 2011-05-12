from time import time

class AI():
    def __init__(self):
        self.time = time()
        self.timeout = 1

    def hitwall(self, critter):
        if time() - self.time > self.timeout:
            critter.turn_around()
            self.time = time()
