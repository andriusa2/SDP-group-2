import numpy as np

from lib.math.vector import Vector2D


__author__ = 'Sam Davies'
from planning.strategies.strategy import Strategy


class BlockGoal(Strategy):
    def __init__(self, world, robot_tag, actual_robot):
        super(BlockGoal, self).__init__(world, robot_tag, actual_robot)
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Robot is Square", self.is_square_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Intercept Ball", self.actions.intercept_ball)
        self.m.add_final_state_and_action("Rotating To Be Square", self.actions.turn_to_closest_square_angle)
        self.m.add_final_state_and_action("Move Robot To Centre", self.actions.move_to_centre)

        # set start state
        self.m.set_start("Start")

    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)

    # ------------------------------------ Transitions ------------------------------------

    def start_trans(self):
        if self.is_at_square_angles():
            new_state = "Robot is Square"
        else:
            new_state = "Rotating To Be Square"
        return new_state

    def is_square_trans(self):
        if self.is_robot_in_centre():
            new_state = "Intercept Ball"
        else:
            new_state = "Move Robot To Centre"
        return new_state

