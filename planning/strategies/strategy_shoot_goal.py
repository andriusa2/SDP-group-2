__author__ = 'Sam Davies'
from planning.strategies.strategy import Strategy
from planning.strategies.state_machine import StateMachine


class ShootForGoal(Strategy):

    def __init__(self, world, robot_tag, actual_robot, config=None):
        super(ShootForGoal, self).__init__(world, robot_tag, actual_robot, config)
        self.m = StateMachine()
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Grabber is Closed", self.grabber_open_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Close Grabber", self.other.close_grabber)
        self.m.add_final_state_and_action("Shoot", self.other.shoot)
        self.m.add_final_state_and_action("Turn to Goal", self.turn.turn_to_enemy_goal)

        # set start state
        self.m.set_start("Start")

    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)

    def start_trans(self):
        if self.world.is_grabber_closed:
            new_state = "Grabber is Closed"
        else:
            new_state = "Close Grabber"
        return new_state

    def grabber_open_trans(self):
        if self.is_facing_enemy_goal():
            new_state = "Shoot"
        else:
            new_state = "Turn to Goal"
        return new_state
