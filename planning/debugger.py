import json
import requests
import numpy as np
from planning.decorators import async

__author__ = 'Sam Davies'


class Debugger(object):

    def __init__(self, planner):
        self.planner = planner

    def do_pretty_print(self, action_info):

        current_zone = self.planner.world.get_zone(self.planner.robot.position)
        dist_to_ball = self.planner.distance_from_kicker_to_ball()
        angle_to_ball = self.planner.robot.angle_to_point(self.planner.ball.position)
        current_state = self.planner.m.state_trace[len(self.planner.m.state_trace) - 2]
        action = self.planner.m.state_trace[len(self.planner.m.state_trace) - 1]
        action_duration = self.planner.next_action_wait
        is_attacker = self.planner.is_attacker
        in_beam = self.planner.is_robot_facing_ball()
        ball_zone = self.planner.world.get_zone(self.planner.ball.position)
        state_trace = self.planner.m.state_trace
        is_ball_close = self.planner.is_ball_close()

        friend = self.planner.get_friend().position
        friend_zone = self.planner.world.get_zone(friend)

        enemy_att = self.planner.get_enemy().position
        enemey_att_zone = self.planner.world.get_zone(enemy_att)

        enemy_def = self.planner.get_enemy_defender().position
        enemey_def_zone = self.planner.world.get_zone(enemy_def)

        my_pos = self.planner.robot.position

        to_print = ""

        if action != 'WAITING':

            self.planner.action_trace.append(action)
            if len(self.planner.action_trace) > 9:
                self.planner.action_trace.pop(0)

            data = {'current_zone': current_zone, 'dist_to_ball': dist_to_ball,
                    'angle_to_ball': angle_to_ball, 'current_state': current_state, 'action': action,
                    'action_duration': action_duration, 'is_attacker': is_attacker, 'in_beam': in_beam,
                    'ball_zone': ball_zone, 'state_trace': state_trace, 'action_info': action_info,
                    'is_ball_close': is_ball_close, 'action_trace': self.planner.action_trace, 'friend': friend.to_array(),
                    'friend_zone': friend_zone, 'enemy_att': enemy_att.to_array(), 'enemy_att_zone': enemey_att_zone,
                    'enemy_def': enemy_def.to_array(), 'enemy_def_zone': enemey_def_zone, 'my_pos': my_pos.to_array()}

            payload_json = json.dumps(data)
            self.send_async_heartbeat(payload_json)

            to_print = self.pretty_print(current_zone, dist_to_ball, angle_to_ball, current_state, action,
                                         action_duration,
                                         is_attacker, in_beam, ball_zone, state_trace, action_info, is_ball_close,
                                         self.planner.action_trace, friend, friend_zone, enemy_att, enemey_att_zone, enemy_def,
                                         enemey_def_zone, my_pos)
            print "\n"
            for line in to_print:
                print line

        return to_print

    @async
    def send_async_heartbeat(self, payload_json):
        r = requests.post('https://robot-heartbeat.herokuapp.com/set/', data=dict(payload=payload_json))
        print r

    def pretty_print(self, current_zone, dist_to_ball, angle_to_ball, current_state, action, action_duration,
                     is_attacker, in_beam, ball_zone, state_trace, action_info, is_ball_close, action_trace,
                     friend, friend_zone, enemy_att, enemey_att_zone, enemy_def, enemey_def_zone, my_pos):
        """
            Robot - Attacker - Zone 1
            --------------------------------------------------
            |    [][][][][]  | State      : GRABBER IS OPEN
            |    [][][][][]  | Action     : TURN TO BALL
            | R->[][][][][]  | Duration   : 0.5 seconds
            |    []::[][][]  |--------------------------------
            |    [][][][][]  | Rotating 24 degrees
            |    <--10cm-->  |
            --------------------------------------------------
            |  Ball is 4cm away
            |  Ball is Far from robot
            |  Ball at Angle : 45 deg (IN BEAM)
            |  Ball Zone  : 1
            --------------------------------------------------
            |  I'm in zone 1 at (0, 0)
            |  Friend in zone 3 at (0, 0)
            |  Enemy attacker in zone 2 at (0, 0)
            |  Enemy defender in zone 4 at (0, 0)
            --------------------------------------------------
            |  Previous 9 Actions ...
            |  -> [TURN TO BALL] -> [MOVE TO BALL] -> [TURN TO GOAL]
            |  -> [TURN TO BALL] -> [MOVE TO BALL] -> [TURN TO GOAL]
            |  -> [TURN TO BALL] -> [MOVE TO BALL] -> [TURN TO GOAL] <- NEW ACTION
            --------------------------------------------------
            |  State Trace ...
            |  -> [CAN ACT]          -> [ATTACKER ROBOT]     -> [BALL IN ATTACKER ZONE]
            |  -> [FETCHING BALL]    -> [GRABBER IS OPEN]    -> [TURN TO BALL]
            |  ...
            |  ...
            --------------------------------------------------
        """
        grid = self.pretty_grid(angle_to_ball, dist_to_ball)
        role = "Attacker" if is_attacker else "Defender"
        beam = "(IN BEAM)" if in_beam else ""
        close = "close to" if is_ball_close else "far from"

        l1 = "Robot - {0} - Zone {1}".format(role, current_zone)
        l2 = "--------------------------------------------------"
        l3 = "|    {0}  | State      : {1}".format(grid[0], current_state)
        l4 = "|    {0}  | Action     : {1}".format(grid[1], action)
        l5 = "| R->{0}  | Duration   : {1} seconds".format(grid[2], action_duration)
        l6 = "|    {0}  |--------------------------------".format(grid[3])
        l7 = "|    {0}  | {1}".format(grid[4], action_info)
        l8 = "|    <--10cm-->  |"
        l9 = "--------------------------------------------------"
        l10 = "|  Ball is {0}cm away".format(dist_to_ball)
        l11 = "|  Ball is {0} robot".format(close)
        l12 = "|  Ball at angle : {0} deg {1}".format(int(360.0 * angle_to_ball / (2 * np.pi)), beam)
        l13 = "|  Ball Zone : {0}".format(ball_zone)
        f0 = "--------------------------------------------------"
        f1 = "|  I'm in zone {0} at ({1}, {2})".format(current_zone, my_pos.x, my_pos.y)
        f2 = "|  Friend in zone {0} at ({1}, {2})".format(friend_zone, friend.x, friend.y)
        f3 = "|  Enemy attacker in zone {0} at ({1}, {2})".format(enemey_att_zone, enemy_att.x, enemy_att.y)
        f4 = "|  Enemy defender in zone {0} at ({1}, {2})".format(enemey_def_zone, enemy_def.x, enemy_def.y)
        p0 = "--------------------------------------------------"
        p1 = "|  Previous 9 Actions ..."
        p2 = "|  "
        p2 += self.print_states(action_trace)
        l14 = "--------------------------------------------------"
        l15 = "|  State Trace ..."
        l16 = "|  "
        l16 += self.print_states(state_trace)
        l18 = "--------------------------------------------------"

        return [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13, f0, f1, f2, f3, f4, p0, p1, p2, l14, l15, l16,
                l18]

    @staticmethod
    def print_states(states):
        line = ""
        x = 0
        for state in states:
            length = len(state)
            padding = 16 - length
            x += 1
            line += "-> %s" % state
            line += " " * padding
            if not x % 3:
                line += "\n|  "
        return line

    @staticmethod
    def pretty_grid(angle_to_ball, dist_to_ball):
        brackets = "[][][][][]"
        matrix = {'0': list(brackets), '1': list(brackets), '2': list(brackets), '-2': list(brackets),
                  '-3': list(brackets)}
        """dist_to_x = dist_to_ball * np.cos(abs(angle_to_ball))
        index = int(dist_to_x)/2 * 2
        dist_to_y = dist_to_ball * np.sin(abs(angle_to_ball))
        if angle_to_ball < 0:
            dist_to_y = - dist_to_y
        if dist_to_y > 5 or dist_to_y < -5 or dist_to_x > 10 or angle_to_ball > np.pi/2 or angle_to_ball < np.pi/-2:
            return ["".join(matrix['2']), "".join(matrix['1']), "".join(matrix['0']), "".join(matrix['-2']), "".join(matrix['-3'])]
        if dist_to_y >= -1:
            row = int(dist_to_y + 1)/2
        else:
            row = int(dist_to_y -1)/2
        matrix[str(row)][index] = ':'
        matrix[str(row)][index + 1] = ":"""
        return ["".join(matrix['2']), "".join(matrix['1']), "".join(matrix['0']), "".join(matrix['-2']),
                "".join(matrix['-3'])]
