import numpy as np
from lib.math.vector import Vector2D
__author__ = 'Sam'


class Strategy(object):

    def __init__(self, world, robot_tag, actual_robot):
        self.actual_robot = actual_robot
        self.robot_tag = robot_tag
        self.world = world

        self.grab_threshold_x = 3  # we need to define these (based on kicker)
        self.grab_threshold_y = 3
        self.dist_kicker_robot = 8

        self.ROBOT_WIDTH = 2

        # initialise state attributes
        self.robot = None
        self.ball = None

    def shoot(self):
        """
        We are facing the goal so just kick
        :return: duration that the motors are on
        """
        print "robot is facing goal"
        self.world.is_grabber_down = False
        return self.actual_robot.kick()  # kick

    def turn_robot_to_goal(self):
        print "robot not facing goal"
        to_turn = self.robot.angle_to_point(self.world.goal)
        print "rotating robot " + str(to_turn) + " radians"
        return self.actual_robot.turn(to_turn)  # turn towards the the goal

    def turn_robot_to_ball(self):
        """
        Turn the robot to face the ball
        :return: duration that the motors are on
        """
        print "robot not facing ball"
        to_turn = self.robot.angle_to_point(self.ball.position)
        print "rotating robot " + str(360.0 * to_turn / (2 * np.pi)) + " degrees"
        return self.actual_robot.turn(to_turn)  # turn towards the the ball

    def move_robot_to_ball(self):
        """
        Move the robot forward in a straight line to the ball
        :return: duration that the motors are on
        """
        print "robot facing ball"
        dist_to_ball = self.distance_from_kicker_to_ball() * 0.9  # only move 90%
        print "moving robot " + str(dist_to_ball)
        return self.actual_robot.move(dist_to_ball)

    def raise_cage(self):
        """
        opens the grabber arms
        :return: time it takes for the grabbers to open
        """
        self.world.is_grabber_down = False
        return self.actual_robot.kick()

    def lower_cage(self):
        """
        closes the grabber in an attempt to collect the ball
        :return: time it takes for the grabbers to close
        """
        # self.actual_robot.lower_cage()
        self.world.is_grabber_down = True
        print "GRABING"
        return self.actual_robot.grab()

    def is_robot_facing_goal(self):
        """
        Check if the angle between the robot and
        the centre of the goal is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        goal = self.world.goal
        robot = self.world.get_robot(self.robot_tag)
        return robot.can_see(point=goal, beam_width=self.ROBOT_WIDTH)

    def is_robot_facing_ball(self):
        """
        Check if the angle between the robot and
        the ball is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        robot = self.world.get_robot(self.robot_tag)
        ball_pos = self.world.get_ball().position
        return robot.can_see(point=ball_pos, beam_width=self.ROBOT_WIDTH/2)

    def is_robot_facing_up(self):
        """
        Check the up position is
        inside the beam projected from the robot
        :return: whether or not the robot is facing the ball
        """
        up_pos = Vector2D(self.robot.position.x, 150)
        robot = self.world.get_robot(self.robot_tag)
        return robot.can_see(point=up_pos, beam_width=self.ROBOT_WIDTH * 20)

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
        print "ball is " + str(ball_kicker_vector.length()) + " away"
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

    def distance_from_robot_to_point(self, x, y):
        return self.vector_from_robot_to_point(x,y).length()

    def vector_from_robot_to_point(self, x, y):
        """
        :return: distance from robot to a given point
        """
        robot_point_dist_x = np.abs(self.robot.position.x-x)
        robot_point_dist_y = np.abs(self.robot.position.y-y)
        return Vector2D(robot_point_dist_x, robot_point_dist_y)

    def ball_going_quickly(self):
        """
        Check is ball is going quicker than a threshold velocity
        """
        velocity_threshold = 10
        ball_velocity = self.world.get_ball().velocity.length()
        return ball_velocity > velocity_threshold

    def get_zone_centre(self):
        return Vector2D(0, 0)  # TODO

    def predict_y(self, predict_for_x):
        """
        Predict the y coordinate the ball will have when it reaches the x coordinate of the robot.
        """
        ball_x = self.ball.position.x
        ball_y = self.ball.position.y
        ball_v = self.ball.velocity

        distance_ball_robot = np.abs(ball_x-predict_for_x)

        if ball_v.x == 0:
            return ball_y
        else:
            return ball_y + (ball_v.y / ball_v.x) * distance_ball_robot



