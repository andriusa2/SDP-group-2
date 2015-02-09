from generalized_strategy import GeneralizedStrategy
import numpy as np
from lib.math.vector import Vector2D
__author__ = 'Sam and alex'


class Defender1(GeneralizedStrategy):

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

        if zone_ball == zone_robot:
            print "ball is in robot's zone"
            if not ball_going_quickly():
                #ball is stationary, or essentially stationary
                if not self.is_ball_close():

                    #raise the cage
                    self.actual_robot.raise_cage()

                    if not self.is_robot_facing_ball():
                        print "robot is not facing ball"
                        to_turn =self.robot_angle_to_point(self.ball.position)
                        print "rotating robot to " + str(to_turn) + " radians"
                        self.actual_robot.turn(to_turn)

                    else: # we are facing the ball
                        print "robot is facing the ball"
                        if not self.is_ball_close:
                            print "Ball is far away"
                            dist_to_ball = self.dist_from_kicker_to_ball()
                            self.actual_robot.move_forward(dist_to_ball)

                    else: #we are close to the ball
                        print "robot is close to ball"
                        self.actual_robot.lower_cage()
                else: # the robot is close to the ball
                    
                    if not self.is_robot_facing_goal():
                        







    
        # no:

        # wait

        # yes:

    # are we in the best position?

        # yes:

        # are we facing the opponent where the ball is?

            # no:

            # turn to face them

            # yes:

            # hold your position

        # no:

        # are we facing the best position?

        # yes:

        # move forward

        # no:

        # turn

    def ball_going_quickly(self):
        """
        Check is ball is going quicker than a threshold velocity
        """
        pass

