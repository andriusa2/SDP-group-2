from generalized_strategy import GeneralizedStrategy
import numpy as np
__author__ = 'alex'


class Attacker1(GeneralizedStrategy):

    def __init__(self, world, robot_tag, actual_robot):
        self.actual_robot = actual_robot
        self.robot_tag = robot_tag
        self.world = world
        
        self.grab_threshold_x = 2  # we need to define these (based on kicker)
        self.grab_threshold_y = 2

        self.is_grabber_down = True

        # initialise state attributes
        self.robot_loc_x = 0
        self.robot_loc_y = 0
        self.ball_loc_x = 0
        self.ball_loc_y = 0

        # fetch the attributes from the world
        self.fetch_world_state()

    def act(self):
        zone_ball = self.world.get_zone(self.world.get_ball().position)
        zone_robot = self.world.get_zone(self.world.get_robot(self.robot_tag).position)

        if zone_ball == zone_robot:  # is the ball in our zone?

            if not self.is_ball_close():

                # raise the cage
                self.actual_robot.raise_cage()

                if not self.is_robot_facing_ball():  # are we facing the ball?

                    ball_pos = self.world.get_ball().position
                    to_turn = self.angle_to_point(ball_pos)
                    self.actual_robot.turn(to_turn)  # turn towards the the ball

                else:  # we're facing the ball

                    if not self.is_ball_close():  # are we close enough to the ball?
                        pass  # keep moving forward

                    else:  # we are close to the ball
                        pass  # stop and lower cage

            else:  # we have the ball

                if not self.is_robot_facing_ball():  # are we facing the goal?
                    pass  # turn towards the goal

                else:  # we are facing the goal
                    pass   # kick

        else:  # the ball is not in our zone
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
        pass  # TODO

    def angle_to_point(self, point):
        """calc the angle between:
        the line through the robots position at the angle of the robots direction
        the line through the robots position and the balls position
        """
        pass  # TODO

    def fetch_world_state(self):
        """
        grab the latest state of the world and set this objects attribute
        :return: nothing
        """
        (robot_loc_x, robot_loc_y) = self.world.get_robot(self.robot_tag).position
        (ball_loc_x, ball_loc_y) = self.world.get_ball().position

        self.robot_loc_x = robot_loc_x
        self.robot_loc_y = robot_loc_y
        self.ball_loc_x = ball_loc_x
        self.ball_loc_y = ball_loc_y

    def is_ball_close(self):
        """
        checks whether the ball is in close proximity to the robot
        :return:
        """
        self.fetch_world_state()
        # check if the balls is in close enough to the robot to be grabbed
        ball_robot_dist = (np.abs(self.robot_loc_x-self.ball_loc_x), np.abs(self.robot_loc_y-self.ball_loc_y))
        (ball_robot_dist_x, ball_robot_dist_y) = ball_robot_dist
        ball_close_x = ball_robot_dist_x < self.grab_threshold_x
        ball_close_y = ball_robot_dist_y < self.grab_threshold_y
        return ball_close_x and ball_close_y
