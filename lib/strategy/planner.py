__author__ = 'Sam Davies'
import time
from lib.strategy.attacker1 import Attacker1
from lib.strategy.fetch_ball import FetchBall
from lib.strategy.shoot_for_goal import ShootForGoal
from lib.strategy.generalized_strategy import GeneralizedStrategy


class Planner(GeneralizedStrategy):

    """
    time the next action be performed before the previous action will finish
    """
    ACTION_COMPENSATION = 0

    def __init__(self, world, robot_tag, actual_robot, is_attacker):
        super(Planner, self).__init__(world, robot_tag, actual_robot)
        # when the next action can be performed
        self.can_act_after = time.time()

        # create all the attacking strategies
        if is_attacker:
            self.fetch_ball = FetchBall(world, robot_tag, actual_robot)
            self.shoot_goal = ShootForGoal(world, robot_tag, actual_robot)

        # create all the defending strategies
        if not is_attacker:
            pass

    def plan_defence(self):
        pass

    def plan_attack(self):
        # update the world
        self.fetch_world_state()

        self.check_for_re_plan()

        if self.can_act():
            # if ball is in attacker zone and not held, fetch ball
            self.do_strategy(self.fetch_ball)

            # if ball is close to kicker, shoot for goal
            # self.do_strategy(self.shoot_goal)

            # if ball is out of zone, return to middle and turn to face ball
            return True
        else:
            return False

    def can_act(self):
        # has the robot finished moving
        if self.can_act_after <= time.time():
            return True
        else:
            return False

    def do_strategy(self, strategy):
        """
        performs the next action in the strategy and sets when we
        can next act based on how long it takes to perform that action
        :param strategy: the strategy on which to act
        :return: nothing
        """
        cool_down_time_period = strategy.act()
        self.can_act_after = time.time() + (cool_down_time_period/1000.0)

    def check_for_re_plan(self):
        # if ball moves while collecting the ball, re-plan
        if False:
            self.stop_robot()

        # if ball moves while turning with ball, re-plan
        if False:
            self.stop_robot()

    def stop_robot(self):
        pass