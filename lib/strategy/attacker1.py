from generalized_strategy import GeneralizedStrategy
__author__ = 'Sam and alex'


class Attacker1(GeneralizedStrategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(Attacker1, self).__init__(world, robot_tag, actual_robot)

    def act(self):
        self.fetch_world_state()
        zone_ball = self.world.get_zone(self.ball.position)
        zone_robot = self.world.get_zone(self.robot.position)

        if zone_ball == zone_robot:  # is the ball in our zone?
            print "ball in robot's zone"
            if not self.is_ball_close():
                print "ball is far away to robot"

                if self.world.get_robot(self.robot_tag).is_grabber_down:  # is the cage down?
                    self.raise_cage()
                else:
                    # cage not down

                    if not self.is_robot_facing_ball():  # are we facing the ball?
                        print "robot not facing ball"
                        to_turn = self.robot.angle_to_point(self.ball.position)
                        print "rotating robot " + str(to_turn) + " radians"
                        self.actual_robot.turn(to_turn)  # turn towards the the ball

                    else:  # we're facing the ball
                        print "robot facing ball"
                        dist_to_ball = self.distance_from_kicker_to_ball()
                        print dist_to_ball
                        self.actual_robot.move_forward(dist_to_ball)

            else:  # the ball can be held
                print "ball is close to robot kicker"
                if self.world.get_robot(self.robot_tag).is_grabber_down:  # we must be holding the ball
                    print "cage is down"
                    if not self.is_robot_facing_goal():  # are we facing the goal?
                        print "robot not facing goal"
                        to_turn = self.robot.angle_to_point(self.world.goal)
                        print "rotating robot " + str(to_turn) + " radians"
                        self.actual_robot.turn(to_turn)  # turn towards the the goal

                    else:  # we are facing the goal
                        print "robot is facing goal"
                        self.actual_robot.kick(power=1.0)  # kick

                else:  # lower the cage
                    print "cage is up"
                    self.lower_cage()

        else:  # the ball is not in our zone
            print "ball not in robot's zone"
            pass  # hold
