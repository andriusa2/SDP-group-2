from generalized_strategy import generalized_strategy
import numpy as np
__author__ = 'alex'


class attacker1(generalized_strategy):

    def __init__(self):
        self.capture_threshold_x = 0 # we need to define these (based on kicker)
        self.capture_threshold_y = 0

        self.hold_threshold_x = 0
        self.hold_threshold_y = 0

    def act(self):
        zone_ball = self.current_state.getZone(self.ball)

        if zone_ball == self.current_state.Zone.L_ATT: # is the ball in our zone?

            (robot_loc_x,robot_loc_y) = self.current_state.robot.position
            (ball_loc_x, ball_loc_y) = self.current_state.ball.position
            (ball_robot_distance_x,ball_robot_distance_y) = (np.abs(robot_loc_x-ball_loc_x),np.abs(robot_loc_y-ball_loc_y))


            if (not(ball_robot_distance_x < self.hold_threshold_x and ball_robot_distance_y < self.hold_threshold_y)): # do we have the ball?

                we_are_facing_the_ball = True

                if (not(we_are_facing_the_ball)): # are we facing the ball?
                    pass # turn towards the the ball

                else: # we're not facing the ball

                    (robot_loc_x,robot_loc_y) = self.current_state.robot.position
                    (ball_loc_x, ball_loc_y) = self.current_state.ball.position
                    (ball_robot_distance_x,ball_robot_distance_y) = (np.abs(robot_loc_x-ball_loc_x),np.abs(robot_loc_y-ball_loc_y))

                    if(not(ball_robot_distance_x < self.capture_threshold_x and ball_robot_distance_y < self.capture_threshold_y)): # are we close enough to the ball?
                        pass # keep moving forward

                    else: # we are close to the bal
                        pass # stop and lower cage

            else:# we have the ball

                we_are_facing_the_ball = True

                if(not(we_are_facing_the_ball)): # are we facing the goal?
                    pass # turn towards the goal

                else:# we are facing the goal
                    pass #kick

        else: #the ball is not in our zone
            pass # hold
