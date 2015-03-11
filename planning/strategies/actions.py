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

    def turn_robot_to_point(self, point):
        """
        turn the robot to face the a Vector2D point
        :return: duration and info
        """
        to_turn = self.strategy.robot.angle_to_point(point)
        rotation_in_deg = int(360.0 * to_turn / (2 * np.pi))
        ball_x = self.strategy.ball.position.x
        ball_y = self.strategy.ball.position.y
        info = "turning {0} degrees to ({1}, {2})".format(rotation_in_deg, ball_x, ball_y)
        return self.strategy.actual_robot.turn(to_turn), info

    def move_robot_to_ball(self):
        """
        Move the robot forward in a straight line to the ball
        :return: duration that the motors are on
        """
        dist_to_ball = self.strategy.distance_from_kicker_to_ball() * 0.8  # only move 90%
        return self.strategy.actual_robot.move(dist_to_ball), "moving {0} cm".format(dist_to_ball)

    def move_to_centre(self):
        robot_y = self.strategy.robot.position.y
        vect_to_point = self.strategy.vector_from_robot_to_point(self.strategy.get_zone_centre(), robot_y)
        dist_to_point = vect_to_point.length()

        # reverse the distance when the intercept point is below the robot
        if vect_to_point.x < 0:
            dist_to_point = - dist_to_point

        # multiply with the robots direction
        to_move = self.strategy.get_local_move(vect_to_point, self.strategy.robot.direction)

        info = "moving robot ({0}, {1}) cm to ({2}, {3})".format(to_move.x, to_move.y, vect_to_point.x,
                                                                 vect_to_point.y)
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

