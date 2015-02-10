__author__ = 'Sam Davies'
import time
from lib.strategy.attacker1 import Attacker1


class Planner(object):

    def __init__(self, world, robot_tag, actual_robot, is_attacker):

        self.is_acting = False

        # time to wait for the last command to be executed
        self.cool_down_time_period = 0.0
        # time since epoch
        self.last_cool_down_time = time.time()

        if is_attacker:
            self.attack_plan = self.attacker1 = Attacker1(world, robot_tag, actual_robot)

    def plan_defence(self):
        pass

    def plan_attack(self):

        # if ball moves while collecting the ball, re-plan
        if False:
            self.stop_robot()

        # if ball moves while turning with ball, re-plan
        if False:
            self.stop_robot()

        # if ball is in attacker zone, use attack plan
        if self.can_act():
            self.cool_down_time_period = self.attack_plan.act()

        # if ball is out of zone, return to middle and turn to face ball

    def can_act(self):
        if self.is_acting is False:
            pass

    def stop_robot(self):
        pass