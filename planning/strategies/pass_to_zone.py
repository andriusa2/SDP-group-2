__author__ = 'Sam Davies'
from planner.strategies.strategy import Strategy


class PassToZone(Strategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(PassToZone, self).__init__(world, robot_tag, actual_robot)

    def act(self):
        pass