__author__ = 'Sam Davies'
from planning.strategies.strategy import Strategy


class FetchBall(Strategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(FetchBall, self).__init__(world, robot_tag, actual_robot)
        self.m.add_state("Start", self.start_trans)
        self.m.add_state("Grabber is Open", self.grabber_is_open_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Open Grabber", self.actions.raise_cage)
        self.m.add_final_state_and_action("Move to Ball", self.actions.move_robot_to_ball)
        self.m.add_final_state_and_action("Turn to Ball", self.actions.turn_robot_to_ball)

        # set start state
        self.m.set_start("Start")

    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)

    # ------------------------------------ Transitions ------------------------------------

    def start_trans(self):
        if self.world.do_refresh_kick:
            new_state = "Open Grabber"
        else:
            new_state = "Grabber is Open"
        return new_state

    def grabber_is_open_trans(self):
        if self.is_robot_facing_ball():
            new_state = "Move to Ball"
        else:
            new_state = "Turn to Ball"
        return new_state