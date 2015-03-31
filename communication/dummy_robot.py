import time
from lib.math.vector import Vector2D
from planning.strategies.strategy import Strategy

__author__ = 'samdavies'
from lib.math.util import rotate_vector
import os
import pty
import serial
from communication.controller import Controller


class DummyRobot(object):

    def __init__(self, world, robot_tag="L_ATT"):

        self.world = world
        self.robot_tag = robot_tag
        self.act_timer = time.time()

    def kick(self, power=None):
        self.add_act_time()

    def turn(self, angle):
        """ Turns robot over 'angle' radians in place. """
        # artificially set the world state
        robot = self.world.get_robot(self.robot_tag)
        robot.direction = rotate_vector(robot.direction, angle)
        self.world.add_robot(self.robot_tag, robot)
        self.add_act_time()

    def move(self, x_distance, y_distance=0, direction=Vector2D(1, 0)):
        # artificially set the world state
        robot = self.world.get_robot(self.robot_tag)

        print "y_distance {0}".format(y_distance)
        robot.position += Strategy.get_global_move(Vector2D(x_distance, y_distance), direction)
        print "new position {0}".format(robot.position)
        self.world.add_robot(self.robot_tag, robot)
        self.add_act_time()

    def close_grabber(self):
        self.add_act_time()

    def open_grabber(self):
        self.add_act_time()

    def is_available(self):
        print "{0} secs to wait".format(self.act_timer - time.time())
        return self.act_timer <= time.time()

    def add_act_time(self):
        self.act_timer = time.time() + 1
        print self.act_timer
