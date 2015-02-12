_author__ = 'Sam Davies'
import unittest
import time

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

    def change_ball_location(self, new_ball_x, new_ball_y):
        ball = Ball(position=(new_ball_x, new_ball_y), velocity=(0, 0), in_possession=False)
        self.world_state.set_ball(ball)
        # refresh the robot's world
        self.attacker1.fetch_world_state()


class FetchBallTest(BaseTest):

    def setUp(self):
        # create a robot and a ball
        robot_1 = Robot(direction=(0, 1), position=(8.0, 8.0), velocity=(0.0, 0.0), enemy=True)
        robot_2 = Robot(direction=(0, 1), position=(15.0, 15.0), velocity=(0.0, 0.0), enemy=True)
        robot_3 = Robot(direction=(0, 1), position=(25, 25), velocity=(0, 0), enemy=True)
        robot_4 = Robot(direction=(0, 1), position=(35, 35), velocity=(0, 0), enemy=True)
        ball = Ball(position=(5, 5), velocity=(0, 0), in_possession=False)

        # set the list of robots
        robots = [robot_1, robot_2, robot_3, robot_4]

        # create a world object
        self.world_state = WorldState(robots=robots, ball=ball, zone_boundaries=[10, 20, 30, 40])
        # make a dummy robot which can change the world
        actual_robot = DummyRobot(self.world_state, Zone.L_ATT)
        # give the strategies the world the dummy and the zone of the dummy
        self.attacker1 = FetchBall(self.world_state, Zone.L_ATT, actual_robot)

    # ensure that a close ball is found to be close
    def test_close_ball(self):
        self.change_ball_location(15.0, 15.0+self.attacker1.dist_kicker_robot)
        # check that the ball is close
        self.assertTrue(self.attacker1.is_ball_close())

    def test_vector_ball_kicker(self):
        self.change_ball_location(15.0, 15.0+self.attacker1.dist_kicker_robot)
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

    # ensure the the robot will lower cage on a close ball
    # def test_will_lower_cage(self):
    #     # set up the world so that the robot does not have to turn or move
    #     self.change_ball_location(15.0, 15.0+self.attacker1.dist_kicker_robot)
    #     # check that the ball is close
    #     self.assertTrue(self.attacker1.is_ball_close())
    #     # do the next action
    #     self.attacker1.act()
    #     # refresh the robot's world
    #     self.attacker1.fetch_world_state()
    #     # check that the robot has reached the ball
    #     self.assertTrue(self.attacker1.is_grabber_down)


class ShootTest(BaseTest):

    def setUp(self):
        # create a robot and a ball
        robot_1 = Robot(direction=(0, 1), position=(8.0, 8.0), velocity=(0.0, 0.0), enemy=True)
        robot_2 = Robot(direction=(0, 1), position=(15.0, 15.0), velocity=(0.0, 0.0), enemy=True)
        robot_3 = Robot(direction=(0, 1), position=(25, 25), velocity=(0, 0), enemy=True)
        robot_4 = Robot(direction=(0, 1), position=(35, 35), velocity=(0, 0), enemy=True)
        ball = Ball(position=(5, 5), velocity=(0, 0), in_possession=False)

        # set the list of robots
        robots = [robot_1, robot_2, robot_3, robot_4]

        # create a world object
        self.world_state = WorldState(robots=robots, ball=ball, zone_boundaries=[10, 20, 30, 40])
        # make a dummy robot which can change the world
        actual_robot = DummyRobot(self.world_state, Zone.L_ATT)
        # give the strategies the world the dummy and the zone of the dummy
        self.attacker1 = ShootForGoal(self.world_state, Zone.L_ATT, actual_robot)

    # ensure that a robot not facing goal is false

    # ensure that a robot facing goal is true

    # ensure that robot will turn towards the goal
    def test_turn_to_goal(self):
        self.change_ball_location(15.0, 15.0+self.attacker1.dist_kicker_robot)
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

    def setUp(self):
        # create a robot and a ball
        robot_1 = Robot(direction=(0, 1), position=(8.0, 8.0), velocity=(0.0, 0.0), enemy=True)
        robot_2 = Robot(direction=(1, 0), position=(15.0, 0), velocity=(0.0, 0.0), enemy=False)
        robot_3 = Robot(direction=(0, 1), position=(25, 25), velocity=(0, 0), enemy=True)
        robot_4 = Robot(direction=(0, 1), position=(35, 35), velocity=(0, 0), enemy=True)
        ball = Ball(position=(15, 15), velocity=(0, 0), in_possession=False)

        # set the list of robots
        robots = [robot_1, robot_2, robot_3, robot_4]

        # create a world object
        self.world_state = WorldState(robots=robots, ball=ball, zone_boundaries=[10, 20, 30, 40])
        # make a dummy robot which can change the world
        actual_robot = DummyRobot(self.world_state, Zone.L_ATT)
        # actual_robot = Controller("/dev/tty.usbmodem000001")
        # give the strategies the world the dummy and the zone of the dummy
        self.planner = Planner(self.world_state, Zone.L_ATT, actual_robot, True)

    # ensure that the timer stops an action from being performed
    def test_timer_prevents_action(self):
        # raise cage
        act_timer1 = self.planner.plan_attack()
        self.assertTrue(act_timer1)
        # prevent action
        act_timer2 = self.planner.plan_attack()
        # make sure that the planning could not act
        self.assertFalse(act_timer2)
        time.sleep(act_timer1)
        act_timer3 = self.planner.plan_attack()
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

        # raise cage
        self.planner.plan_attack()
        # turn
        self.planner.plan_attack()
        self.assertTrue(self.planner.is_robot_facing_ball())


class BlockTest(BaseTest):

    def test_block_goal(self):
        # create a robot and a ball
        robot_1 = Robot(direction=(0, 1), position=(8.0, 8.0), velocity=(0.0, 0.0), enemy=True)
        robot_2 = Robot(direction=(1, 0), position=(15.0, 0), velocity=(0.0, 0.0), enemy=False)
        robot_3 = Robot(direction=(0, 1), position=(25, 25), velocity=(0, 0), enemy=True)
        robot_4 = Robot(direction=(0, 1), position=(35, 35), velocity=(0, 0), enemy=True)
        ball = Ball(position=(5, 5), velocity=(5, 0), in_possession=False)

        # set the list of robots
        robots = [robot_1, robot_2, robot_3, robot_4]

        # create a world object
        self.world_state = WorldState(robots=robots, ball=ball, zone_boundaries=[10, 20, 30, 40])
        # make a dummy robot which can change the world
        actual_robot = DummyRobot(self.world_state, Zone.L_DEF)
        # actual_robot = Controller("/dev/tty.usbmodem000001")
        # give the strategies the world the dummy and the zone of the dummy
        self.planner = Planner(self.world_state, Zone.L_DEF, actual_robot, False)

        self.assertTrue(self.planner.ball_going_quickly())

        self.planner.plan_defence()
        self.assertTrue(self.planner.is_robot_facing_up())

        self.planner.plan_defence()
        self.assertEquals(self.planner.robot.position, Vector2D(8, 5))

    def test_block_goal(self):
        # create a robot and a ball
        robot_1 = Robot(direction=(0, 1), position=(5.0, 5.0), velocity=(0.0, 0.0), enemy=True)
        robot_2 = Robot(direction=(1, 0), position=(15.0, 0), velocity=(0.0, 0.0), enemy=False)
        robot_3 = Robot(direction=(0, 1), position=(25, 25), velocity=(0, 0), enemy=True)
        robot_4 = Robot(direction=(0, 1), position=(35, 35), velocity=(0, 0), enemy=True)
        ball = Ball(position=(8, 8), velocity=(5, 0), in_possession=False)

        # set the list of robots
        robots = [robot_1, robot_2, robot_3, robot_4]

        # create a world object
        self.world_state = WorldState(robots=robots, ball=ball, zone_boundaries=[10, 20, 30, 40])
        # make a dummy robot which can change the world
        actual_robot = DummyRobot(self.world_state, Zone.L_DEF)
        # actual_robot = Controller("/dev/tty.usbmodem000001")
        # give the strategies the world the dummy and the zone of the dummy
        self.planner = Planner(self.world_state, Zone.L_DEF, actual_robot, False)

        self.assertTrue(self.planner.ball_going_quickly())

        self.planner.plan_defence()
        self.assertTrue(self.planner.is_robot_facing_up())

        self.planner.plan_defence()
        self.assertEquals(self.planner.robot.position, Vector2D(5, 8))







    # ensure that the attacker fetches the ball when in own zone

    # ensure that the attacker shoots when it has the ball

    # ensure that the planning moves to centre when ball is away




if __name__ == '__main__':
    unittest.main()
