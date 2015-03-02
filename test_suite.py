_author__ = 'Sam Davies'
import unittest
import time
import numpy as np

from planning.world.world_state import Robot, Ball, WorldState, Zone
from planning.planner import Planner
from planning.strategies.fetch_ball import FetchBall
from planning.strategies.shoot_for_goal import ShootForGoal
from communication.dummy_robot import DummyRobot
from lib.math.vector import Vector2D
from vision.dummy_vision import DummyRobotModel, DummyBallModel



class TestWorldState(unittest.TestCase):
    def setUp(self):
        pass

    # ensure that a bad robot can be added
    def test_bad_robot(self):
        bad_robot = Robot(direction=(0, 1), position=(0, 0), velocity=(0, 0), enemy=True)
        self.assertTrue(bad_robot.is_enemy())


class BaseTest(unittest.TestCase):
    def setUp(self):
        # create a world object
        self.world_state = self.put_robot_and_ball(robot_pos=(15, 0), robot_dir=(1, 0), ball_pos=(15, 15), robot_num=1)
        # make a dummy robot which can change the world
        actual_robot = DummyRobot(self.world_state, Zone.L_ATT)
        # actual_robot = Controller("/dev/tty.usbmodem000001")
        # give the strategies the world the dummy and the zone of the dummy
        self.planner = Planner(self.world_state, Zone.L_ATT, actual_robot, True)

    def put_robot_and_ball(self, robot_pos, robot_dir, ball_pos, robot_num):
        return self.put_robots_and_ball(robot_pos, [(18.0, 8.0), (25, 25), (35, 35)], robot_dir, ball_pos, robot_num)

    def put_robots_and_ball(self, my_position, other_positions, my_direction, ball_pos, robot_num):
        robot1_pos_x, robot1_pos_y = my_position
        robot2_pos_x, robot2_pos_y = other_positions[0]
        robot3_pos_x, robot3_pos_y = other_positions[1]
        robot4_pos_x, robot4_pos_y = other_positions[2]

        robot_dir_x, robot_dir_y = my_direction
        ball_pos_x, ball_pos_y = ball_pos

        # create a robot and a ball
        me = Robot(direction=(robot_dir_x, robot_dir_y), position=(robot1_pos_x, robot1_pos_y), velocity=(0.0, 0.0),
                   enemy=False)
        robot_2 = Robot(direction=(0, 1), position=(robot2_pos_x, robot2_pos_y), velocity=(0.0, 0.0), enemy=True)
        robot_3 = Robot(direction=(0, 1), position=(robot3_pos_x, robot3_pos_y), velocity=(0, 0), enemy=True)
        robot_4 = Robot(direction=(0, 1), position=(robot4_pos_x, robot4_pos_y), velocity=(0, 0), enemy=True)
        ball = Ball(position=(ball_pos_x, ball_pos_y), velocity=(0, 0), in_possession=False)

        # set the list of robots
        if robot_num is 0:
            robots = [me, robot_2, robot_3, robot_4]
        if robot_num is 1:
            robots = [robot_2, me, robot_3, robot_4]
        if robot_num is 2:
            robots = [robot_2, robot_3, me, robot_4]
        if robot_num is 3:
            robots = [robot_2, robot_3, robot_4, me]

        # create a world object
        return WorldState(robots=robots, ball=ball, zone_boundaries=[10, 20, 30, 40], left_goal=(0, 50),
                          right_goal=(40, 50))

    def change_ball_location(self, new_ball_x, new_ball_y):
        ball = Ball(position=(new_ball_x, new_ball_y), velocity=(0, 0), in_possession=False)
        self.world_state.set_ball(ball)
        # refresh the robot's world
        self.attacker1.fetch_world_state()

    def choose_planner(self, side):
        if side == "left":
            actual_robot = DummyRobot(self.world_state, Zone.L_DEF)
            self.planner = Planner(self.world_state, Zone.L_DEF, actual_robot, False)
        else:
            actual_robot = DummyRobot(self.world_state, Zone.R_DEF)
            self.planner = Planner(self.world_state, Zone.R_DEF, actual_robot, False)


class FetchBallTest(BaseTest):
    def setUp(self):
        self.world_state = self.put_robot_and_ball(robot_pos=(15, 15), robot_dir=(0, 1), ball_pos=(5, 5), robot_num=1)
        # make a dummy robot which can change the world
        actual_robot = DummyRobot(self.world_state, Zone.L_ATT)
        # give the strategies the world the dummy and the zone of the dummy
        self.attacker1 = FetchBall(self.world_state, Zone.L_ATT, actual_robot)

    # ensure that a close ball is found to be close
    def test_close_ball(self):
        self.change_ball_location(15.0, 15.0 + self.attacker1.dist_kicker_robot)
        # check that the ball is close
        self.assertTrue(self.attacker1.is_ball_close())

    def test_vector_ball_kicker(self):
        self.change_ball_location(15.0, 15.0 + self.attacker1.dist_kicker_robot)
        vec = self.attacker1.vector_from_kicker_to_ball()
        self.assertEquals(vec.x, 0.0)
        self.assertEquals(vec.y, 0.0)

    # ensure that a non close ball is found to be not close
    def test_non_close_ball(self):
        self.change_ball_location(19, 19)
        # check that the ball is close
        self.assertFalse(self.attacker1.is_ball_close())

    # ensure that a robot will turn towards the ball
    def test_robot_turns_towards_ball(self):
        # set up the world so that the robot has to turn
        ball = Ball(position=(15, 15), velocity=(0, 0), in_possession=False)
        robot_2 = Robot(direction=(1, 0), position=(15, 0), velocity=(0, 0), enemy=False)
        self.world_state.set_ball(ball)
        self.world_state.add_robot(Zone.L_ATT, robot_2)
        # raise cage
        self.attacker1.act()
        # turn
        self.attacker1.act()
        # refresh the robot's world
        self.attacker1.fetch_world_state()
        # check that robot if facing the ball
        self.assertTrue(self.attacker1.is_robot_facing_ball())

    # ensure that the robot will move towards the ball when facing it
    def test_robot_moves_to_ball(self):
        # set up the world so that the robot does not have to turn
        ball = Ball(position=(15, 15), velocity=(0, 0), in_possession=False)
        robot_2 = Robot(direction=(0, 1), position=(15, 0), velocity=(0, 0), enemy=False)
        self.world_state.set_ball(ball)
        self.world_state.add_robot(Zone.L_ATT, robot_2)
        # raise cage
        self.attacker1.act()
        # move
        self.attacker1.act()
        # refresh the robot's world
        self.attacker1.fetch_world_state()
        # check that the robot has reached the ball
        self.assertTrue(self.attacker1.is_ball_close())


class ShootTest(BaseTest):
    def setUp(self):
        self.world_state = self.put_robot_and_ball(robot_pos=(15, 15), robot_dir=(0, 1), ball_pos=(5, 5), robot_num=1)
        # make a dummy robot which can change the world
        actual_robot = DummyRobot(self.world_state, Zone.L_ATT)
        # give the strategies the world the dummy and the zone of the dummy
        self.attacker1 = ShootForGoal(self.world_state, Zone.L_ATT, actual_robot)

    # ensure that a robot not facing goal is false

    # ensure that a robot facing goal is true

    # ensure that robot will turn towards the goal
    def test_turn_to_goal(self):
        self.change_ball_location(15.0, 15.0 + self.attacker1.dist_kicker_robot)
        # check that the ball is close
        self.assertTrue(self.attacker1.is_ball_close())
        # lower cage
        self.attacker1.act()
        # turn to goal
        self.attacker1.act()
        # refresh the robot's world
        self.attacker1.fetch_world_state()
        # check that the robot has reached the ball
        self.assertTrue(self.attacker1.is_robot_facing_goal())


class PlannerTest(BaseTest):
    # ensure that the timer stops an action from being performed
    def test_timer_prevents_action(self):
        # raise cage
        act_timer1 = self.planner.plan()
        self.assertTrue(act_timer1)
        # prevent action
        act_timer2 = self.planner.plan()
        # make sure that the planning could not act
        self.assertFalse(act_timer2)
        time.sleep(act_timer1)
        act_timer3 = self.planner.plan()
        self.assertTrue(act_timer3)

    # ensure that the world state is fetched
    def test_fetch_world_state(self):
        self.planner.fetch_world_state()
        # check that the correct location is fetched for robot and ball
        self.assertEquals(self.planner.robot.position, Vector2D(15, 0))
        self.assertEquals(self.planner.ball.position, Vector2D(15, 15))

    # ensure that real world values work
    def test_real_world_values(self):
        scale_factor = 0.4
        robot1 = Robot().convert_from_model(DummyRobotModel(22.0, 168.0, 0.04, 0.0), scale_factor)
        robot2 = Robot().convert_from_model(DummyRobotModel(172.0, 207.0, 6.21, 0.0), scale_factor)
        robot3 = Robot().convert_from_model(DummyRobotModel(336.0, 133.0, 3.33, 1.0), scale_factor)
        robot4 = Robot().convert_from_model(DummyRobotModel(436.0, 238.0, 4.3, 0.0), scale_factor)
        robots = [robot1, robot2, robot3, robot4]

        ball = Ball().convert_from_model(DummyBallModel(180.0, 236.0, 3.14, 1.0), scale_factor)
        boundries = [47, 106, 165, 212]

        self.world_state.set_zone_boundaries(boundries)
        self.world_state.set_robots(robots)
        self.world_state.set_ball(ball)
        self.assertFalse(self.planner.is_robot_facing_ball())

        # raise cage
        timer = self.planner.plan()
        self.assertFalse(self.planner.can_act())


class BlockTest(BaseTest):

    # ensure that a robot turns
    def test_turn_to_face_up(self):
        self.world_state = self.put_robot_and_ball(robot_pos=(5, 50), robot_dir=(1, 0), ball_pos=(15, 60), robot_num=0)
        self.set_up_y_intercept_of_ball_goal("left")

        self.planner.plan()
        direction = self.planner.robot.direction
        self.assertAlmostEqual(direction.x, 0)
        self.assertAlmostEqual(direction.y, 1)

    def test_y_intercept_of_ball_goal(self):
        self.world_state = self.put_robot_and_ball(robot_pos=(5, 50), robot_dir=(0, 1), ball_pos=(10, 60), robot_num=0)
        pos = self.set_up_y_intercept_of_ball_goal("left")
        self.assertEquals(pos, (5, 55))

        self.world_state = self.put_robot_and_ball(robot_pos=(5, 50), robot_dir=(0, 1), ball_pos=(10, 40), robot_num=0)
        pos = self.set_up_y_intercept_of_ball_goal("left")
        self.assertEquals(pos, (5, 45))

        self.world_state = self.put_robot_and_ball(robot_pos=(35, 50), robot_dir=(0, 1), ball_pos=(30, 60), robot_num=3)
        pos = self.set_up_y_intercept_of_ball_goal("right")
        self.assertEquals(pos, (35, 55))

        self.world_state = self.put_robot_and_ball(robot_pos=(35, 50), robot_dir=(0, 1), ball_pos=(30, 40), robot_num=3)
        pos = self.set_up_y_intercept_of_ball_goal("right")
        self.assertEquals(pos, (35, 45))

    def test_intercept_ball(self):
        self.world_state = self.put_robot_and_ball(robot_pos=(10, 50), robot_dir=(0, 1), ball_pos=(20, 60), robot_num=0)
        self.choose_planner("left")
        self.planner.plan()
        self.assertEquals(self.planner.robot.position.x, 10)
        self.assertEquals(self.planner.robot.position.y, 55)

        self.world_state = self.put_robot_and_ball(robot_pos=(10, 50), robot_dir=(0, 1), ball_pos=(20, 40), robot_num=0)
        self.choose_planner("left")
        self.planner.fetch_world_state()
        self.planner.plan()
        self.assertEquals(self.planner.robot.position.x, 10)
        self.assertEquals(self.planner.robot.position.y, 45)

        self.world_state = self.put_robots_and_ball((35, 50), [(5.0, 50), (15, 50), (25, 0)], my_direction=(0, 1), ball_pos=(30, 60), robot_num=3)
        self.choose_planner("right")
        self.planner.fetch_world_state()
        self.planner.plan()
        self.assertEquals(self.planner.robot.position.x, 35)
        self.assertEquals(self.planner.robot.position.y, 55)

        self.world_state = self.put_robots_and_ball((35, 50), [(5.0, 50), (15, 50), (25, 0)], my_direction=(0, 1), ball_pos=(30, 40), robot_num=3)
        self.choose_planner("right")
        self.planner.fetch_world_state()
        self.planner.plan()
        self.assertEquals(self.planner.robot.position.x, 35)
        self.assertEquals(self.planner.robot.position.y, 45)

    def set_up_y_intercept_of_ball_goal(self, side):
        self.choose_planner(side)
        self.planner.fetch_world_state()

        robot_pos = self.planner.robot.position
        goal = self.planner.goal
        ball_pos = self.planner.ball.position
        return self.planner.y_intercept_of_ball_goal(robot_pos, goal, ball_pos)


class PassToZoneTest(BaseTest):

    # ensure that a blocked pass is found to be blocked
    def test_next_location_top(self):
        self.world_state = self.put_robots_and_ball((5, 50), [(15.0, 50), (25, 50), (35, 0)], my_direction=(0, 1),
                                                    ball_pos=(20, 60), robot_num=0)
        self.choose_planner("left")
        next_location = self.planner.pass_ball.determine_next_location()
        self.assertEqual(next_location.x, 5)
        self.assertEqual(next_location.y, self.planner.pass_ball.preset_pass_locations[0].y)

    # ensure that a blocked pass is found to be blocked
    def test_next_location_bottom(self):
        self.world_state = self.put_robots_and_ball((5, 100), [(15.0, 50), (25, 50), (35, 0)], my_direction=(0, 1),
                                                    ball_pos=(20, 60), robot_num=0)
        self.choose_planner("left")
        next_location = self.planner.pass_ball.determine_next_location()
        self.assertEqual(next_location.x, 5)
        self.assertEqual(next_location.y, self.planner.pass_ball.preset_pass_locations[1].y)

    # ensure that a friend robot is found correctly
    def test_get_friend_left(self):
        self.world_state = self.put_robots_and_ball((5, 50), [(15.0, 50), (25, 50), (35, 0)], my_direction=(0, 1), ball_pos=(20, 60), robot_num=0)
        self.choose_planner("left")
        friend = self.planner.pass_ball.get_friend()
        self.assertEqual(self.planner.world.get_zone(friend.position), Zone.R_ATT)

    def test_get_friend_right(self):
        self.world_state = self.put_robots_and_ball((34, 50), [(5.0, 50), (15, 50), (25, 0)], my_direction=(0, 1), ball_pos=(20, 60), robot_num=3)
        self.choose_planner("right")
        friend = self.planner.pass_ball.get_friend()
        self.assertEqual(self.planner.world.get_zone(friend.position), Zone.L_ATT)

    # ensure that the blocking robot is found correctly
    def test_get_enemy(self):
        self.world_state = self.put_robot_and_ball(robot_pos=(5, 50), robot_dir=(0, 1), ball_pos=(20, 60), robot_num=0)
        self.choose_planner("left")
        friend = self.planner.pass_ball.get_enemy()
        self.assertEqual(self.planner.world.get_zone(friend.position), Zone.L_ATT)

    # ensure that a blocked pass is found to be blocked
    def test_blocked_pass(self):
        self.world_state = self.put_robots_and_ball((5, 50), [(15.0, 50), (25, 50), (35, 0)], my_direction=(0, 1),
                                                    ball_pos=(20, 60), robot_num=0)
        self.choose_planner("left")
        is_blocked = self.planner.pass_ball.is_pass_blocked()
        self.assertTrue(is_blocked)

    # ensure that unblocked pass is found to be open
    def test_unblocked_pass(self):
        self.world_state = self.put_robots_and_ball((10, 50), [(8.0, 8.0), (25, 25), (35, 35)], my_direction=(0, 1),
                                                    ball_pos=(20, 60), robot_num=0)
        self.choose_planner("left")
        is_blocked = self.planner.pass_ball.is_pass_blocked()
        self.assertFalse(is_blocked)

    # ensure that a blocked pass results in a position change
    def test_blocked_pass_action(self):
        self.world_state = self.put_robots_and_ball((5, 50), [(15.0, 50), (25, 50), (35, 0)], my_direction=(1, 0),
                                                    ball_pos=(6, 50), robot_num=0)
        self.choose_planner("left")
        is_blocked = self.planner.pass_ball.is_pass_blocked()
        self.assertTrue(is_blocked)

        timer = self.planner.plan()
        time.sleep(timer)

        timer = self.planner.plan()
        time.sleep(timer)

    # ensure that an unblocked results in a pass
    def test_unblocked_pass_action(self):
        pass


class PrettyPrintTest(BaseTest):
    state_trace = ["a", "b", "c", "d", "e"]
    def test_simple_print(self):
        printed = self.planner.pretty_print(1, 3.8, np.pi/4, "GRABBER IS OPEN", "TURN TO BALL", 0.5, True, True, 1, ["a", "b", "c", "d", "e"])

        self.assertEquals("Robot - Attacker - Zone 1", printed[0])
        self.assertEquals("--------------------------------------------------", printed[1])
        self.assertEquals("|    [][][][][]  | State      : GRABBER IS OPEN", printed[2])
        self.assertEquals("|    []::[][][]  | Action     : TURN TO BALL", printed[3])
        self.assertEquals("| R->[][][][][]  | Duration   : 0.5 seconds", printed[4])
        self.assertEquals("|    [][][][][]  |--------------------------------", printed[5])
        self.assertEquals("|    [][][][][]  |", printed[6])
        self.assertEquals("|    <--10cm-->  |", printed[7])
        self.assertEquals("--------------------------------------------------", printed[8])
        self.assertEquals("| Ball is 3.8cm away", printed[9])
        self.assertEquals("| Ball is close to robot", printed[10])
        self.assertEquals("| Ball at angle : 45 deg (IN BEAM)", printed[11])
        self.assertEquals("| Ball Zone : 1", printed[12])
        self.assertEquals("--------------------------------------------------", printed[13])

    def test_simple_print_negative(self):
        printed = self.planner.pretty_print(1, 3.8, np.pi/-4, "GRABBER IS OPEN", "TURN TO BALL", 0.5, True, True, 1, ["a", "b", "c", "d", "e"])

        self.assertEquals("Robot - Attacker - Zone 1", printed[0])
        self.assertEquals("--------------------------------------------------", printed[1])
        self.assertEquals("|    [][][][][]  | State      : GRABBER IS OPEN", printed[2])
        self.assertEquals("|    [][][][][]  | Action     : TURN TO BALL", printed[3])
        self.assertEquals("| R->[][][][][]  | Duration   : 0.5 seconds", printed[4])
        self.assertEquals("|    []::[][][]  |--------------------------------", printed[5])
        self.assertEquals("|    [][][][][]  |", printed[6])
        self.assertEquals("|    <--10cm-->  |", printed[7])
        self.assertEquals("--------------------------------------------------", printed[8])
        self.assertEquals("| Ball is 3.8cm away", printed[9])
        self.assertEquals("| Ball is close to robot", printed[10])
        self.assertEquals("| Ball at angle : -45 deg (IN BEAM)", printed[11])
        self.assertEquals("| Ball Zone : 1", printed[12])
        self.assertEquals("--------------------------------------------------", printed[13])

    def test_simple_print_behind(self):
        printed = self.planner.pretty_print(1, 3.8, np.pi, "GRABBER IS OPEN", "TURN TO BALL", 0.5, True, True, 1, ["a", "b", "c", "d", "e"])

        self.assertEquals("Robot - Attacker - Zone 1", printed[0])
        self.assertEquals("--------------------------------------------------", printed[1])
        self.assertEquals("|    [][][][][]  | State      : GRABBER IS OPEN", printed[2])
        self.assertEquals("|    [][][][][]  | Action     : TURN TO BALL", printed[3])
        self.assertEquals("| R->[][][][][]  | Duration   : 0.5 seconds", printed[4])
        self.assertEquals("|    [][][][][]  |--------------------------------", printed[5])
        self.assertEquals("|    [][][][][]  |", printed[6])
        self.assertEquals("|    <--10cm-->  |", printed[7])
        self.assertEquals("--------------------------------------------------", printed[8])
        self.assertEquals("| Ball is 3.8cm away", printed[9])
        self.assertEquals("| Ball is close to robot", printed[10])
        self.assertEquals("| Ball at angle : 180 deg (IN BEAM)", printed[11])
        self.assertEquals("| Ball Zone : 1", printed[12])
        self.assertEquals("--------------------------------------------------", printed[13])

    def test_simple_print_distance(self):
        printed = self.planner.pretty_print(1, 10.1, np.pi/4, "GRABBER IS OPEN", "TURN TO BALL", 0.5, True, True, 1, ["a", "b", "c", "d", "e"])

        self.assertEquals("Robot - Attacker - Zone 1", printed[0])
        self.assertEquals("--------------------------------------------------", printed[1])
        self.assertEquals("|    [][][][][]  | State      : GRABBER IS OPEN", printed[2])
        self.assertEquals("|    [][][][][]  | Action     : TURN TO BALL", printed[3])
        self.assertEquals("| R->[][][][][]  | Duration   : 0.5 seconds", printed[4])
        self.assertEquals("|    [][][][][]  |--------------------------------", printed[5])
        self.assertEquals("|    [][][][][]  |", printed[6])
        self.assertEquals("|    <--10cm-->  |", printed[7])
        self.assertEquals("--------------------------------------------------", printed[8])
        self.assertEquals("| Ball is 10.1cm away", printed[9])
        self.assertEquals("| Ball is close to robot", printed[10])
        self.assertEquals("| Ball at angle : 45 deg (IN BEAM)", printed[11])
        self.assertEquals("| Ball Zone : 1", printed[12])
        self.assertEquals("--------------------------------------------------", printed[13])

   
    def test_simple_print_corner_top(self):
        printed = self.planner.pretty_print(1, np.sqrt(440)/2, 0.442374223, "GRABBER IS OPEN", "TURN TO BALL", 0.5, True, True, 1, ["a", "b", "c", "d", "e"])
        self.assertEquals("Robot - Attacker - Zone 1", printed[0])
        self.assertEquals("--------------------------------------------------", printed[1])
        self.assertEquals("|    [][][][]::  | State      : GRABBER IS OPEN", printed[2])
        self.assertEquals("|    [][][][][]  | Action     : TURN TO BALL", printed[3])
        self.assertEquals("| R->[][][][][]  | Duration   : 0.5 seconds", printed[4])
        self.assertEquals("|    [][][][][]  |--------------------------------", printed[5])
        self.assertEquals("|    [][][][][]  |", printed[6])
        self.assertEquals("|    <--10cm-->  |", printed[7])
        self.assertEquals("--------------------------------------------------", printed[8])
        self.assertEquals("| Ball is 3.8cm away", printed[9])
        self.assertEquals("| Ball is close to robot", printed[10])
        self.assertEquals("| Ball at angle : 25 deg (IN BEAM)", printed[11])
        self.assertEquals("| Ball Zone : 1", printed[12])
        self.assertEquals("--------------------------------------------------", printed[13])

    def test_simple_print_corner_top(self):
        printed = self.planner.pretty_print(1, np.sqrt(440)/2, -0.442374223, "GRABBER IS OPEN", "TURN TO BALL", 0.5, True, True, 1, ["a", "b", "c", "d", "e"])
        self.assertEquals("Robot - Attacker - Zone 1", printed[0])
        self.assertEquals("--------------------------------------------------", printed[1])
        self.assertEquals("|    [][][][][]  | State      : GRABBER IS OPEN", printed[2])
        self.assertEquals("|    [][][][][]  | Action     : TURN TO BALL", printed[3])
        self.assertEquals("| R->[][][][][]  | Duration   : 0.5 seconds", printed[4])
        self.assertEquals("|    [][][][][]  |--------------------------------", printed[5])
        self.assertEquals("|    [][][][]::  |", printed[6])
        self.assertEquals("|    <--10cm-->  |", printed[7])
        self.assertEquals("--------------------------------------------------", printed[8])
        self.assertEquals("| Ball is 10.4880884817cm away", printed[9])
        self.assertEquals("| Ball is close to robot", printed[10])
        self.assertEquals("| Ball at angle : -25 deg (IN BEAM)", printed[11])
        self.assertEquals("| Ball Zone : 1", printed[12])
        self.assertEquals("--------------------------------------------------", printed[13])


if __name__ == '__main__':
    unittest.main()
