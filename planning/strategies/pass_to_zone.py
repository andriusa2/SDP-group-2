from lib.math.vector import Vector2D
from planning.strategies.strategy import Strategy
from planning.world.world_state import Zone

__author__ = 'Sam Davies'


class PassToZone(Strategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(PassToZone, self).__init__(world, robot_tag, actual_robot)
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Pass Blocked", self.pass_blocked_trans)
        self.m.add_state("Pass Not Blocked", self.pass_not_blocked_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Turn to location", self.turn_to_location)
        self.m.add_final_state_and_action("Move to location", self.move_to_location)
        self.m.add_final_state_and_action("Turn to pass", self.turn_to_friend)
        self.m.add_final_state_and_action("Passing", self.pass_to_friend)

        # set start state
        self.m.set_start("Start")

        self.friend = self.get_friend()
        self.preset_pass_locations = [Vector2D(self.robot.position.x, 120), Vector2D(self.robot.position.x, 10)]

    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)

    # ------------------------------------ Transitions ------------------------------------

    def start_trans(self):
        if self.is_pass_blocked():
            new_state = "Pass Blocked"
        else:
            new_state = "Pass Not Blocked"
        return new_state

    def pass_blocked_trans(self):
        if self.is_robot_facing_point(self.determine_next_location()):
            new_state = "Turn to location"
        else:
            new_state = "Move to location"
        return new_state

    def pass_not_blocked_trans(self):
        if self.is_robot_facing_point(self.determine_next_location()):
            new_state = "Passing"
        else:
            new_state = "Turn to pass"
        return new_state

    def is_pass_blocked(self):
        # first find the location of your friend
        friend = self.get_friend()
        direction = (friend.position - self.robot.position).unit_vector()
        enemy_robot = self.get_enemy()
        if self.robot.is_point_within_beam(enemy_robot.position, direction, beam_width=self.ROBOT_WIDTH*2):
            return True
        else:
            return False

    def turn_to_location(self):
        to_turn = self.robot.angle_to_point(self.determine_next_location())
        return self.actual_robot.turn(to_turn)

    def move_to_location(self):
        v = self.determine_next_location()
        to_move = self.distance_from_robot_to_point(v.x, v.y) * 0.9  # only move 90%
        return self.actual_robot.move(to_move)

    def determine_next_location(self):
        # find the furthest preset location
        v1 = self.preset_pass_locations[0]
        v2 = self.preset_pass_locations[1]
        dist_to_1 = self.distance_from_robot_to_point(v1.x, v1.y)
        dist_to_2 = self.distance_from_robot_to_point(v2.x, v2.y)

        max_distance = max(dist_to_1, dist_to_2)
        return v1 if max_distance == dist_to_1 else v2

    def turn_to_friend(self):
        to_turn = self.robot.angle_to_point(self.friend.position)
        return self.actual_robot.turn(to_turn)

    def pass_to_friend(self):
        return self.shoot()