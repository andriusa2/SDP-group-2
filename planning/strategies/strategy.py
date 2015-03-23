import numpy as np

from lib.math.vector import Vector2D
from planning.strategies.actions import Actions
from planning.strategies.state_machine import StateMachine
from planning.world_state import Zone, Robot


__author__ = 'Sam'


class Strategy(object):

    def __init__(self, world, robot_tag, actual_robot):
        self.actual_robot = actual_robot
        self.robot_tag = robot_tag
        self.world = world

        self.grab_threshold_x = 8  # we need to define these (based on kicker)
        self.grab_threshold_y = 8
        self.dist_kicker_robot = 12

        self.ROBOT_WIDTH = 4
        self.zone_centre_width = 8
        self.square_angle_threshold = 0.001

        # initialise state attributes
        self.robot = None
        self.ball = None
        self.goal = None
        self.m = StateMachine()
        self.actions = Actions()

        self.ACTUAL_WIDTH = 114
        self.ACTUAL_LENGTH = 45
        self.DEADSPACE_SLOPE = 27.0/14.0
        self.DEADSPACE_BOUNDARY = 14
        self.DEADSPACE_SAFE_X = 25
        self.SAFE_X = 55
        self.SAFE_Y = 40

    def fetch_world_state(self):
        """
        grab the latest state of the world and set this objects attribute
        :return: nothing
        """
        self.robot = self.world.get_robot(self.robot_tag)
        self.ball = self.world.get_ball()
        self.goal = self.get_goal()

        # update rotation and movement
        self.actions.__int__(self)

    """
    -------------------------------------------------------
        Complex World State Checks
    -------------------------------------------------------
    """

    def is_robot_facing_goal(self):
        """
        Check if the angle between the robot and
        the centre of the goal is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        goal = self.goal
        return self.robot.can_see(point=goal, beam_width=self.ROBOT_WIDTH)

    def is_robot_facing_ball(self):
        """
        Check if the angle between the robot and
        the ball is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        ball_pos = self.ball.position
        return self.robot.can_see(point=ball_pos, beam_width=self.ROBOT_WIDTH/2)

    def is_at_square_angles(self):
        dir_x = self.robot.direction.x
        dir_y = self.robot.direction.y

        major_axis = max(abs(dir_x), abs(dir_y))
        print "Major axis is {0}, and is at square angles if > {1}".format(major_axis, 1-self.square_angle_threshold)
        return major_axis > 1-self.square_angle_threshold

    def is_robot_facing_point(self, point, beam_width=None):
        """
        Check to see if a point is in the robots beam
        :return: whether or not the robot is facing the point
        """
        if not beam_width:
            beam_width = self.ROBOT_WIDTH
        return self.robot.can_see(point=point, beam_width=beam_width)

    def is_robot_in_centre(self):
        zone_centre = self.get_zone_centre()
        centre_bound_l = zone_centre - (self.zone_centre_width/2)
        centre_bound_r = zone_centre + (self.zone_centre_width/2)
        return centre_bound_l < self.robot.position.x < centre_bound_r


    def is_robot_safe(self):
        if self.is_robot_x_safe() and self.is_robot_y_safe():
            return True
        else:
            return False


    def is_robot_y_safe(self):
        if np.abs(self.robot.position.y - self.get_zone_centre_y()) > self.SAFE_Y:
            return False
        else:
            return True


    def is_robot_x_safe(self):
        # do we need to consider deadspace?
        if self.robot.position.y < self.DEADSPACE_BOUNDARY:
            # we need to think about deadspace
            safe_width =  + (self.DEADSPACE_SLOPE) * self.robot.position.y
            '''
                    Explanation

                |  .       x
             14 |      .--------
                |          .     additional x = f(y) = (27/14) * y
                ---------------
                        27

            '''

            # how close are we to the walls, taking into account deadspace?
            if np.abs(self.robot.position.x - self.zone_centre())\
                    > self.DEADSPACE_SAFE_X + safe_width:
                return False
            else:
                return True

        # There's no deadspace; how close are we to the walls?
        elif(np.abs(self.robot.position.x - self.get_zone_centre_y()) > self.SAFE_X):
            return False

    """
    -------------------------------------------------------
        Fetching of Objects in World State
    -------------------------------------------------------
    """

    def get_zone_centre(self):
        my_zone = self.world.get_zone(self.robot.position)
        zone_edges = [0] + self.world.zone_boundaries
        edge_L = zone_edges[my_zone]
        edge_R = zone_edges[my_zone+1]
        zone_centre = edge_L + (edge_R - edge_L)/2.0
        # print "Left: {0}, right {1}, centre: {2}".format(edge_L, edge_R, zone_centre)
        return zone_centre


    def get_zone_centre_y(self):
        # returns the inferred zone center_y
        #pitch is roughly 114cm x 45; normalize the value and find others
        zone_center = self.get_zone_centre()
        zone_center_y = zone_center * (self.ACTUAL_LENGTH/self.ACTUAL_WIDTH)
        return  zone_center_y


    def get_centre_point(self):
        # returns point (int, int)  an (x,y)
        return (self.get_zone_centre(), self.get_zone_centre_y())


    def is_ball_in_friend_zone(self):
        friend_zone = self.world.get_zone(self.get_friend().position)
        ball_zone = self.world.get_zone(self.world.get_ball().position)
        return friend_zone == ball_zone

    def get_goal(self):
        zone = self.world.get_zone(self.robot.position)
        if zone == Zone.L_ATT or zone == Zone.L_DEF:
            return self.world.left_goal
        else:
            return self.world.right_goal

    def get_friend(self):
        self.fetch_world_state()
        my_zone = self.world.get_zone(self.robot.position)
        if my_zone == 0 or my_zone == 1:
            friend = self.world.get_robot(Zone.R_ATT)
        else:
            friend = self.world.get_robot(Zone.L_ATT)

        if friend:
            return friend
        else:
            return Robot()

    def get_enemy(self):
        self.fetch_world_state()
        my_zone = self.world.get_zone(self.robot.position)
        if my_zone == 0 or 1:
            enemy = self.world.get_robot(Zone.L_ATT)
        else:
            enemy = self.world.get_robot(Zone.R_ATT)
        if enemy:
            return enemy
        else:
            return Robot()

    def get_enemy_defender(self):
        self.fetch_world_state()
        my_zone = self.world.get_zone(self.robot.position)
        if my_zone == 0 or 1:
            enemy = self.world.get_robot(Zone.L_DEF)
        else:
            enemy = self.world.get_robot(Zone.R_DEF)
        if enemy:
            return enemy
        else:
            return Robot()

    def is_ball_in_robot_zone(self):
        zone_ball = self.world.get_zone(self.ball.position)
        zone_robot = self.world.get_zone(self.robot.position)
        return zone_ball == zone_robot

    def is_ball_close(self):
        """
        checks whether the ball is in close proximity to the robot's kicker
        :return:
        """
        self.fetch_world_state()

        # check if the balls is in close enough to the robot to be grabbed
        ball_kicker_vector = self.vector_from_kicker_to_ball()
        ball_close_x = abs(ball_kicker_vector.x) < self.grab_threshold_x
        ball_close_y = abs(ball_kicker_vector.y) < self.grab_threshold_y
        return ball_close_x and ball_close_y

    def distance_from_kicker_to_ball(self):
        """
        :return: distance from the kicker to the ball
        """
        return self.vector_from_kicker_to_ball().length()

    def vector_from_kicker_to_ball(self):
        """
        :return: vector from the kicker to the ball
        """
        kicker_pos = self.get_kicker_position()
        ball_kicker_dist_x = kicker_pos.x-self.ball.position.x
        ball_kicker_dist_y = kicker_pos.y-self.ball.position.y
        return Vector2D(ball_kicker_dist_x, ball_kicker_dist_y)

    def get_kicker_position(self):
        """
        fetch the kicker position based on robot pos and direction
        :return: a vector
        """
        # use the direction and position of the robot to find the position of the kicker
        direction_unit_vector = self.robot.direction.unit_vector()
        kicker_vector = direction_unit_vector.scale(self.dist_kicker_robot)
        return self.robot.position + kicker_vector

    def distance_from_robot_to_point(self, x, y):
        return self.vector_from_robot_to_point(x, y).length()

    def vector_from_robot_to_point(self, x, y):
        """
        :return: distance from robot to a given point
        """
        robot_point_dist_x = -self.robot.position.x+x
        robot_point_dist_y = -self.robot.position.y+y
        return Vector2D(robot_point_dist_x, robot_point_dist_y)

    @staticmethod
    def get_local_move(to_move, direction):
        """
        For a vector, all that you have to do is rotate it by the angle difference between
        your local and global coordinate systems. You can calculate this by taking the
        inverse cosine of the dot product of your two x-axes
        """

        # angle = -np.arccos(Vector2D(1, 0).dot(Vector2D(direction.x, direction.y)))
        angle = Vector2D.axis_perp_dot_product(direction)

        print "rotating vector by: {0} rads".format(angle)

        rotated_v = to_move.rotate(angle)
        return rotated_v

    @staticmethod
    def get_global_move(to_move, direction):
        """
        Does the oposite of get_local_move
        """

        # angle = -np.arccos(Vector2D(1, 0).dot(Vector2D(direction.x, direction.y)))
        angle = -Vector2D.axis_perp_dot_product(direction)

        rotated_v = to_move.rotate(angle)
        return rotated_v

    def ball_going_quickly(self):
        """
        Check is ball is going quicker than a threshold velocity
        """
        velocity_threshold = 10
        ball_velocity = self.world.get_ball().velocity.length()
        return ball_velocity > velocity_threshold

    def predict_y(self, predict_for_x):
        """
        Predict the y coordinate the ball will have when it reaches the x coordinate of the robot.
        """
        ball_x = self.ball.position.x
        ball_y = self.ball.position.y
        ball_v = self.ball.velocity

        distance_ball_robot = np.abs(ball_x-predict_for_x)

        if ball_v.x == 0:
            return ball_y
        else:
            return ball_y + (ball_v.y / ball_v.x) * distance_ball_robot

    def y_intercept_of_ball_goal(self, goal_pos, ball_pos):
        to_move_x = self.robot.position.x

        m = 1.0*(goal_pos.y - ball_pos.y)/(goal_pos.x - ball_pos.x)

        to_move_y = (m * (to_move_x - goal_pos.x)) + goal_pos.y

        return to_move_x, to_move_y



