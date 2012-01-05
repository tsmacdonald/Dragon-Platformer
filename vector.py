class Vector(object):
    """2D vector with the option to set maximum and minimum values."""
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
