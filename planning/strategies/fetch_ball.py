__author__ = 'Sam Davies'
import numpy as np
from planning.strategies.strategy import Strategy
from planning.strategies.state_machine import StateMachine


class FetchBall(Strategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(FetchBall, self).__init__(world, robot_tag, actual_robot)
        self.m = StateMachine()
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Grabber is Open", self.grabber_is_open_trans)

        # End States / Actions
        self.m.add_action("Open Grabber", self.open_grabber)
        self.m.add_action("Move to Ball", self.move_robot_to_ball)
        self.m.add_action("Turn to Ball", self.turn_robot_to_ball)

        # set start state
        self.m.set_start("Start")

    def act(self):
        self.fetch_world_state()
        print "ball is far away to robot"

        action_state = self.m.run()
        return self.m.do_action(action_state)

    ##------------------------------------ Transitions ------------------------------------

    def start_trans(self):
        if self.world.is_grabber_down:
            new_state = "Open Grabber"
        else:
            new_state = "Grabber is Open"
        return new_state

    def grabber_is_open_trans(self):
        if self.is_robot_facing_ball():
            new_state = "Move to Ball"
        else:
            new_state = "Turn to Ball"
        return new_state

    ##-------------------------------------- Actions --------------------------------------

    def open_grabber(self):
        return self.raise_cage()

    def turn_robot_to_ball(self):
        print "robot not facing ball"
        to_turn = self.robot.angle_to_point(self.ball.position)
        print "rotating robot " + str(360.0 * to_turn / (2 * np.pi)) + " degrees"
        return self.actual_robot.turn(to_turn)  # turn towards the the ball

    def move_robot_to_ball(self):
        print "robot facing ball"
        dist_to_ball = self.distance_from_kicker_to_ball() * 0.9  # only move 90%
        print "moving robot " + str(dist_to_ball)
        return self.actual_robot.move(dist_to_ball)