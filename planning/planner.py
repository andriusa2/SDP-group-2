__author__ = 'Sam Davies'
import time

from planning.strategies.fetch_ball import FetchBall
from planning.strategies.shoot_for_goal import ShootForGoal
from planning.strategies.block_goal import BlockGoal
from planning.strategies.strategy import Strategy


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
        performs the next action in the strategies and sets when we
        can next act based on how long it takes to perform that action
        :param strategy: the strategies on which to act
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

    def pretty_print(self, current_zone, dist_to_ball, angle_to_ball, current_state, action, action_duration, is_attacker, beam_width, ball_zone):
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
        robot_matrix = selfpretty_helper(self, angle_to_ball, dist_to_ball)
        if is_attacker:
            isAttacker = "Attacker"
        else:
            isAttacker = "Defender"
        print("Robot - ", isAttacker, " - Zone ", current_zone)
        print("--------------------------------------------------")
        print("|", robot_matrix[0],"| State      : ", current_state)
        print("|", robot_matrix[1],"| Action     : ", action)
        print("|", robot_matrix[2],"| Duration   : ", action_duration, " seconds")
        print("|", robot_matrix[3],"|---------------------------------")
        if angle_to_ball <= beam_width:
            inBeam = "(IN BEAM)"
        else:
            inBeam = "(OUTSIDE BEAM)"
        print("|", robot_matrix[4],"| Ball Angle : ", angle_to_ball, " ", inBeam)
        print("|", robot_matrix[5],"| Ball Zone  : ", ball_zone)
        print("--------------------------------------------------")

    def pretty_helper(self, angle_to_ball, dist_to_ball):
        matrix[0] = "    [][][][][]  "
        matrix[1] = "    [][][][][]  "
        matrix[2] = " R->[][][][][]  "
        matrix[3] = "    [][][][][]  "
        matrix[4] = "    [][][][][]  "
        matrix[5] = "    <--10cm-->  "
        if angle_to_ball < 10 or angle_to_ball > 350:
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
        elif angle_to_ball < 30 and angle_to_ball >= 10:
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
        elif angle_to_ball < 50 and angle_to_ball >=30:
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
        elif angle_to_ball > 330 and angle_to_ball <= 350:
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
        elif angle_to_ball > 310 and angle_to_ball <= 330:
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
        return matrix


