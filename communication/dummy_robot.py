__author__ = 'samdavies'
import time
from lib.math.util import rotate_vector


class DummyRobot():

    def __init__(self, world, robot_tag):
        self.world = world
        self.robot_tag = robot_tag

    def kick(self, power=None):
        pass
        # artificially set the world state

    def turn(self, angle):
        """ Turns robot over 'angle' radians in place. """
        pass
        # artificially set the world state
        robot = self.world.get_robot(self.robot_tag)
        robot.direction = rotate_vector(robot.direction, angle)
        self.world.add_robot(self.robot_tag, robot)

    def move_forward(self, distance):
        # artificially set the world state
        robot = self.world.get_robot(self.robot_tag)
        old_pos = robot.position
        unit_direction = robot.direction.scale(distance)
        robot.position += unit_direction
        print("robot moved from " + str(old_pos.x) + ", " + str(old_pos.y) + " to " + str(robot.position.x) + ", " + str(robot.position.y))
        self.world.add_robot(self.robot_tag, robot)

    def go(self, duration, power=None):
        pass

    def raise_cage(self):
        pass
        # artificially set the world state

    def lower_cage(self):
        pass
        # artificially set the world state