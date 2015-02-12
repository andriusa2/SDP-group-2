__author__ = 'Sam Davies'
from planner.strategies.strategy import Strategy


class MoveToZoneCentre(Strategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(MoveToZoneCentre, self).__init__(world, robot_tag, actual_robot)

    def act(self):

        # is the robot at the zone centre?
        if True:
            print "robot in zone centre"
            # turn to face the ball
            if not self.is_robot_facing_ball():  # are we facing the ball?
                print "robot not facing ball"
                to_turn = self.robot.angle_to_point(self.ball.position)
                print "rotating robot " + str(to_turn) + " radians"
                return self.actual_robot.turn(to_turn)  # turn towards the the ball

            else:  # we're facing the ball
                print "robot facing ball"
        else:
            # is the robot facing the centre?
            if True:
                print "moving robot to centre"
                dist_to_ball = self.distance_from_kicker_to_ball()
                return self.actual_robot.move(dist_to_ball)
            else:
                zone_centre = self.get_zone_centre()
                to_turn = self.robot.angle_to_point(zone_centre)
                print "rotating robot " + str(to_turn) + " radians"
                return self.actual_robot.turn(to_turn)  # turn towards the the ball