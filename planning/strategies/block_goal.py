__author__ = 'samdavies'
import numpy as np

from planning.strategies.strategy import Strategy
from lib.math.vector import Vector2D


class BlockGoal(Strategy):
    def __init__(self, world, robot_tag, actual_robot):
        super(BlockGoal, self).__init__(world, robot_tag, actual_robot)
        self.m.add_state("Start", self.start_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Intercept Ball", self.intercept_ball)
        self.m.add_final_state_and_action("Turn To Face Up", self.turn_robot_to_ball)

        # set start state
        self.m.set_start("Start")

    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)

    ##------------------------------------ Transitions ------------------------------------

    def start_trans(self):
        if self.is_robot_facing_up():
            new_state = "Intercept Ball"
        else:
            new_state = "Turn To Face Up"
        return new_state

    ##-------------------------------------- Actions --------------------------------------

    def intercept_ball(self):
        x, y = self.y_intercept_of_ball_goal(self.robot.position, self.goal, self.ball.position)
        vect_to_point = self.vector_from_robot_to_point(x, y)
        dist_to_point = vect_to_point.length()

        # reverse the distance when the intercept point is below the robot
        if vect_to_point.y < 0:
            dist_to_point = - dist_to_point

        return self.actual_robot.move(dist_to_point)

    """def act(self):
        self.fetch_world_state()

        # is the robot facing up?
        if self.is_robot_facing_up():
            print "robot is facing up"
            to_move_x = self.robot.position.x
            to_move_y = self.predict_y(to_move_x)
            if not (0 < to_move_y < 110):
                to_move_y = 55
            print 'Moving to {0!r}'.format((to_move_x, to_move_y))
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
            print "rotating to face up"
            up_pos = Vector2D(self.robot.position.x, 150)
            print "up is at " + str(up_pos.x) + ", " + str(up_pos.y) 
            print "robot at {0}; {1}".format(self.robot.position.x, self.robot.position.y)
            to_turn = self.robot.angle_to_point(up_pos)
            print "rotating robot " + str(360.0 * to_turn / (2 * np.pi)) + " degrees"
            return self.actual_robot.turn(to_turn) # turn towards up"""
