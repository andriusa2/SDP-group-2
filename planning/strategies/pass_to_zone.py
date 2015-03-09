from lib.math.vector import Vector2D
from planning.strategies.strategy import Strategy
from planning.world.world_state import Zone
import numpy as np

__author__ = 'Sam Davies'


class PassToZone(Strategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(PassToZone, self).__init__(world, robot_tag, actual_robot)
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Pass Blocked", self.pass_blocked_trans)
        self.m.add_state("Pass Not Blocked", self.pass_not_blocked_trans)
        self.m.add_state("Grabber is Closed", self.grabber_open_trans)


        # End States / Actions
        self.m.add_final_state_and_action("Close Grabber", self.lower_cage)
        self.m.add_final_state_and_action("Turn to location", self.turn_to_location)
        self.m.add_final_state_and_action("Move to location", self.move_to_location)
        self.m.add_final_state_and_action("Turn to pass", self.turn_to_friend)
        self.m.add_final_state_and_action("Passing", self.pass_to_friend)

        # set start state
        self.m.set_start("Start")
        self.fetch_world_state()
        zone_centre = self.get_zone_centre()
        self.preset_pass_locations = [Vector2D(zone_centre, 90), Vector2D(zone_centre, 20)]

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
        if self.is_pass_blocked():
            new_state = "Pass Blocked"
        else:
            new_state = "Pass Not Blocked"
        return new_state

    def pass_blocked_trans(self):
        if self.is_robot_facing_point(self.determine_next_location()):
            new_state = "Move to location"
        else:
            new_state = "Turn to location"
        return new_state

    def pass_not_blocked_trans(self):
        if self.is_robot_facing_point(self.get_friend().position, beam_width=self.ROBOT_WIDTH):
            new_state = "Passing"
        else:
            new_state = "Turn to pass"
        return new_state

    def is_pass_blocked(self):
        # first find the location of your friend
        friend = self.get_friend()
        direction = (friend.position - self.robot.position).unit_vector()
        enemy_robot = self.get_enemy()
        if self.robot.is_point_within_beam(
            enemy_robot.position, direction,
            beam_width=self.ROBOT_WIDTH * 1.5):
            return True
        else:
            return False

    def turn_to_location(self):
        to_turn = self.robot.angle_to_point(self.determine_next_location())
        return self.actual_robot.turn(to_turn), "turning {0} degrees".format(int(360.0 * to_turn / (2 * np.pi)))

    def move_to_location(self):
        v = self.determine_next_location()
        to_move = self.distance_from_robot_to_point(v.x, v.y) * 0.4  # only move 90%
        return self.actual_robot.move(to_move), "moving {0} cm to ({1}, {2})".format(to_move, v.x, v.y)

    def determine_next_location(self):
        # find the furthest preset location
        self.fetch_world_state()
        v1 = self.preset_pass_locations[0]
        v2 = self.preset_pass_locations[1]
        dist_to_1 = self.distance_from_robot_to_point(v1.x, v1.y)
        dist_to_2 = self.distance_from_robot_to_point(v2.x, v2.y)

        max_distance = max(dist_to_1, dist_to_2)
        v = v1 if max_distance == dist_to_1 else v2
        print "Safe pass point: {0}".format(v)
        print "Robot {0}".format(self.robot)
        return v

    def turn_to_friend(self):
        friend_pos = self.get_friend().position
        to_turn = self.robot.angle_to_point(friend_pos)
        return self.actual_robot.turn(to_turn), "turning {0} degrees to ({1}, {2})".format(int(360.0 * to_turn / (2 * np.pi)), friend_pos.x, friend_pos.y)

    def pass_to_friend(self):
        return self.shoot()