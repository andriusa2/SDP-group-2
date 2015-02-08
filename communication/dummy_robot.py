__author__ = 'samdavies'
import time
from lib.math.util import rotate_vector


class DummyRobot():

    def __init__(self, world, robot_tag):
        self.world = world
        self.robot_tag = robot_tag
        self.robot = world.get_robot(robot_tag)

    def kick(self, power=None):
        pass
        # artificially set the world state

    def turn(self, angle):
        """ Turns robot over 'angle' radians in place. """
        pass
        # artificially set the world state
        self.robot.direction = rotate_vector(self.robot.direction, angle)
        self.world.add_robot(self.robot_tag, self.robot)

    def go(self, duration, power=None):
        pass
        # artificially set the world state

    def raise_cage(self):
        pass
        # artificially set the world state

    def lower_cage(self):
        pass
        # artificially set the world state