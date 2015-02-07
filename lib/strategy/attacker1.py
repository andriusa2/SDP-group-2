from generalized_strategy import GeneralizedStrategy
import numpy as np
__author__ = 'alex'


class Attacker1(GeneralizedStrategy):

    def __init__(self):
        self.capture_threshold_x = 0  # we need to define these (based on kicker)
        self.capture_threshold_y = 0

        self.hold_threshold_x = 0
        self.hold_threshold_y = 0

        # initialise state attributes
        self.robot_loc_x = 0
        self.robot_loc_y = 0
        self.ball_loc_x = 0
        self.ball_loc_y = 0
        self.fetch_world_state()

    def act(self):
        zone_ball = self.current_state.getZone(self.ball)

        if zone_ball == self.current_state.Zone.L_ATT:  # is the ball in our zone?

            if not self.is_ball_close():

                we_are_facing_the_ball = True

                if not we_are_facing_the_ball:  # are we facing the ball?
                    pass  # turn towards the the ball

                else:  # we're not facing the ball

                    if not self.is_ball_close():  # are we close enough to the ball?
                        pass  # keep moving forward

                    else:  # we are close to the bal
                        pass  # stop and lower cage

            else:  # we have the ball

                we_are_facing_the_ball = True

                if not we_are_facing_the_ball:  # are we facing the goal?
                    pass  # turn towards the goal

                else:  # we are facing the goal
                    pass   # kick

        else:  # the ball is not in our zone
            pass  # hold

    def fetch_world_state(self):
        """
        grab the latest state of the world and set this objects attribute
        :return: nothing
        """
        (robot_loc_x, robot_loc_y) = self.current_state.robot.position
        (ball_loc_x, ball_loc_y) = self.current_state.ball.position

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
        ball_close_x = ball_robot_dist_x < self.hold_threshold_x
        ball_close_y = ball_robot_dist_y < self.hold_threshold_y
        return ball_close_x and ball_close_y
