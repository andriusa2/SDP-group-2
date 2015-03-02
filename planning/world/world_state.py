from lib.math.vector import Vector2D
from math import sin, cos, sqrt, pi
"""
TODO: convert to numpy arrays instead of tuples
      roll out proper vector/point classes?
      maybe permit two robots in one zone?
"""


class Zone(object):
    """ Zone enum. """
    L_DEF, L_ATT, R_ATT, R_DEF = range(4)
    zone_order = (L_DEF, L_ATT, R_ATT, R_DEF)


class _WorldObject(object):
    def __init__(self, position, velocity):
        self.position = Vector2D.to_vector2d(position)
        self.velocity = Vector2D.to_vector2d(velocity)


class Robot(_WorldObject):
    """
    Robot object.
    Contains all position/velocity data and also:
    - direction it can shoot at (or could drive towards? hm...).
    - whether it's an enemy robot or not. << might not be needed!
    """

    def __init__(self, direction=(0, 0), position=(0, 0), velocity=(0, 0), enemy=False):
        self.enemy = enemy if enemy else False
        self.direction = Vector2D.to_vector2d(direction)
        self.is_moving = False
        super(Robot, self).__init__(position, velocity)

    def convert_from_model(self, model_robot, scale_factor):
        direction = Vector2D.from_angle(model_robot.angle, 1, Vector2D(1, 0))
        position = model_robot.x * scale_factor, model_robot.y * scale_factor
        velocity = model_robot.velocity * cos(model_robot.angle), model_robot.velocity * sin(model_robot.angle)
        return Robot(direction, position, velocity, self.enemy)

    def is_enemy(self):
        return self.enemy

    def __repr__(self):
        return (
            "Robot(direction={direction!r}, "
            "position={position!r}, velocity={velocity!r}, "
            "is_enemy={enemy!r})"
        ).format(**self.__dict__)

    def can_see(self, point, threshold=None, beam_width=7):
        """
        Return true if robot can "see" a given point withing a beam.
        """
        # vector from robot to point
        assert not threshold
        return self.is_point_within_beam(point, self.direction, beam_width)

    def is_point_within_beam(self, point, direction, beam_width=7):
        dpoint = point - self.position
        # sanity check
        if abs(dpoint.get_angle(direction)) >= pi / 2:
            return False
        projection = direction.scale(dpoint.dot(direction))
        dist_vector = dpoint - projection
        return dist_vector.dot(dist_vector) <= beam_width * beam_width

    def angle_to_point(self, point):
        """
        calculates the angle from the robots direction to a point
        """
        # create a vector from robot origin to a point
        point = Vector2D.to_vector2d(point)
        d = point - self.position
        if d.is_null():
            return False
        angle = d.get_angle(self.direction.unit_vector())
        return angle


class Ball(_WorldObject):
    """
    Ball object.
    in_possession is set to True if some robot currently possesses this ball.
    """

    def __init__(self, position=(0, 0), velocity=(0, 0), in_possession=None):
        self.in_possession = in_possession if in_possession else False
        super(Ball, self).__init__(position, velocity)

    def convert_from_model(self, model_ball, scale_factor):
        return Ball(position=(model_ball.x * scale_factor, model_ball.y * scale_factor),
                    velocity=(model_ball.velocity * cos(model_ball.angle), model_ball.velocity * sin(model_ball.angle)),
                    in_possession=False)

    def __repr__(self):
        return (
            "Ball(position={position!r}, velocity={velocity!r}, "
            "in_possession={in_possession!r})"
        ).format(**self.__dict__)


class WorldState(object):
    """
    Object containing:
    - A collection of recognised robots per zone
    - A ball object
    - Zone boundaries  NB. Assumes that zones are perfectly vertical. Might want to fix that later
    
    All objects should contain following properties:
    - Position (relative to some point on arena (bottom left maybe?), in cm)
    - Velocity (vector, magnitude is cm/s)
    
    Robots should also have:
    - Flag whether they are enemy robots or not
    - direction vector (normalized wrt their position)
    
    Should be filled by vision component of our system.
    """

    def __init__(self, robots=None, ball=None, zone_boundaries=None, left_goal=(0, 50), right_goal=(212, 50)):
        """
        :param robots: A list of robots (if zone_boundaries is supplied) or
          a dictionary mapping zone to robot.
        :param zone_boundaries: an iterable with 4 elements (first boundary is always at x=0)
        """
        self.ball = ball
        self.zone_boundaries = zone_boundaries
        self.robots = dict() if not robots else robots
        self.fix_robots()
        self.left_goal = Vector2D.to_vector2d(left_goal)
        self.right_goal = Vector2D.to_vector2d(right_goal)
        self.is_grabber_down = False
        self.do_refresh_kick = True

    def fix_robots(self):
        """
        Converts self.robots to a canonical representation (currently a dict of zone: robot)
        """
        # duck-typey check whether it's a dict or not
        try:
            self.robots.keys()
        except AttributeError:
            # not a dict-like object
            self.set_robots_list(self.robots)
        else:
            # dict-like object
            self.set_robots_dict(self.robots)

    def get_zone(self, point):
        """
        Returns a zone in which the given point should reside
        """
        if not self.zone_boundaries:
            raise TypeError("No zone boundaries are set")
        for zone_id, right_bound in zip(Zone.zone_order, self.zone_boundaries):
            if point.x <= right_bound:
                return zone_id
        raise Exception("Point does not fit into any zone")

    def set_zone_boundaries(self, boundaries):
        self.zone_boundaries = boundaries

    def add_robot(self, zone, robot):
        """ Add a robot to a given zone. Replaces any robot which was there already. """
        self.robots[zone] = robot

    def set_robots(self, robots):
        """ Initialize all robots from `robots`. """
        self.robots = robots
        self.fix_robots()

    def set_robots_list(self, robot_list):
        """
        Try to initialize self.robots from a list of robots.
        It assumes that robot ordering is from left to right.
        """
        self.robots = dict()
        robot_list.sort(key=lambda a: a.position.x)
        for robot in robot_list:
            self.robots[self.get_zone(robot.position)] = robot

        """
        Removed since there won't be 4 robots on pitch during milestone.
        """
        """
        Try to initialize self.robots from a list of robots.
        If there are no zone boundaries set, it assumes that robot ordering is from left
        to right. If there aren't 4 robots given, it should error out.

        If zone boundaries are set, then it tries to allocate robots properly to their zones.
        """
        # if not self.zone_boundaries:
        #     if len(robot_list) != 4:
        #         raise TypeError("Provided robot list of length < 4, but no zone boundary map is found")
        #     # assume that robots are listed in turn from left to right
        #     # probably we would need to recalculate that
        #     # no dict comprehensions in 2.6 :/
        #     self.robots = dict()
        #     for key, val in zip(Zone.zone_order, robot_list):
        #         self.robots[key] = val
        # else:
        #     self.robots = dict()
        #     for robot in robot_list:
        #         self.robots[self.get_zone(robot.position)] = robot

    def set_robots_dict(self, robot_dict):
        unknown_keys = set(robot_dict.keys()) - set(Zone.zone_order)
        if unknown_keys:
            raise TypeError("robot_dict contains some unknown keys: {0!r}".format(unknown_keys))
        self.robots = robot_dict

    def get_robot(self, zone):
        return self.robots.get(zone, None)

    def get_robots_list(self):
        return [self.robots[zone] for zone in Zone.zone_order if zone in self.robots]

    def get_robots_dict(self):
        return self.robots

    def set_ball(self, ball):
        self.ball = ball

    def get_ball(self):
        return self.ball

    def __repr__(self):
        return (
            "WorldState(robots={robots!r}, ball={ball!r}, "
            "zone_boundaries={zone_boundaries!r})"
        ).format(**self.__dict__)
