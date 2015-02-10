from math import cos, sin, sqrt
import numpy as np


class Vector2D(object):
    """
    Contains a 2-dimensional vector
    """
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __iter__(self):
        return self.x, self.y

    def __eq__(self, other):
        return (self.x == other.x) & (self.y == other.y)

    @staticmethod
    def to_vector2d(args):
        if isinstance(args, Vector2D):
            return args
        x, y = args
        return Vector2D(x, y)

    @staticmethod
    def from_angle(angle, length, base_vector):
        """

        :param angle: angle in radians wrt base_vector
        :param length: length of new vector
        :param base_vector: a normalized vector
        :return: a new vector which has specified length is at given angle from base_vector
        """
        assert base_vector is not None
        assert length > 0

        x, y = base_vector
        _x = x * cos(angle) - y * sin(angle)
        _y = x * sin(angle) + y * cos(angle)
        return Vector2D(_x * sqrt(length), _y * sqrt(length))

    def length(self):
        return sqrt(self.dot(self))

    def dot(self, v1):
        return v1.x * self.x + v1.y * self.y

    def __add__(self, v):
        return Vector2D(self.x + v.x, self.y + v.y)

    def __sub__(self, v):
        return Vector2D(self.x - v.x, self.y - v.y)

    def scale(self, size):
        new_x = self.x * size
        new_y = self.y * size
        return Vector2D(float(new_x), float(new_y))

    def get_angle(self, base_vector):
        v1_u = self.unit_vector()
        v2_u = base_vector.unit_vector()
        # convert to numpy representation
        v1_u = [v1_u.x, v1_u.y]
        v2_u = [v2_u.x, v2_u.y]
        angle = np.arccos(np.dot(v1_u, v2_u))
        if np.isnan(angle):
            if (v1_u == v2_u).all():
                return 0.0
            else:
                return np.pi
        return angle

    def is_null(self):
        return self.x == 0.0 and self.y == 0.0

    def unit_vector(self):
        magnitude = self.length()
        unit_vector = Vector2D(float(self.x / magnitude), float(self.y / magnitude))
        return unit_vector

