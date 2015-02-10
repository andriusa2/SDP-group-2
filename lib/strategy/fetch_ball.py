__author__ = 'Sam Davies'
from lib.strategy.generalized_strategy import GeneralizedStrategy
import numpy as np


class FetchBall(GeneralizedStrategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(FetchBall, self).__init__(world, robot_tag, actual_robot)

    def act(self):
        self.fetch_world_state()
        print "ball is far away to robot"
            # cage not down

        if not self.is_robot_facing_ball():  # are we facing the ball?
            print "robot not facing ball"
            to_turn = self.robot.angle_to_point(self.ball.position)
            print "rotating robot " + str(360.0 * to_turn / (2 * np.pi)) + " degrees"
            return self.actual_robot.turn(to_turn)  # turn towards the the ball

        else:  # we're facing the ball
            print "robot facing ball"
            dist_to_ball = self.distance_from_kicker_to_ball()
            print "moving robot " + str(dist_to_ball)
            return self.actual_robot.move(dist_to_ball)