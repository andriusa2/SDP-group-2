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
<<<<<<< HEAD


    def __init__(self, world, robot_tag, actual_robot):
        super(SaveRobot, self).__init__(world, robot_tag, actual_robot)
        # this is the point we try to recover to
        self.home = (self.get_centre_point())

=======
    def __init__(self, world, robot_tag, actual_robot, config=None):
        super(SaveRobot, self).__init__(world, robot_tag, actual_robot, config)
>>>>>>> 90f32efeff048183486121ab42b62764d4f592c0
        self.m.add_state("Start", self.start_trans)

        # End States / Actions
        self.m.add_final_state_and_action("Move Robot", self.actions.move_robot_to_point(self.home))
        self.m.add_final_state_and_action("Turn Robot", self.actions.turn_robot_to_point(self.home))

        # set start state
        self.m.set_start("Start")


    def act(self):
        self.fetch_world_state()

        action_state = self.m.run()
        return self.m.do_action(action_state)


    def start_trans(self):
        if self.is_robot_safe():  # if we're in the way, move to get out
            if self.is_robot_facing_point(self.get_zone_center_point()): # if facing home location.
                new_state = "Move Robot"
            else:
                new_state = "Turn Robot"
        else: # if we're not in the buffer zone, we don't need to do anything
            raise "Accesing save_robot when robot is safe"
        return new_state


    def move_out_of_danger(self):
        to_move = self.distance_from_robot_to_point(v.x, v.y) * 0.4  # only move 90%
        return self.actual_robot.move(to_move), "moving {0} cm to ({1}, {2})".format(to_move, v.x, v.y)
