from planning.strategies.strategy_bounce_pass import BouncePass

__author__ = 'Sam Davies'
import time

from planning.debugger import Debugger

# Strategies
from planning.strategies.strategy_pass_ball import PassToZone
from planning.strategies.strategy_receive_pass import ReceivePass
from planning.strategies.strategy_save_robot import SaveRobot
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

    def __init__(self, world, robot_tag, actual_robot, is_attacker, config=None, debug=False):
        super(Planner, self).__init__(world, robot_tag, actual_robot, config)
        # when the next action can be performed
        self.debug = debug
        self.debugger = Debugger(self)
        self.can_act_after = time.time()
        self.is_attacker = is_attacker
        self.next_action_wait = 0
        self.action_trace = []

        self.fetch_ball = FetchBall(world, robot_tag, actual_robot, config)
        self.shoot_goal = ShootForGoal(world, robot_tag, actual_robot, config)

        self.block_goal = BlockGoal(world, robot_tag, actual_robot, config)
        self.pass_ball = BouncePass(world, robot_tag, actual_robot, config)
        self.receive_pass = ReceivePass(world, robot_tag, actual_robot, config)
        self.save_robot = SaveRobot(world, robot_tag, actual_robot, config)

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
        if self.debug:
            self.debugger.do_pretty_print(action_info)
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
            new_state = "blocking goal"
        else:
            new_state = "blocking goal"
        return new_state

    @staticmethod
    def do_nothing():
        return False, "No Info"

    def can_act(self):
        # has the robot finished moving
        # if self.can_act_after <= time.time():
        #     return True
        # else:
        #     return False
        return self.actual_robot.is_available()

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
        _, info = strategy.act()
        self.m.state_trace += strategy.m.state_trace
        # self.can_act_after = time.time() + cool_down_time_period
        return 0, info

    def check_for_re_plan(self):
        # if ball moves while collecting the ball, re-plan
        if False:
            self.stop_robot()

        # if ball moves while turning with ball, re-plan
        if False:
            self.stop_robot()

    def stop_robot(self):
        pass