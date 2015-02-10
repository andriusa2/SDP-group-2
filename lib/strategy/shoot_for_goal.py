__author__ = 'Sam Davies'
from lib.strategy.generalized_strategy import GeneralizedStrategy


class ShootForGoal(GeneralizedStrategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(ShootForGoal, self).__init__(world, robot_tag, actual_robot)

    def act(self):
        if self.is_grabber_down:  # we must be holding the ball
            print "cage is down"
            if not self.is_robot_facing_goal():  # are we facing the goal?
                print "robot not facing goal"
                to_turn = self.robot.angle_to_point(self.world.goal)
                print "rotating robot " + str(to_turn) + " radians"
                self.actual_robot.turn(to_turn)  # turn towards the the goal

            else:  # we are facing the goal
                print "robot is facing goal"
                self.actual_robot.kick(power=1.0)  # kick

        else:  # lower the cage
            print "cage is up"
            self.lower_cage()