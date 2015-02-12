__author__ = 'Sam Davies'
import time
from lib.strategy.fetch_ball import FetchBall
from lib.strategy.shoot_for_goal import ShootForGoal
from lib.strategy.block_goal import BlockGoal
from lib.strategy.strategy import Strategy


class Planner(Strategy):

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
            self.block_goal = BlockGoal(world, robot_tag, actual_robot)
            self.fetch_ball = FetchBall(world, robot_tag, actual_robot)
            self.clear_ball = ShootForGoal(world, robot_tag, actual_robot)

    def plan_defence(self):
        self.fetch_world_state()

        if self.can_act:

            zone_ball = self.world.get_zone(self.ball.position)
            zone_robot = self.world.get_zone(self.robot.position)

            if zone_ball == zone_robot:
                print "ball in robot's zone"
                if self.ball_going_quickly():
                    print "Ball going quickly. Block the goal"
                    return self.do_strategy(self.block_goal)
                else:
                    if not self.is_ball_close():
                        print "Ball is (near) stationary. Get the ball"
                        return self.do_strategy(self.fetch_ball)
                    else:
                        print "Ball is held. Kick ball upfield"
                        return self.do_strategy(self.clear_ball)
            else:
                if self.ball_going_quickly():
                    print "ball is not in robot's zone but moving quickly. Block the ball"
                    return self.do_strategy(self.block_goal)
                else:
                    # print "ball is not in robot's zone and stationary. Pass"
                    return 0

        else:
            return False

    def plan_attack(self):
        # update the world
        self.fetch_world_state()

        self.check_for_re_plan()

        if self.can_act():

            zone_ball = self.world.get_zone(self.ball.position)
            zone_robot = self.world.get_zone(self.robot.position)

            if zone_ball == zone_robot:  # is the ball in our zone?
                print "ball in robot's zone"
                # if ball is in attacker zone and not held, fetch ball
                if not self.is_ball_close():
                    return self.do_strategy(self.fetch_ball)
                else:
                    # if ball is close to kicker, shoot for goal
                    return self.do_strategy(self.shoot_goal)
            else:
                # print "ball not in robot's zone"
                # self.is_robot_facing_ball()
                return 0

            # if ball is out of zone, return to middle and turn to face ball
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
        :return: the time that we have to wait
        """
        cool_down_time_period = strategy.act()
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