import numpy as np

from lib.math.vector import Vector2D


__author__ = 'Sam Davies'
from planning.strategies.strategy import Strategy


class BlockGoal(Strategy):
    def __init__(self, world, robot_tag, actual_robot, config=None):
        super(BlockGoal, self).__init__(world, robot_tag, actual_robot, config)
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Robot is Square", self.is_square_trans)
        self.m.add_state("Robot in Centre", self.in_centre_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Open Grabber", self.other.open_grabber)
        self.m.add_final_state_and_action("Close Grabber", self.other.close_grabber)
        self.m.add_final_state_and_action("Intercept Ball", self.move.intercept_ball)
        self.m.add_final_state_and_action("Rotating To Be Square", self.turn.turn_to_closest_square_angle)
        self.m.add_final_state_and_action("Move Robot To Centre", self.move.move_to_centre_x)

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
        if self.is_robot_in_centre_x():
            new_state = "Robot in Centre"
        else:
            new_state = "Move Robot To Centre"
        return new_state

    def in_centre_trans(self):
        should_open = self.should_open_grabber()
        if should_open and self.world.is_grabber_closed:
            new_state = "Open Grabber"
        else:
            if (not should_open) and (not self.world.is_grabber_closed):
                new_state = "Close Grabber"
            else:
                new_state = "Intercept Ball"
        return new_state

    def should_open_grabber(self):
        """
        If the ball is in enemy attacker zone and travelling fast,
        then open the grabber (unless already open)
        """
        if self.ball_in_enemy_att_zone() and self.ball_is_fast():
            return True
        else:
            return False

