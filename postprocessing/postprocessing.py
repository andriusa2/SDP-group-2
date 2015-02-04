# from planning.models import Vector
from copy import deepcopy
# from math import atan2, pi, hypot
from math import cos, sin, hypot, pi, atan2
from vision import tools


class Coordinate(object):

    def __init__(self, x, y):
        if x == None or y == None:
            raise ValueError('Can not initialize to attributes to None')
        else:
            self._x = x
            self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, new_x):
        if new_x == None:
            raise ValueError('Can not set attributes of Coordinate to None')
        else:
            self._x = new_x

    @y.setter
    def y(self, new_y):
        if new_y == None:
            raise ValueError('Can not set attributes of Coordinate to None')
        else:
            self._y = new_y

    def __repr__(self):
        return 'x: %s, y: %s\n' % (self._x, self._y)


class Vector(Coordinate):

    def __init__(self, x, y, angle, velocity):
        super(Vector, self).__init__(x, y)
        if angle == None or velocity == None or angle < 0 or angle >= (2*pi):
            raise ValueError('Can not initialise attributes of Vector to None')
        else:
            self._angle = angle
            self._velocity = velocity

    @property
    def angle(self):
        return self._angle

    @property
    def velocity(self):
        return self._velocity

    @angle.setter
    def angle(self, new_angle):
        if new_angle == None or new_angle < 0 or new_angle >= (2*pi):
            raise ValueError('Angle can not be None, also must be between 0 and 2pi')
        self._angle = new_angle

    @velocity.setter
    def velocity(self, new_velocity):
        if new_velocity == None or new_velocity < 0:
            raise ValueError('Velocity can not be None or negative')
        self._velocity = new_velocity

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and (self.__dict__ == other.__dict__))

    def __repr__(self):
        return ('x: %s, y: %s, angle: %s, velocity: %s\n' %
                (self.x, self.y,
                 self._angle, self._velocity))

class Postprocessing(object):

    def __init__(self):
        self._vectors = {}
        self._vectors['ball'] = {'vec': Vector(0, 0, 0, 0), 'time': 0}
        self._vectors['our_attacker'] = {'vec': Vector(0, 0, 0, 0), 'time': 0}
        self._vectors['their_attacker'] = {'vec': Vector(0, 0, 0, 0), 'time': 0}
        self._vectors['our_defender'] = {'vec': Vector(0, 0, 0, 0), 'time': 0}
        self._vectors['their_defender'] = {'vec': Vector(0, 0, 0, 0), 'time': 0}
        self._time = 0

    def analyze(self, vector_dict):
        '''
        This method analyzes current positions and previous object vector.
        '''
        self._time += 1
        new_vector_dict = {}
        for name, info in vector_dict.iteritems():
            if name == 'ball':
                new_vector_dict[name] = self.analyze_ball(info)
            else:
                new_vector_dict[name] = self.analyze_robot(name, info)
        return new_vector_dict

    def analyze_ball(self, info):
        '''
        This method calculates the angle and the velocity of the ball.
        '''
        if not(info['x'] is None) and not (info['y'] is None):
            delta_x = info['x'] - self._vectors['ball']['vec'].x
            delta_y = info['y'] - self._vectors['ball']['vec'].y
            velocity = hypot(delta_y, delta_x)/(self._time - self._vectors['ball']['time'])
            angle = atan2(delta_y, delta_x) % (2*pi)
            self._vectors['ball']['vec'] = Vector(info['x'], info['y'], angle, velocity)
            self._vectors['ball']['time'] = self._time
            return Vector(int(info['x']), int(info['y']), angle, velocity)
        else:
            return deepcopy(self._vectors['ball']['vec'])

    def analyze_robot(self, key, info):
        '''
        This method calculates the angle and the velocity of the robot.
        '''
        if not(info['x'] is None) and not(info['y'] is None) and not(info['angle'] is None):

            robot_angle = info['angle']

            delta_x = info['x'] - self._vectors[key]['vec'].x
            delta_y = info['y'] - self._vectors[key]['vec'].y

            # Calculate the angle of the delta vector relative to (1, 0)
            delta_angle = atan2(delta_y, delta_x)
            # Offset the angle if negative, we only want positive values
            delta_angle = delta_angle if delta_angle > 0 else 2 * pi + delta_angle

            velocity = hypot(delta_y, delta_x)/(self._time - self._vectors[key]['time'])

            # Make the velocity negative if the angles are not roughly the same
            if not (-pi / 2 < abs(delta_angle - robot_angle) < pi / 2):
                velocity = -velocity

            self._vectors[key]['vec'] = Vector(info['x'], info['y'], info['angle'], velocity)
            self._vectors[key]['time'] = self._time
            return Vector(info['x'], info['y'], info['angle'], velocity)
        else:
            return deepcopy(self._vectors[key]['vec'])
