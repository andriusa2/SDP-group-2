__author__ = 'samdavies'
import time


class DummyRobot():

    def __init__(self, world):
        self.world = world

    def kick(self, power=None):
        time.sleep(1000)
        # artificially set the world state

    def turn(self, angle):
        """ Turns robot over 'angle' radians in place. """
        time.sleep(1000)
        # artificially set the world state

    def go(self, duration, power=None):
        time.sleep(1000)
        # artificially set the world state