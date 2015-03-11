from lib.math.vector import Vector2D
import numpy as np

__author__ = 'samdavies'
from planning.strategies.strategy import Strategy


class BlockGoal(Strategy):
    def __init__(self, world, robot_tag, actual_robot):
        super(BlockGoal, self).__init__(world, robot_tag, actual_robot)
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Robot is Square", self.is_square_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Intercept Ball", self.intercept_ball)
        self.m.add_final_state_and_action("Turn To Face Up", self.turn_robot_to_up)
        self.m.add_final_state_and_action("Rotating To Be Square", self.turn_to_closest_square_angle)
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

    # -------------------------------------- Actions --------------------------------------

    def turn_to_closest_square_angle(self):

        # angle in range 0..2pi
        angle_to_turn = self.robot.direction.get_angle(Vector2D(1, 0)) + np.pi
        assert 0 <= angle_to_turn <= 2 * np.pi

        while angle_to_turn > np.pi / 2:
            angle_to_turn -= np.pi / 2

        if angle_to_turn > np.pi / 4:
            angle_to_turn -= np.pi / 2

        to_turn = -angle_to_turn
        info = "turning {0} degrees)".format(to_turn)
        return self.actual_robot.turn(to_turn), info

    def intercept_ball(self):
        x, y = self.y_intercept_of_ball_goal(self.goal, self.ball.position)
        vect_to_point = self.vector_from_robot_to_point(x, y)

        # multiply with the robots direction
        to_move = self.get_local_move(vect_to_point, self.robot.direction)

        info = "moving robot ({0}, {1}) cm to ({2}, {3})".format(to_move.x, to_move.y, vect_to_point.x,
                                                                 vect_to_point.y)
        print info
        return self.actual_robot.move(to_move.x, to_move.y, self.robot.direction), info

    def turn_robot_to_up(self):
        # rotate to face up
        up_pos = Vector2D(self.robot.position.x, 150)
        to_turn = self.robot.angle_to_point(up_pos)
        return self.actual_robot.turn(to_turn), "turning {0} degrees to ({1}, {2})".format(
            int(360.0 * to_turn / (2 * np.pi)), up_pos.x, up_pos.y)

