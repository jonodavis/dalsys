import random


class TrackingSystem(object):
    ''' Defines the tracking system interface. '''

    _initialised = False

    def retrieve(self, map, drone):
        ''' Retrieves the location of a drone on a map. '''
        if not self._initialised:
            self._initialised = True
            random.seed()

        return DroneLocation(map is not None)


class DroneLocation(object):
    ''' Contains the location of a drone. '''

    _x = random.randint(0, 100)
    _y = random.randint(0, 100)

    def __init__(self, valid):
        self._valid = valid

    def is_valid(self):
        ''' Checks if this location instance is still valid. '''
        self._x += random.randint(-10, 10)
        self._y += random.randint(-10, 10)
        return self._valid and (self._x >= 0) and (self._x <= 100) and (self._y >= 0) and (self._y <= 100)

    def position(self):
        ''' Retrieves the position of the drone on the map. '''
        return (self._x, self._y, 1)
