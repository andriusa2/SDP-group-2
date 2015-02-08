__author__ = 'samdavies'
import time


class DummyRobot():

    def __init__(self, world):
        self.world = world

    def kick(self, power=None):
        pass
        # artificially set the world state

    def turn(self, angle):
        """ Turns robot over 'angle' radians in place. """
        pass
        # artificially set the world state

    def go(self, duration, power=None):
        pass
        # artificially set the world state

    def raise_cage(self):
        pass
        # artificially set the world state

    def lower_cage(self):
        pass
        # artificially set the world state