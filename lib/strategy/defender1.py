from generalized_strategy import GeneralizedStrategy
import numpy as np
from lib.math.vector import Vector2D
__author__ = 'Sam and alex'


class Defender1(GeneralizedStrategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(Attacker1, self).__init__(world, robot_tag, actual_robot)

