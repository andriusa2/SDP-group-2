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
        self.m.add_state("Robot Is Square", self.is_square_trans)
        self.m.add_state("Robot In Center", self.is_centered_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Close Grabber", self.actions.lower_cage)
        self.m.add_final_state_and_action("Rotating To Be Square", self.actions.turn_to_closest_square_angle)
        self.m.add_final_state_and_action("Move To Center", self.actions.move_to_center)
        self.m.add_final_state_and_action("Robot Not Facing Point", self.actions.turn_robot_to_point(self.select_bounce_point()))
        self.m.add_final_state_and_action("Robot Facing Pass Point", self.actions.shoot())

        # set start state
        self.m.set_start("Start")
        enemy_zone_center = self.get_zone_center(self.get_enemy().position)
        self.preset_pass_locations = [Vector2D(enemy_zone_center, 110), Vector2D(enemy_zone_centre, 0)]

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
        if self.is_at_square_angles():
            new_state = "Robot Is Square"
        else:
            new_state = "Rotating To Be Square"
        return new_state

    def robot_is_square_trans(self):
        if self.is_robot_in_center():
            new_state = "Robot In Center"
        else:
            new_state = "Move To Center"
        return new_state

    def is_centered_trans:
        bounce_point = self.select_bounce_point()
        if is_robot_facing_point(bounce_point, beam_width=self.ROBOT_WIDTH):
            new_state = "Robot Facing Pass Point"
        else:
            new_state = "Robot Not Facing Point"
        return new_state

    def select_bounce_point(self):
        """
        Determine the bounce point, either up or down, which is furthest from the enemy robot
        :return: a Vector2D
        """
        enemy_position_x = self.get_enemy().position.x
        enemy_position_y = self.get_enemy().position.y
        v1 = self.preset_pass_locations[0]
        v2 = self.preset_pass_locations[1]
        dist_to_1 = self.dist_to_pass_point(enemy_position_x, enemy_position_y, v1.x, v1.y)
        dist_to_2 = self.dist_to_pass_point(enemy_position_x, enemy_position_y, v2.x, v2.y)

        max_distance = max(dist_to_1, dist_to_2)
        v = v1 if max_distance == dist_to_1 else v2
        return v

        


    def move_to_centre_y(self):
        info = ""
        return 0, info  # duration and information about the movement

    def turn_to_bounce_point(self):
        info = ""
        return 0, info

    def bounce_pass(self):
        info = ""
        return 0, info