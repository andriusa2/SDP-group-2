_author__ = 'Sam Davies'
import unittest
from lib.world.world_state import Robot, Ball, WorldState
from lib.strategy.attacker1 import attacker1
from numpy import pi


class TestWorldState(unittest.TestCase):

    def setUp(self):
        pass

    # ensure that a bad robot can be added
    def test_bad_robot(self):
        bad_robot = Robot(direction=pi, position=(0, 0), velocity=(0, 0), enemy=True)
        self.assertTrue(bad_robot.is_enemy())

if __name__ == '__main__':
    unittest.main()
