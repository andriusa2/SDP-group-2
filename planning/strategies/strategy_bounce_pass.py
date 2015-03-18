from lib.math.vector import Vector2D
from planning.strategies.strategy import Strategy

__author__ = 'Sam Davies'


class BouncePass(Strategy):

    """
    OVERALL PLAN
    ----------------------------
    Make robot turn to be square
    Move to the X centre
    Move to the Y centre
    Turn the Pass Point
    Pass the Ball
    """

    def __init__(self, world, robot_tag, actual_robot):
        super(BouncePass, self).__init__(world, robot_tag, actual_robot)
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Grabber is Closed", self.grabber_open_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Close Grabber", self.actions.lower_cage)

        # set start state
        self.m.set_start("Start")

    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)

    # ------------------------------------ Transitions ------------------------------------

    def start_trans(self):
        if self.world.is_grabber_down:
            new_state = "Grabber is Closed"
        else:
            new_state = "Close Grabber"
        return new_state

    def grabber_open_trans(self):
        if True:
            new_state = ""
        else:
            new_state = ""
        return new_state

    def select_bounce_point(self):
        """
        Determine the bounce point, either up or down, which is furthest from the enemy robot
        :return: a Vector2D
        """
        pass

    def move_to_centre_y(self):
        info = ""
        return 0, info  # duration and information about the movement

    def turn_to_bounce_point(self):
        info = ""
        return 0, info

    def bounce_pass(self):
        info = ""
        return 0, info