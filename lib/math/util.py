from math import pi, sin, cos
from lib.math.vector import Vector2D
import numpy as np
# that is how numpy fit the thing to 3rd degree poly
# it is somewhat accurate
# I believe that we will have worse problems with accuracy either way
# x=np.array([0.,0.1,0.15,0.2,0.25,0.3])
# y=np.array([0.,2.56,4.8,7.68,12.8,18.9])
# z=np.polyfit(y, x, 3)  # as we want f: Y -> X, not f: X -> Y

distance_polynomial = np.poly1d(np.array([-0.094, 11.89, 52.6]))


def get_duration(distance, power):
    """ Calculates how long does a bot need to move at power to cover distance. """
    assert power == 1
    if distance <= 21:
        t = distance_polynomial(distance)
    else:
        # s = (t - 260) * 0.043 + 21
        t = (distance - 21) / 0.043 + 260
    return int(t)


def convert_angle(radians):
    """ Maps given angle to [-pi;pi] range. """
    while radians > pi:
        print '-pi', radians
        radians -= pi
    while radians < -pi:
        print '+pi', radians
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


def clamp(num, max_val, min_val):
    return max(min(num, max_val), min_val)


def rad_to_deg(rad):
    return int(360.0 * rad / (2 * np.pi))