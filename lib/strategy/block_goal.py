__author__ = 'samdavies'

from lib.strategy.generalized_strategy import GeneralizedStrategy
import numpy as np

class BlockGoal(GeneralizedStrategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(BlockGoal, self).__init__(world, robot_tag, actual_robot)

    def act(self):
        self.fetch_world_state()
        if not self.sidewards:
      		robot_x = self.robot.x
      		set_point = (robot_x, 0)
      		to_turn = self.robot.angle_to_point(set_point)
       		print "rotating robot to " + str(to_turn) + " radians"
       		self.actual_robot.turn(to_turn) # turn towards the sideline
       	else:
       		x = self.robot.x
       		y = predict_y(self, x, ball)
       		dist_to_point = self.dist_from_robot_to_point(x,y)
       		print dist_to_point
       		self.actual_robot.move_forward(dist_to_point)
