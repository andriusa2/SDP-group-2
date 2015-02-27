__author__ = 'Sam Davies'
import time
import numpy as np

from planning.strategies.fetch_ball import FetchBall
from planning.strategies.shoot_for_goal import ShootForGoal
from planning.strategies.block_goal import BlockGoal
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

        self.fetch_ball = FetchBall(world, robot_tag, actual_robot)
        self.shoot_goal = ShootForGoal(world, robot_tag, actual_robot)
        self.block_goal = BlockGoal(world, robot_tag, actual_robot)
        self.clear_ball = ShootForGoal(world, robot_tag, actual_robot)

        self.m = StateMachine()
        self.m.add_state("Start", self.start_trans)
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

        # set start state
        self.m.set_start("Start")

    def plan(self):
        # update the world
        self.fetch_world_state()

        self.check_for_re_plan()

        action_state = self.m.run()
        self.next_action_wait = self.m.do_action(action_state)
        self.do_pretty_print()
        return self.next_action_wait

    def start_trans(self):
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
        # if self.ball_going_quickly():
        #     new_state = "blocking goal"
        # else:
        #     new_state = "waiting"
        new_state = "blocking goal"
        return new_state

    def do_nothing(self):
        return False

    def can_act(self):
        # has the robot finished moving
        if self.can_act_after <= time.time():
            return True
        else:
            return False

    def do_fetch_ball(self):
        return self.do_strategy(self.fetch_ball)

    def do_shoot_goal(self):
        return self.do_strategy(self.shoot_goal)

    def do_block_goal(self):
        return self.do_strategy(self.block_goal)

    def do_clear_ball(self):
        return self.do_strategy(self.clear_ball)

    def do_strategy(self, strategy):
        """
        performs the next action in the strategies and sets when we
        can next act based on how long it takes to perform that action
        :param strategy: the strategies on which to act
        :return: the time that we have to wait
        """
        cool_down_time_period = strategy.act()
        self.m.state_trace += strategy.m.state_trace
        self.can_act_after = time.time() + cool_down_time_period
        return cool_down_time_period

    def check_for_re_plan(self):
        # if ball moves while collecting the ball, re-plan
        if False:
            self.stop_robot()

        # if ball moves while turning with ball, re-plan
        if False:
            self.stop_robot()

    def stop_robot(self):
        pass

    def do_pretty_print(self):

        current_zone = self.world.get_zone(self.robot.position)
        dist_to_ball = self.distance_from_kicker_to_ball()
        angle_to_ball = int(360.0 * self.robot.angle_to_point(self.ball.position) / (2 * np.pi))
        current_state = self.m.state_trace[len(self.m.state_trace)-2]
        action = self.m.state_trace[len(self.m.state_trace)-1]
        action_duration = self.next_action_wait
        is_attacker = self.is_attacker
        in_beam = self.is_robot_facing_ball()
        ball_zone = self.world.get_zone(self.ball.position)
        state_trace = self.m.state_trace

        to_print = self.pretty_print(current_zone, dist_to_ball, angle_to_ball, current_state, action, action_duration,
                                     is_attacker, in_beam, ball_zone)

        print ""
        for line in to_print:
            print line

        return to_print

    def pretty_print(self, current_zone, dist_to_ball, angle_to_ball, current_state, action, action_duration,
                     is_attacker, in_beam, ball_zone):
        """
            Robot - Attacker - Zone 1
            --------------------------------------------------
            |    [][][][][]  | State      : GRABBER IS OPEN
            |    [][][][][]  | Action     : TURN TO BALL
            | R->[][][][][]  | Duration   : 0.5 seconds
            |    []::[][][]  |--------------------------------
            |    [][][][][]  | Ball Angle : 45 deg (IN BEAM)
            |    <--10cm-->  | Ball Zone  : 1
            --------------------------------------------------
            |  Ball is 4cm away
            |  Ball is Far from robot
            --------------------------------------------------
            | State Trace ...
            | -> [CAN ACT]          -> [ATTACKER ROBOT]     -> [BALL IN ATTACKER ZONE]
            | -> [FETCHING BALL]    -> [GRABBER IS OPEN]    -> [MOVE TO BALL]
            | ...
            | ...
            --------------------------------------------------
        """
        grid = self.pretty_grid(angle_to_ball, dist_to_ball)
        role = "Attacker" if is_attacker else "Defender"
        beam = "(IN BEAM)" if in_beam else ""

        l1 = "Robot - {0} - Zone {1}".format(role, current_zone)
        l2 = "--------------------------------------------------"
        l3 = "|    {0}  | State      : {1}".format(grid[0], current_state)
        l4 = "|    {0}  | Action     : {1}".format(grid[1], action)
        l5 = "| R->{0}  | Duration   : {1} seconds".format(grid[2], action_duration)
        l6 = "|    {0}  |--------------------------------".format(grid[3])
        l7 = "|    {0}  | Ball Angle : {1} deg {2}".format(grid[4], angle_to_ball, beam)
        l8 = "|    <--10cm-->  | Ball Zone  : {0}".format(ball_zone)
        l9 = "--------------------------------------------------"

        return [l1, l2, l3, l4, l5, l6, l7, l8, l9]

    @staticmethod
    def pretty_grid(angle_to_ball, dist_to_ball):
        g0 = "[][][][][]"
        g1 = "[][][][][]"
        g2 = "[][][][][]"
        g3 = "[][][][][]"
        g4 = "[][][][][]"

        return [g0, g1, g2, g3, g4]


