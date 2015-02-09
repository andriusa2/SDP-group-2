from math import pi, sin, cos
from lib.math.vector import Vector2D


def get_duration(distance, power):
    """ Calculates how long does a bot need to move at power to cover distance. """
    # up to 200 it's nice and 40cm/s
    # then up to 300 it's faster (60 cm/s)
    # then again gets to 40cm/s
    assert power == 1
    if distance <= 5:
        # s = (t - 100)/0.04 + 1.0
        t = (distance + 3) / 0.04
    elif distance <= 11.3:
        # s = (t - 200) * 0.063 + 5
        t = (distance + 7) / 0.063
    else:
        # s = (t - 300) * 0.04 + 11.3
        t = (distance + 1.3) / 0.04
    return t


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