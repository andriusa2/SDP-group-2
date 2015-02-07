_author__ = 'Sam Davies'
import unittest
from lib.world.world_state import Robot, Ball, WorldState, Zone
from lib.strategy.attacker1 import Attacker1
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

        a_world_state = WorldState(robots=robots, ball=ball, zone_boundaries=None)
        actual_robot = None
        self.attacker1 = Attacker1(a_world_state, Zone.L_ATT, actual_robot)

    # ensure that the world state is fetched
    def test_fetch_world_state(self):
        self.attacker1.fetch_world_state()
        # check that the correct location is fetched for robot and ball
        self.assertEquals((self.attacker1.robot_loc_x, self.attacker1.robot_loc_y), (20, 20))
        self.assertEquals((self.attacker1.ball_loc_x, self.attacker1.ball_loc_y), (10, 10))

    # ensure that a close ball is found to be close

    # ensure that a non close ball is found to be not close

if __name__ == '__main__':
    unittest.main()
