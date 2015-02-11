__author__ = 'samdavies'
from lib.strategy.generalized_strategy import GeneralizedStrategy


class BlockGoal(GeneralizedStrategy):
    def __init__(self, world, robot_tag, actual_robot):
        super(BlockGoal, self).__init__(world, robot_tag, actual_robot)

    def act(self):
        self.fetch_world_state()
        x = self.robot.x
        y = self.predict_y(self, x, ball)
        if y > self.robot.y:
        	if not is_sideways_up(self):
	        	robot_x = self.robot.x
	        	robot_y = self.robot.y
	        	set_point = (robot_x, robot_y + 20)
	        	to_turn = self.robot.angle_to_point(set_point)
	        	print "rotating robot to " str(to_turn) + " radians"
	        	self.actual_robot.turn(to_turn)
	        else:
	            dist_to_point = self.dist_from_robot_to_point(x, y)
	            print dist_to_point
	            self.actual_robot.move(dist_to_point)
	    else:
	    	if not sidewards(self):
	            robot_x = self.robot.x
	            set_point = (robot_x, 0)
	            to_turn = self.robot.angle_to_point(set_point)
	            print "rotating robot to " + str(to_turn) + " radians"
	            self.actual_robot.turn(to_turn)  # turn towards the sideline
	        else:
	        	dist_to_point - self.dist_from_robot_to_point(x, y)
	        	print dist_to_point
	        	self.actual_robot.move(dist_to_point)