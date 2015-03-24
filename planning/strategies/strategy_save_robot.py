from planning.strategies.strategy import Strategy
__author__ = 'Sam Davies'


'''

            114 cm
     -----------------
    |                 |
45  |                 |
     -----------------
    \                /
  34 \              /
        ============
            59cm

                            as y increases the width we have available increases


    |  .       x
 14 |      .--------    27/14 = m
    |           .     additional x = f(y) = (27/14) * y
     ---------------
            27

'''

class SaveRobot(Strategy):

    def __init__(self, world, robot_tag, actual_robot, config=None):
        super(SaveRobot, self).__init__(world, robot_tag, actual_robot, config)
        self.m.add_state("Start", self.start_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Move Robot", self.actions.move_to_home)
        self.m.add_final_state_and_action("Turn Robot", self.actions.turn_to_home)

        # set start state
        self.m.set_start("Start")


    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)


    def start_trans(self):
        if self.is_robot_safe():  # if we're in the way, move to get out
            if self.is_robot_facing_point(self.get_center_point()): # if facing home location.
                new_state = "Move Robot"
            else:
                new_state = "Turn Robot"
        else: # if we're not in the buffer zone, we don't need to do anything
            raise "Accesing save_robot when robot is safe"
        return new_state