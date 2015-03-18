from planning.strategies.strategy_pass_ball import PassToZone
from planning.strategies.strategy_receive_pass import ReceivePass
from planning.strategies.strategy_save_robot import SaveRobot

__author__ = 'Sam Davies'
import time
import numpy as np

from planning.strategies.strategy_fetch_ball import FetchBall
from planning.strategies.strategy_shoot_goal import ShootForGoal
from planning.strategies.strategy_block_goal import BlockGoal
from planning.strategies.strategy import Strategy
from planning.strategies.state_machine import StateMachine


class Planner(Strategy):
    """
    time the next action be performed before the previous action will finish
    """
    ACTION_COMPENSATION = 0

    def __init__(self, world, robot_tag, actual_robot, is_attacker):
        super(Planner, self).__init__(world, robot_tag, actual_robot)
        # when the next action can be performed
        self.can_act_after = time.time()
        self.is_attacker = is_attacker
        self.next_action_wait = 0
        self.action_trace = []

        self.fetch_ball = FetchBall(world, robot_tag, actual_robot)
        self.shoot_goal = ShootForGoal(world, robot_tag, actual_robot)

        self.block_goal = BlockGoal(world, robot_tag, actual_robot)
        self.pass_ball = PassToZone(world, robot_tag, actual_robot)
        self.receive_pass = ReceivePass(world, robot_tag, actual_robot)
        self.save_robot = SaveRobot(world, robot_tag, actual_robot)

        self.m = StateMachine()
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Robot is Safe", self.safe_robot_trans)
        self.m.add_state("Can Act", self.can_act_trans)

        self.m.add_state("Attacker Robot", self.attacker_robot_trans)
        self.m.add_state("Defender Robot", self.defender_robot_trans)

        self.m.add_state("ball in attacker zone", self.ball_in_attacker_zone_trans)

        self.m.add_state("ball in defender zone", self.ball_in_defender_zone_trans)
        self.m.add_state("ball not in defender zone", self.ball_not_in_defender_zone_trans)

        # End States / Actions
        self.m.add_final_state_and_action("waiting", action=self.do_nothing)
        self.m.add_final_state_and_action("shooting", action=self.do_shoot_goal)
        self.m.add_final_state_and_action("fetching ball", action=self.do_fetch_ball)
        self.m.add_final_state_and_action("blocking goal", action=self.do_block_goal)
        self.m.add_final_state_and_action("passing ball", action=self.do_pass_ball)
        self.m.add_final_state_and_action("receiving pass", action=self.do_receive_pass)
        self.m.add_final_state_and_action("Saving Robot", action=self.save_robot)

        # set start state
        self.m.set_start("Start")

    def plan(self):
        # update the world
        self.fetch_world_state()

        self.check_for_re_plan()

        action_state = self.m.run()
        self.next_action_wait, action_info = self.m.do_action(action_state)
        self.do_pretty_print(action_info)
        return self.next_action_wait

    def start_trans(self):
        if self.is_robot_safe():
            new_state = "Robot is Safe"
        else:
            new_state = "Saving Robot"
        return new_state

    def safe_robot_trans(self):
        if self.can_act():
            new_state = "Can Act"
        else:
            new_state = "waiting"
        return new_state

    def can_act_trans(self):
        if self.is_attacker:
            new_state = "Attacker Robot"
        else:
            new_state = "Defender Robot"
        return new_state

    def attacker_robot_trans(self):
        if self.is_ball_in_robot_zone():
            new_state = "ball in attacker zone"
        else:
            new_state = "waiting"
        return new_state

    def ball_in_attacker_zone_trans(self):
        if self.is_ball_close():
            new_state = "shooting"
        else:
            new_state = "fetching ball"
        return new_state

    def defender_robot_trans(self):
        if self.is_ball_in_robot_zone():
            new_state = "ball in defender zone"
        else:
            new_state = "ball not in defender zone"
        return new_state

    def ball_in_defender_zone_trans(self):
        if self.ball_going_quickly():
            new_state = "blocking goal"
        else:
            if self.is_ball_close():
                new_state = "passing ball"
            else:
                new_state = "fetching ball"
        return new_state

    def ball_not_in_defender_zone_trans(self):
        print "friend zone is {0}".format(self.world.get_zone(self.get_friend().position))
        if self.is_ball_in_friend_zone():
            print "receiving pass"
            new_state = "receiving pass"
        else:
            print "blocking goal"
            new_state = "blocking goal"
        return new_state

    def do_nothing(self):
        return False, "No Info"

    def can_act(self):
        # has the robot finished moving
        if self.can_act_after <= time.time():
            return True
        else:
            return False

    def do_fetch_ball(self):
        to_return = self.do_strategy(self.fetch_ball)
        self.world.do_refresh_kick = False
        return to_return

    def do_shoot_goal(self):
        self.world.do_refresh_kick = True
        return self.do_strategy(self.shoot_goal)

    def do_block_goal(self):
        self.world.do_refresh_kick = True
        return self.do_strategy(self.block_goal)

    def do_pass_ball(self):
        self.world.do_refresh_kick = True
        return self.do_strategy(self.pass_ball)

    def do_receive_pass(self):
        self.world.do_refresh_kick = True
        return self.do_strategy(self.receive_pass)

    def do_strategy(self, strategy):
        """
        performs the next action in the strategies and sets when we
        can next act based on how long it takes to perform that action
        :param strategy: the strategies on which to act
        :return: the time that we have to wait
        """
        cool_down_time_period, info = strategy.act()
        self.m.state_trace += strategy.m.state_trace
        self.can_act_after = time.time() + cool_down_time_period
        return cool_down_time_period, info

    def check_for_re_plan(self):
        # if ball moves while collecting the ball, re-plan
        if False:
            self.stop_robot()

        # if ball moves while turning with ball, re-plan
        if False:
            self.stop_robot()

    def stop_robot(self):
        pass

    def do_pretty_print(self, action_info):

        current_zone = self.world.get_zone(self.robot.position)
        dist_to_ball = self.distance_from_kicker_to_ball()
        angle_to_ball = self.robot.angle_to_point(self.ball.position)
        current_state = self.m.state_trace[len(self.m.state_trace)-2]
        action = self.m.state_trace[len(self.m.state_trace)-1]
        action_duration = self.next_action_wait
        is_attacker = self.is_attacker
        in_beam = self.is_robot_facing_ball()
        ball_zone = self.world.get_zone(self.ball.position)
        state_trace = self.m.state_trace
        is_ball_close = self.is_ball_close()

        friend = self.get_friend().position
        friend_zone = self.world.get_zone(friend)

        enemy_att = self.get_enemy().position
        enemey_att_zone = self.world.get_zone(enemy_att)

        enemy_def = self.get_enemy_defender().position
        enemey_def_zone = self.world.get_zone(enemy_def)

        my_pos = self.robot.position

        to_print = ""

        if action != 'WAITING':

            self.action_trace.append(action)
            if len(self.action_trace) > 9:
                self.action_trace.pop(0)

            to_print = self.pretty_print(current_zone, dist_to_ball, angle_to_ball, current_state, action, action_duration,
                                        is_attacker, in_beam, ball_zone, state_trace, action_info, is_ball_close,
                                        self.action_trace, friend, friend_zone, enemy_att, enemey_att_zone, enemy_def,
                                        enemey_def_zone, my_pos)
            print "\n"
            for line in to_print:
                print line


        return to_print

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

        return [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13, f0, f1, f2, f3, f4, p0, p1, p2, l14, l15, l16, l18]

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
            if not x%3:
                line += "\n|  "
        return line

    @staticmethod
    def pretty_grid(angle_to_ball, dist_to_ball):
        brackets = "[][][][][]"
        matrix = {'0': list(brackets), '1': list(brackets), '2': list(brackets), '-2': list(brackets), '-3': list(brackets)}
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
        return ["".join(matrix['2']), "".join(matrix['1']), "".join(matrix['0']), "".join(matrix['-2']), "".join(matrix['-3'])]




