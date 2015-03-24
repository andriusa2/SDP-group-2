from lib.math.util import clamp

__author__ = 'Sam Davies'


class Move(object):

    def __int__(self, strategy):
        self.strategy = strategy

    def intercept_ball(self):
        s = self.strategy
        x, y = s.y_intercept_of_ball_goal(s.goal, s.ball.position)
        vect_to_point = s.vector_from_robot_to_point(x, y)

        # multiply with the robots direction
        to_move = s.get_local_move(vect_to_point, s.robot.direction)

        info = "moving robot ({0}, {1}) cm to ({2}, {3})".format(to_move.x, to_move.y, vect_to_point.x,
                                                                 vect_to_point.y)
        return self._move_robot(to_move.x, to_move.y, info, s.robot.direction)

    def move_robot_to_ball(self):
        """
        Move the robot forward in a straight line to the ball
        :return: duration that the motors are on
        """
        dist_to_ball = self.strategy.distance_from_kicker_to_ball()
        info = "moving {0} cm".format(dist_to_ball)
        return self._move_robot(dist_to_ball, None, info)

    def move_to_centre_x(self):
        robot_y = self.strategy.robot.position.y
        centre_x = self.strategy.get_my_zone_centre()
        vect_to_point = self.strategy.vector_from_robot_to_point(centre_x, robot_y)

        # multiply with the robots direction
        to_move = self.strategy.get_local_move(vect_to_point, self.strategy.robot.direction)

        info = "moving robot ({0}, {1}) cm to ({2}, {3})".format(to_move.x, to_move.y, centre_x, robot_y)
        return self._move_robot(to_move.x, to_move.y, info, self.strategy.robot.direction)

    def move_to_centre_y(self):
        x = self.strategy.robot.position.x
        y = self.strategy.get_zone_centre_y()
        vect_to_point = self.strategy.vector_from_robot_to_point(x, y)

        to_move = self.strategy.get_local_move(vect_to_point, self.strategy.robot.direction)

        info = "moving robot ({0}, {1}) cm to ({2}, {3})".format(to_move.x, to_move.y, x, y)
        return self._move_robot(to_move.x, to_move.y, info, self.strategy.robot.direction)

    def _move_robot(self, x, y, info, direction=None):
        if x:
            x *= self.strategy.move_dampening
            x = clamp(x, self.strategy.max_move, -self.strategy.max_move)
        if y:
            y *= self.strategy.move_dampening
            y = clamp(y, self.strategy.max_move, -self.strategy.max_move)

        return self.strategy.actual_robot.move(x, y, direction), info