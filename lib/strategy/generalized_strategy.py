from lib.world.world_state import WorldState
__author__ = 'alex'


class generalized_strategy():

    def __init__(self):
        self.current_state = None

    def act(self):
        pass

    def update_state(self, world_state):
        if (type(world_state) != type(WorldState)):
            raise Exception
        self.current_state = world_state
