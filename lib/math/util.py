from math import pi, sin, cos
from lib.math.vector import Vector2D

CLICKS_PER_CM = 1.0  # hm...


def get_duration(distance, power):
    """ Calculates how long does a bot need to move at power to cover distance. """
    return distance / power * CLICKS_PER_CM


def convert_angle(radians):
    """ Maps given angle to [-pi;pi] range. """
    while radians > pi:
        radians -= pi
    while radians < -pi:
        radians += pi
    return radians


def rotate_vector(vector, angle, anchor=(0, 0)):
        """Rotate by the given angle, relative to the anchor point."""
        x = vector.x - anchor[0]
        y = vector.y - anchor[1]

        cos_theta = cos(angle)
        sin_theta = sin(angle)

        nx = x*cos_theta - y*sin_theta
        ny = x*sin_theta + y*cos_theta

        nx = nx + anchor[0]
        ny = ny + anchor[1]

        return Vector2D(nx, ny)