from generalized_strategy import GeneralizedStrategy
import numpy as np
from lib.math.vector import Vector2D
__author__ = 'alex'


class Attacker1(GeneralizedStrategy):

    def __init__(self, world, robot_tag, actual_robot):
        self.actual_robot = actual_robot
        self.robot_tag = robot_tag
        self.world = world
        
        self.grab_threshold_x = 2  # we need to define these (based on kicker)
        self.grab_threshold_y = 2
        self.dist_kicker_robot = 2

        self.is_grabber_down = True

        # initialise state attributes
        self.robot = None
        self.ball = None

        # fetch the attributes from the world
        self.fetch_world_state()

    def act(self):
        self.fetch_world_state()
        zone_ball = self.world.get_zone(self.ball.position)
        zone_robot = self.world.get_zone(self.robot.position)

        if zone_ball == zone_robot:  # is the ball in our zone?
            print "ball in robot's zone"
            if not self.is_ball_close():

                # raise the cage
                self.actual_robot.raise_cage()

                if not self.is_robot_facing_ball():  # are we facing the ball?

                    to_turn = self.robot.angle_to_point(self.ball.position)
                    print "rotating robot " + str(to_turn) + " radians"
                    self.actual_robot.turn(to_turn)  # turn towards the the ball

                else:  # we're facing the ball

                    if not self.is_ball_close():  # are we close enough to the ball?
                        dist_to_ball = self.distance_from_kicker_to_ball()
                        self.actual_robot.go(dist_to_ball)

                    else:  # we are close to the ball
                        self.actual_robot.lower_cage  # lower the cage

            else:  # the ball can be held

                if self.is_grabber_down:  # we must be holding the ball

                    if not self.is_robot_facing_ball():  # are we facing the goal?
                        pass  # turn towards the goal

                    else:  # we are facing the goal
                        pass   # kick

                else:  # lower the cage
                    self.actual_robot.lower_cage

        else:  # the ball is not in our zone
            print "ball not in robot's zone"
            pass  # hold

    def is_robot_facing_goal(self):
        """
        Check if the angle between the robot and
        the centre of the goal is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        pass  # TODO

    def is_robot_facing_ball(self):
        """
        Check if the angle between the robot and
        the ball is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        robot = self.world.get_robot(self.robot_tag)
        ball_pos = self.world.get_ball().position
        return robot.can_see(point=ball_pos, threshold=0.05)

    def fetch_world_state(self):
        """
        grab the latest state of the world and set this objects attribute
        :return: nothing
        """
        self.robot = self.world.get_robot(self.robot_tag)
        self.ball = self.world.get_ball()

    def is_ball_close(self):
        """
        checks whether the ball is in close proximity to the robot's kicker
        :return:
        """
        self.fetch_world_state()

        # use the direction and position of the robot to find the position of the kicker
        direction_unit_vector = self.robot.direction.unit_vector()
        kicker_vector = direction_unit_vector.scale(self.dist_kicker_robot)
        kicker_pos = self.robot.position + kicker_vector

        # check if the balls is in close enough to the robot to be grabbed
        ball_kicker_dist_x = np.abs(kicker_pos.x-self.ball.position.x)
        ball_kicker_dist_y = np.abs(kicker_pos.y-self.ball.position.y)
        ball_close_x = ball_kicker_dist_x < self.grab_threshold_x
        ball_close_y = ball_kicker_dist_y < self.grab_threshold_y
        return ball_close_x and ball_close_y

    def distance_from_kicker_to_ball(self):
        """
        This assumes that the robot is facing the ball.
        :return: distance from the kicker to the ball
        """

        vectors = [[self.robot.position.x, self.robot.position.y], [self.ball.position.x,  self.ball.position.y]]
        dist_robot_ball = np.linalg.norm(vectors)
        dist_kicker_ball = dist_robot_ball - self.dist_kicker_robot
        return dist_kicker_ball
