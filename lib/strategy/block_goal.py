__author__ = 'samdavies'
from lib.strategy.generalized_strategy import GeneralizedStrategy
import numpy as np


class BlockGoal(GeneralizedStrategy):
    def __init__(self, world, robot_tag, actual_robot):
        super(BlockGoal, self).__init__(world, robot_tag, actual_robot)

    def act(self):
        self.fetch_world_state()

        # is the robot facing up?
        if self.is_robot_facing_up():
            print "robot is facing up"
            to_move_x = self.robot.position.x
            to_move_y = self.predict_y(to_move_x)

            # should the robot move up?
            to_move = self.distance_from_robot_to_point(to_move_x, to_move_y)
            if to_move_y > self.robot.position.y:

                print "moving robot up " + str(to_move)
                return self.actual_robot.move(to_move)
            else:
                print "moving robot down " + str(to_move)
                return self.actual_robot.move(-to_move)
        else:
            # rotate to face up
            to_turn = self.robot.angle_to_point(self.ball.position)
            print "rotating robot " + str(360.0 * to_turn / (2 * np.pi)) + " degrees"
            return self.actual_robot.turn(to_turn)  # turn towards up
