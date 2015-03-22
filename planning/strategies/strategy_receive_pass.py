from lib.math.util import clamp

__author__ = 'Sam Davies'

from lib.math.vector import Vector2D
import numpy as np
from planning.strategies.strategy import Strategy


class ReceivePass(Strategy):
    def __init__(self, world, robot_tag, actual_robot):
        super(ReceivePass, self).__init__(world, robot_tag, actual_robot)
        self.m.add_state("Start", self.start_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Follow Friend", self.follow_friend)
        self.m.add_final_state_and_action("Turn To Face Up", self.turn_robot_to_up)

        # set start state
        self.m.set_start("Start")

    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)

    # ------------------------------------ Transitions ------------------------------------

    def start_trans(self):
        if self.is_robot_facing_up():
            new_state = "Follow Friend"
        else:
            new_state = "Turn To Face Up"
        return new_state

    # -------------------------------------- Actions --------------------------------------

    def follow_friend(self):
        x = self.get_zone_centre()
        y = clamp(self.get_friend().position.y, max_val=80, min_val=30)
        vect_to_point = self.vector_from_robot_to_point(x, y)
        dist_to_point = vect_to_point.length()

        # reverse the distance when the intercept point is below the robot
        if vect_to_point.y < 0:
            dist_to_point = - dist_to_point

        return self.actual_robot.move(dist_to_point), "moving {0} cm to ({1}, {2})".format(dist_to_point, vect_to_point.x, vect_to_point.y)

    def turn_robot_to_up(self):
        # rotate to face up
        up_pos = Vector2D(self.robot.position.x, 150)
        to_turn = self.robot.angle_to_point(up_pos)
        return self.actual_robot.turn(to_turn), "turning {0} degrees to ({1}, {2})".format(int(360.0 * to_turn / (2 * np.pi)), up_pos.x, up_pos.y)

