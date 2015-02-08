_author__ = 'Sam Davies'
import unittest
from lib.world.world_state import Robot, Ball, WorldState, Zone
from lib.strategy.attacker1 import Attacker1
from communication.dummy_robot import DummyRobot
from numpy import pi


class TestWorldState(unittest.TestCase):

    def setUp(self):
        pass

    # ensure that a bad robot can be added
    def test_bad_robot(self):
        bad_robot = Robot(direction=pi, position=(0, 0), velocity=(0, 0), enemy=True)
        self.assertTrue(bad_robot.is_enemy())


class TestAttacker1(unittest.TestCase):

    def setUp(self):
        # create a robot and a ball
        robot_1 = Robot(direction=pi, position=(8, 8), velocity=(0, 0), enemy=True)
        robot_2 = Robot(direction=pi, position=(20, 20), velocity=(0, 0), enemy=True)
        robot_3 = Robot(direction=pi, position=(30, 30), velocity=(0, 0), enemy=True)
        robot_4 = Robot(direction=pi, position=(40, 40), velocity=(0, 0), enemy=True)
        ball = Ball(position=(10, 10), velocity=(0, 0), in_possession=False)

        # set the list of robots
        robots = [robot_1, robot_2, robot_3, robot_4]

        # create a world object
        self.world_state = WorldState(robots=robots, ball=ball, zone_boundaries=None)
        # make a dummy robot which can change the world
        actual_robot = DummyRobot(self.world_state)
        # give the strategy the world the dummy and the zone of the dummy
        self.attacker1 = Attacker1(self.world_state, Zone.L_ATT, actual_robot)

    # ensure that the world state is fetched
    def test_fetch_world_state(self):
        self.attacker1.fetch_world_state()
        # check that the correct location is fetched for robot and ball
        self.assertEquals((self.attacker1.robot_loc_x, self.attacker1.robot_loc_y), (20, 20))
        self.assertEquals((self.attacker1.ball_loc_x, self.attacker1.ball_loc_y), (10, 10))

    # ensure that a close ball is found to be close
    def test_close_ball(self):
        self.change_ball_location(21, 21)
        # check that the ball is close
        self.assertTrue(self.attacker1.is_ball_close())

    def change_ball_location(self, new_ball_x, new_ball_y):
        ball = Ball(position=(new_ball_x, new_ball_y), velocity=(0, 0), in_possession=False)
        self.world_state.set_ball(ball)
        # refresh the robot's world
        self.attacker1.fetch_world_state()

    # ensure that a non close ball is found to be not close
    def test_non_close_ball(self):
        self.change_ball_location(23, 23)
        # check that the ball is close
        self.assertFalse(self.attacker1.is_ball_close())

    # ensure that a robot will turn towards the ball
    def test_robot_turns_towards_ball(self):
        # set up the world so that the robot has to turn
        ball = Ball(position=(10.0, 10.0), velocity=(0, 0), in_possession=False)
        robot_2 = Robot(direction=pi, position=(20, 20), velocity=(0, 0), enemy=True)
        self.world_state.set_ball(ball)
        self.world_state.add_robot(Zone.L_ATT, robot_2)
        #
        self.attacker1.act()
        # check that robot if facing the ball
        self.assertTrue(self.attacker1.is_robot_facing_ball())

    # ensure that a robot won't turn if ball already in line

    # ensure the the robot will lower cage on a close ball


if __name__ == '__main__':
    unittest.main()
