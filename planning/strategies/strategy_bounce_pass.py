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

    def __init__(self, world, robot_tag, actual_robot, config=None):
        super(BouncePass, self).__init__(world, robot_tag, actual_robot, config)
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Grabber is Closed", self.grabber_closed_trans)
        self.m.add_state("Robot In Center", self.is_centered_trans)
        self.m.add_state("Robot Not In Center", self.not_centered_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Close Grabber", self.other.close_grabber)
        self.m.add_final_state_and_action("Rotating To Be Square", self.turn.turn_to_closest_square_angle)
        self.m.add_final_state_and_action("Move To Center Y", self.move.move_to_centre_y)
        self.m.add_final_state_and_action("Turning to Face Bounce Point", self.turn.turn_to_bounce_point)
        self.m.add_final_state_and_action("Pass Ball", self.other.shoot)


        # set start state
        self.m.set_start("Start")

    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)

    # ------------------------------------ Transitions ------------------------------------

    def start_trans(self):
        if self.world.is_grabber_closed:
            new_state = "Grabber is Closed"
        else:
            new_state = "Close Grabber"
        return new_state

    def grabber_closed_trans(self):
        if self.is_robot_in_centre_y():
            new_state = "Robot In Center"
        else:
            new_state = "Robot Not In Center"
        return new_state

    def is_centered_trans(self):
        bounce_point = self.select_bounce_point()
        if self.is_robot_facing_point(bounce_point):
            new_state = "Pass Ball"
        else:
            new_state = "Turning to Face Bounce Point"
        return new_state

    def not_centered_trans(self):
        if self.is_at_square_angles():
            new_state = "Move To Center Y"
        else:
            new_state = "Rotating To Be Square"
        return new_state


