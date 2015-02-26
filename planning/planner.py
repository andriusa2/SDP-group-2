__author__ = 'Sam Davies'
import time

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
        return self.m.do_action(action_state)

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
        if self.ball_going_quickly():
            new_state = "blocking goal"
        else:
            new_state = "waiting"
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
        print "cool down period of {0}".format(cool_down_time_period)
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


    def pretty_print(self, current_zone, dist_to_ball, angle_to_ball, current_state, action, action_duration, is_attacker, beam_width, ball_zone, ball_pos):
        """
            Robot - Attacker - Zone 1
            --------------------------------------------------
            |    [][][][][]  | State      : GRABBER IS OPEN    |
            |    [][][][][]  | Action     : TURN TO BALL       |
            | R->[][][][][]  | Duration   : 0.5 seconds        |
            |    []::[][][]  |---------------------------------|
            |    [][][][][]  | Ball Angle : 45 deg (IN BEAM)   |
            |    <--10cm-->  | Ball Zone  : 1                  |
            --------------------------------------------------
        """
        robot_matrix = self.pretty_helper(angle_to_ball, dist_to_ball, ball_pos)
        if is_attacker:
            isAttacker = "Attacker"
        else:
            isAttacker = "Defender"
        print "\nRobot - ", isAttacker, " - Zone ", current_zone
        print "--------------------------------------------------"
        print "|", robot_matrix[0],"| State      : ", current_state
        print "|", robot_matrix[1],"| Action     : ", action
        print "|", robot_matrix[2],"| Duration   : ", action_duration, " seconds"
        print "|", robot_matrix[3],"|---------------------------------"
        if angle_to_ball <= beam_width:
            inBeam = "(IN BEAM)"
        else:
            inBeam = "(OUTSIDE BEAM)"
        print "|", robot_matrix[4],"| Ball Angle : ", angle_to_ball, " ", inBeam
        print "|", robot_matrix[5],"| Ball Zone  : ", ball_zone
        print "--------------------------------------------------"

    def pretty_helper(self, angle_to_ball, dist_to_ball, ball_pos):
        matrix = [0] * 6
        matrix[0] = "    [][][][][]  "
        matrix[1] = "    [][][][][]  "
        matrix[2] = " R->[][][][][]  "
        matrix[3] = "    [][][][][]  "
        matrix[4] = "    [][][][][]  "
        matrix[5] = "    <--10cm-->  "
        if angle_to_ball < 15:
            if dist_to_ball <= 10 and dist_to_ball > 8:
                matrix[2] = " R->[][][][]::  "
            elif dist_to_ball <= 8 and dist_to_ball > 6:
                matrix[2] = " R->[][][]::[]  "
            elif dist_to_ball <= 6 and dist_to_ball > 4:
                matrix[2] = " R->[][]::[][]  "
            elif dist_to_ball <= 4 and dist_to_ball > 2:
                matrix[2] = " R->[]::[][][]  "
            elif dist_to_ball <= 2:
                matrix[2] = " R->::[][][][]  "
        elif angle_to_ball < 30 and angle_to_ball >= 15 and ball_pos == "left":
            if dist_to_ball <= 10 and dist_to_ball > 8:
                matrix[1] = "    [][][][]::  "
            elif dist_to_ball <= 8 and dist_to_ball > 6:
                matrix[1] = "    [][][]::[]  "
            elif dist_to_ball <= 6 and dist_to_ball > 4:
                matrix[1] = "    [][]::[][]  "
            elif dist_to_ball <= 4 and dist_to_ball > 2:
                matrix[1] = "    []::[][][]  "
            elif dist_to_ball <= 2:
                matrix[1] = "    ::[][][][]  "
        elif angle_to_ball < 45 and angle_to_ball >=30 and ball_pos == "left":
            if dist_to_ball <= 10 and dist_to_ball > 8:
                matrix[0] = "    [][][][]::  "
            elif dist_to_ball <= 8 and dist_to_ball > 6:
                matrix[0] = "    [][][]::[]  "
            elif dist_to_ball <= 6 and dist_to_ball > 4:
                matrix[0] = "    [][]::[][]  "
            elif dist_to_ball <= 4 and dist_to_ball > 2:
                matrix[0] = "    []::[][][]  "
            elif dist_to_ball <= 2:
                matrix[0] = "    ::[][][][]  "
        elif angle_to_ball < 30  and angle_to_ball >=15 and ball_pos == "right":
            if dist_to_ball <= 10 and dist_to_ball > 8:
                matrix[3] = "    [][][][]::  "
            elif dist_to_ball <= 8 and dist_to_ball > 6:
                matrix[3] = "    [][][]::[]  "
            elif dist_to_ball <= 6 and dist_to_ball > 4:
                matrix[3] = "    [][]::[][]  "
            elif dist_to_ball <= 4 and dist_to_ball > 2:
                matrix[3] = "    []::[][][]  "
            elif dist_to_ball <= 2:
                matrix[3] = "    ::[][][][]  "
        elif angle_to_ball < 45  and angle_to_ball >= 30 and ball_pos == "right":
            if dist_to_ball <= 10 and dist_to_ball > 8:
                matrix[4] = "    [][][][]::  "
            elif dist_to_ball <= 8 and dist_to_ball > 6:
                matrix[4] = "    [][][]::[]  "
            elif dist_to_ball <= 6 and dist_to_ball > 4:
                matrix[4] = "    [][]::[][]  "
            elif dist_to_ball <= 4 and dist_to_ball > 2:
                matrix[4] = "    []::[][][]  "
            elif dist_to_ball <= 2:
                matrix[4] = "    ::[][][][]  "
        return matrix


