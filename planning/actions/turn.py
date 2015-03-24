from lib.math.util import rad_to_deg, clamp
from lib.math.vector import Vector2D
import numpy as np

__author__ = 'Sam Davies'


class Turn(object):

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
        return self._turn_robot(to_turn,), info

    def turn_to_bounce_point(self):
        bounce_point = self.strategy.select_bounce_point()
        return self.turn_robot_to_point(bounce_point)

    def turn_to_home(self):
        """
        turn the robot to face the centre point
        """
        home = self.strategy.get_centre_point()
        return self.turn_robot_to_point(home)

    def turn_robot_to_point(self, point):
        """
        turn the robot to face the a Vector2D point
        :return: duration and info
        """
        to_turn = self.strategy.robot.angle_to_point(point)
        ball_x = self.strategy.ball.position.x
        ball_y = self.strategy.ball.position.y
        info = "turning {0} degrees to ({1}, {2})".format(rad_to_deg(to_turn), ball_x, ball_y)
        return self._turn_robot(to_turn,), info

    def _turn_robot(self, to_turn):
        to_turn *= self.strategy.turn_dampening
        to_turn = clamp(to_turn, self.strategy.max_turn, -self.strategy.max_turn)
        return self.strategy.actual_robot.turn(to_turn)