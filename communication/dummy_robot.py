__author__ = 'samdavies'
import time
from lib.math.util import rotate_vector
import os
import pty
import serial
from communication.controller import Controller


class DummyRobot(Controller):

    def __init__(self, world, robot_tag="L_ATT"):

        self.world = world
        self.robot_tag = robot_tag

        master, slave = pty.openpty()
        s_name = os.ttyname(slave)
        ser = serial.Serial(s_name)

        super(DummyRobot, self).__init__(ser.getPort(), is_dummy=True)

    def kick(self, power=None):
        pass
        return super(DummyRobot, self).kick(power)

    def turn(self, angle):
        """ Turns robot over 'angle' radians in place. """
        # artificially set the world state
        robot = self.world.get_robot(self.robot_tag)
        robot.direction = rotate_vector(robot.direction, angle)
        self.world.add_robot(self.robot_tag, robot)
        return super(DummyRobot, self).turn(angle)

    def move(self, distance):
        # artificially set the world state
        robot = self.world.get_robot(self.robot_tag)
        old_pos = robot.position
        unit_direction = robot.direction.scale(distance)
        robot.position += unit_direction
        self.world.add_robot(self.robot_tag, robot)
        return super(DummyRobot, self).move(distance)

    def grab(self):
        return super(DummyRobot, self).grab()