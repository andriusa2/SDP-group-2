import numpy as np
from lib.math.vector import Vector2D
__author__ = 'Sam'


class GeneralizedStrategy(object):

    def __init__(self, world, robot_tag, actual_robot):
        self.actual_robot = actual_robot
        self.robot_tag = robot_tag
        self.world = world

        self.grab_threshold_x = 2  # we need to define these (based on kicker)
        self.grab_threshold_y = 2
        self.dist_kicker_robot = 2

        self.is_grabber_down = True

        # initialise state attributes
        self.robot = None
        self.ball = None

        # fetch the attributes from the world
        # self.fetch_world_state()

    def raise_cage(self):
        self.actual_robot.raise_cage()
        self.is_grabber_down = False
        print "raising cage"

    def lower_cage(self):
        self.actual_robot.lower_cage()
        self.is_grabber_down = True
        print "lowering cage"

    def is_robot_facing_goal(self):
        """
        Check if the angle between the robot and
        the centre of the goal is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        goal = self.world.goal
        robot = self.world.get_robot(self.robot_tag)
        return robot.can_see(point=goal, threshold=0.05)

    def is_robot_facing_ball(self):
        """
        Check if the angle between the robot and
        the ball is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        robot = self.world.get_robot(self.robot_tag)
        ball_pos = self.world.get_ball().position
        return robot.can_see(point=ball_pos, threshold=0.05)

    def fetch_world_state(self):
        """
        grab the latest state of the world and set this objects attribute
        :return: nothing
        """
        self.robot = self.world.get_robot(self.robot_tag)
        self.ball = self.world.get_ball()

    def is_ball_close(self):
        """
        checks whether the ball is in close proximity to the robot's kicker
        :return:
        """
        self.fetch_world_state()

        # check if the balls is in close enough to the robot to be grabbed
        ball_kicker_vector = self.vector_from_kicker_to_ball()
        ball_close_x = ball_kicker_vector.x < self.grab_threshold_x
        ball_close_y = ball_kicker_vector.y < self.grab_threshold_y
        return ball_close_x and ball_close_y

    def distance_from_kicker_to_ball(self):
        """
        :return: distance from the kicker to the ball
        """
        return self.vector_from_kicker_to_ball().length()

    def vector_from_kicker_to_ball(self):
        """
        :return: vector from the kicker to the ball
        """
        kicker_pos = self.get_kicker_position()

        ball_kicker_dist_x = np.abs(kicker_pos.x-self.ball.position.x)
        ball_kicker_dist_y = np.abs(kicker_pos.y-self.ball.position.y)
        return Vector2D(ball_kicker_dist_x, ball_kicker_dist_y)

    def get_kicker_position(self):
        """
        fetch the kicker position based on robot pos and direction
        :return: a vector
        """
        # use the direction and position of the robot to find the position of the kicker
        direction_unit_vector = self.robot.direction.unit_vector()
        kicker_vector = direction_unit_vector.scale(self.dist_kicker_robot)
        return self.robot.position + kicker_vector

