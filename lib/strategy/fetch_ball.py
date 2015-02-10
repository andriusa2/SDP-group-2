__author__ = 'Sam Davies'
from lib.strategy.generalized_strategy import GeneralizedStrategy


class FetchBall(GeneralizedStrategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(FetchBall, self).__init__(world, robot_tag, actual_robot)

    def act(self):
        self.fetch_world_state()
        if not self.is_ball_close():
            print "ball is far away to robot"

            if self.is_grabber_down:  # is the cage down?
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
            if self.is_grabber_down:  # we must be holding the ball
                print "STATE SHOULD NOT BE REACHED"

            else:  # lower the cage
                print "cage is up"
                self.lower_cage()