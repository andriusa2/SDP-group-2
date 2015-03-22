from lib.math.util import rad_to_deg
from lib.math.vector import Vector2D
import numpy as np

__author__ = 'Sam Davies'


class Actions(object):

    def __int__(self, strategy):
        self.strategy = strategy

    def turn_robot_to_goal(self):
        """
        turn the robot to face the goal
        :return: duration and info
        """
        return self.turn_robot_to_point(self.strategy.goal)

    def turn_robot_to_ball(self):
        """
        Turn the robot to face the ball
        :return: duration and info
        """
        return self.turn_robot_to_point(self.strategy.ball.position)

    def turn_to_closest_square_angle(self):

        # angle in range 0..2pi
        angle_to_turn = self.strategy.robot.direction.get_angle(Vector2D(1, 0)) + np.pi
        assert 0 <= angle_to_turn <= 2 * np.pi

        while angle_to_turn > np.pi / 2:
            angle_to_turn -= np.pi / 2

        if angle_to_turn > np.pi / 4:
            angle_to_turn -= np.pi / 2

        to_turn = -angle_to_turn
        info = "turning {0} degrees)".format(rad_to_deg(to_turn))
        return self.turn_robot(to_turn,), info

    def turn_robot_to_point(self, point):
        """
        turn the robot to face the a Vector2D point
        :return: duration and info
        """
        to_turn = self.strategy.robot.angle_to_point(point)
        ball_x = self.strategy.ball.position.x
        ball_y = self.strategy.ball.position.y
        info = "turning {0} degrees to ({1}, {2})".format(rad_to_deg(to_turn), ball_x, ball_y)
        return self.turn_robot(to_turn,), info

    def turn_robot(self, to_turn):
        return self.strategy.actual_robot.turn(to_turn)

    def intercept_ball(self):
        s = self.strategy
        x, y = s.y_intercept_of_ball_goal(s.goal, s.ball.position)
        vect_to_point = s.vector_from_robot_to_point(x, y)

        # multiply with the robots direction
        to_move = s.get_local_move(vect_to_point, s.robot.direction)

        info = "moving robot ({0}, {1}) cm to ({2}, {3})".format(to_move.x, to_move.y, vect_to_point.x,
                                                                 vect_to_point.y)
        return s.actual_robot.move(to_move.x, to_move.y, s.robot.direction), info

    def move_robot_to_ball(self):
        """
        Move the robot forward in a straight line to the ball
        :return: duration that the motors are on
        """
        dist_to_ball = self.strategy.distance_from_kicker_to_ball() * 0.8  # only move 90%
        return self.strategy.actual_robot.move(dist_to_ball), "moving {0} cm".format(dist_to_ball)

    def move_to_centre(self):
        robot_y = self.strategy.robot.position.y
        centre_x = self.strategy.get_zone_centre()
        vect_to_point = self.strategy.vector_from_robot_to_point(centre_x, robot_y)

        # multiply with the robots direction
        to_move = self.strategy.get_local_move(vect_to_point, self.strategy.robot.direction)

        info = "moving robot ({0}, {1}) cm to ({2}, {3})".format(to_move.x, to_move.y, centre_x, robot_y)
        return self.strategy.actual_robot.move(to_move.x, to_move.y, self.strategy.robot.direction), info

    def shoot(self):
        """
        We are facing the goal so just kick
        :return: duration that the motors are on
        """
        self.strategy.world.is_grabber_down = False
        return self.strategy.actual_robot.kick(), "Kicking"  # kick

    def raise_cage(self):
        """
        opens the grabber arms
        :return: time it takes for the grabbers to open
        """
        self.strategy.world.is_grabber_down = False
        return self.strategy.actual_robot.kick(), "Kicking and opening grabber"

    def lower_cage(self):
        """
        closes the grabber in an attempt to collect the ball
        :return: time it takes for the grabbers to close
        """
        self.strategy.world.is_grabber_down = True
        return self.strategy.actual_robot.grab(), "Closing grabber"

