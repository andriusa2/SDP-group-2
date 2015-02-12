__author__ = 'Sam Davies'
from planning.strategies.strategy import Strategy
from planning.strategies.state_machine import StateMachine


class ShootForGoal(Strategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(ShootForGoal, self).__init__(world, robot_tag, actual_robot)
        self.m = StateMachine()
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Grabber is Closed", self.grabber_open_trans)

        # End States / Actions
        self.m.add_action("Close Grabber", self.lower_cage)
        self.m.add_action("Shoot", self.shoot)
        self.m.add_action("Turn to Goal", self.turn_robot_to_goal)

        # set start state
        self.m.set_start("Start")

    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)

    def start_trans(self):
        if self.world.is_grabber_down:
            new_state = "Grabber is Closed"
        else:
            new_state = "Close Grabber"
        return new_state

    def grabber_open_trans(self):
        if self.is_robot_facing_goal():
            new_state = "Shoot"
        else:
            new_state = "Turn to Goal"
        return new_state
