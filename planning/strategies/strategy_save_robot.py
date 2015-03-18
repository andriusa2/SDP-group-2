from planning.strategies.strategy import Strategy

__author__ = 'Sam Davies'


class SaveRobot(Strategy):
    def __init__(self, world, robot_tag, actual_robot):
        super(SaveRobot, self).__init__(world, robot_tag, actual_robot)
        self.m.add_state("Start", self.start_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Move Robot", self.move_out_of_danger)
        self.m.add_final_state_and_action("Turn Robot", self.turn_bla_bla)

        # set start state
        self.m.set_start("Start")

    def start_trans(self):
        if True:
            new_state = ""
        else:
            new_state = ""
        return new_state

    def move_out_of_danger(self):
        info = ""
        return 0, info

    def turn_bla_bla(self):
        info = ""
        return 0, info