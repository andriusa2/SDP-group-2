import numpy as np

from lib.math.vector import Vector2D
from planning.actions.move import Move
from planning.actions.other import Other
from planning.actions.turn import Turn
from planning.config import Config
from planning.strategies.state_machine import StateMachine
from planning.world_state import Zone, Robot, Ball


__author__ = 'Sam'


class Strategy(object):

    def __init__(self, world, robot_tag, actual_robot, config=None):
        self.actual_robot = actual_robot
        self.robot_tag = robot_tag
        self.world = world

        # this sets the default config
        if config is None:
            config = Config()

        self.grab_threshold = config.GRAB_THRESHOLD
        self.dist_kicker_robot = config.DIST_KICKER_ROBOT

        self.ROBOT_WIDTH = config.ROBOT_WIDTH
        self.zone_centre_width = config.ZONE_CENTRE_WIDTH
        self.pitch_height = config.PITCH_HEIGHT

        self.move_dampening = config.MOVE_DAMPENING
        self.max_move = config.MAX_MOVE

        self.turn_dampening = config.TURN_DAMPENING
        self.max_turn = config.MAX_TURN

        self.square_angle_threshold = config.SQUARE_ANGLE_THRESHOLD
        self.zone_centre_offset = config.ZONE_CENTRE_OFFSET

        self.ball_velocity_grabber_trigger = config.BALL_VELOCITY_GRABBER_TRIGGER
        self.ball_distance_grabber_trigger = config.BALL_DISTANCE_GRABBER_TRIGGER

        # initialise state attributes
        self.robot = Robot()
        self.ball = Ball()
        self.own_goal = None
        self.enemy_goal = None
        self.m = StateMachine()
        self.move = Move()
        self.turn = Turn()
        self.other = Other()

    def fetch_world_state(self):
        """
        grab the latest state of the world and set this objects attribute
        :return: nothing
        """
        self.robot = self.world.get_robot(self.robot_tag)
        self.ball = self.world.get_ball()
        self.own_goal = self.get_own_goal()
        self.enemy_goal = self.get_enemy_goal()

        # update rotation and movement
        self.move.__int__(self)
        self.turn.__int__(self)
        self.other.__int__(self)

    """
    -------------------------------------------------------
        Complex World State Checks
    -------------------------------------------------------
    """

    def is_facing_own_goal(self):
        """
        Check if the angle between the robot and
        the centre of the goal is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        goal = self.own_goal
        return self.robot.can_see(point=goal, beam_width=self.ROBOT_WIDTH)

    def is_facing_enemy_goal(self):
        """
        Check if the angle between the robot and
        the centre of the goal is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        goal = self.enemy_goal
        return self.robot.can_see(point=goal, beam_width=4*self.ROBOT_WIDTH)

    def is_robot_facing_ball(self):
        """
        Check if the angle between the robot and
        the ball is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        ball_pos = self.ball.position
        return self.robot.can_see(point=ball_pos, beam_width=self.ROBOT_WIDTH/2)

    def is_at_square_angles(self):
        # dir_x = self.robot.direction.x
        # dir_y = self.robot.direction.y
        #
        # major_axis = max(abs(dir_x), abs(dir_y))
        # print "Major axis is {0}, and is at square angles if > {1}".format(major_axis, 1-self.square_angle_threshold)
        # return major_axis > 1-self.square_angle_threshold
        """is facing direction of the goal"""
        dir_x = self.robot.direction.x
        my_zone = self.world.get_zone(self.robot.position)
        if my_zone == Zone.L_ATT or my_zone == Zone.L_DEF:
            return dir_x > 1-self.square_angle_threshold
        else:
            return dir_x < -1+self.square_angle_threshold


    def is_robot_facing_point(self, point, beam_width=None):
        """
        Check to see if a point is in the robots beam
        :return: whether or not the robot is facing the point
        """
        if not beam_width:
            beam_width = self.ROBOT_WIDTH
        return self.robot.can_see(point=point, beam_width=beam_width)

    def is_robot_in_centre_x(self):
        zone_centre_x = self.get_my_zone_centre()
        centre_bound_l = zone_centre_x - (self.zone_centre_width/2)
        centre_bound_r = zone_centre_x + (self.zone_centre_width/2)
        return centre_bound_l < self.robot.position.x < centre_bound_r

    def is_robot_in_centre_y(self):
        zone_centre_y = self.get_zone_centre_y()
        centre_bound_l = zone_centre_y - (self.zone_centre_width/2)
        centre_bound_r = zone_centre_y + (self.zone_centre_width/2)
        return centre_bound_l < self.robot.position.y < centre_bound_r

    def is_robot_safe(self):
        return True

    def select_bounce_point(self):
        """
        Determine the bounce point, either up or down, which is furthest from the enemy robot
        :return: a Vector2D
        """
        self.fetch_world_state()
        enemy_zone = self.world.get_zone(self.get_enemy().position)
        enemy_zone_centre = self.get_zone_centre(enemy_zone)
        preset_pass_locations = [Vector2D(enemy_zone_centre, 110), Vector2D(enemy_zone_centre, 0)]

        enemy_position_x = self.get_enemy().position.x
        enemy_position_y = self.get_enemy().position.y
        v1 = preset_pass_locations[0]
        v2 = preset_pass_locations[1]
        dist_to_1 = self.dist_to_pass_point(enemy_position_x, enemy_position_y, v1.x, v1.y)
        dist_to_2 = self.dist_to_pass_point(enemy_position_x, enemy_position_y, v2.x, v2.y)

        max_distance = max(dist_to_1, dist_to_2)
        v = v1 if max_distance == dist_to_1 else v2
        return v

    def ball_in_enemy_att_zone(self):
        return self.world.get_zone(self.world.ball.position) == self.world.get_zone(self.get_enemy().position)

    def ball_is_fast(self):
        ball_vel = self.world.ball.velocity

        # is moving
        is_fast = ball_vel.length() > self.ball_velocity_grabber_trigger
        not_too_fast = ball_vel.length() < 150

        """ball_pos = self.world.ball.position
        enemy_pos = self.get_enemy().position
        my_zone = self.world.get_zone(self.robot.position)
        if my_zone == Zone.L_ATT or my_zone == Zone.L_DEF:
            # is ball direction towards us
            is_towards = abs(ball_vel.x) > abs(ball_vel.y) and ball_vel.x < 0

            # is ball X beyond enemy
            print ball_pos.x + self.ball_distance_grabber_trigger, enemy_pos.x
            is_beyond = ball_pos.x + self.ball_distance_grabber_trigger < enemy_pos.x

        else:
            # is ball direction towards us
            is_towards = abs(ball_vel.x) > abs(ball_vel.y) and ball_vel.x > 0

            # is ball X beyond enemy
            is_beyond = ball_pos.x - self.ball_distance_grabber_trigger > enemy_pos.x

        print is_fast, not_too_fast, is_towards, is_beyond"""
        return is_fast and not_too_fast # and is_towards and is_beyond

    """
    -------------------------------------------------------
        Fetching of Objects in World State
    -------------------------------------------------------
    """

    def get_my_zone_centre(self):
        my_zone = self.world.get_zone(self.robot.position)
        return self.get_zone_centre(my_zone, True)

    def get_zone_centre(self, zone, offset=False):
        zone_edges = [0] + self.world.zone_boundaries
        edge_L = zone_edges[zone]
        edge_R = zone_edges[zone+1]
        zone_width = edge_R - edge_L
        zone_centre = edge_L + zone_width/2.0

        # move the centre closer to the pitch centre
        if offset:
            if zone >= 2:
                zone_centre -= (self.zone_centre_offset * (zone_width/2))
            else:
                zone_centre += (self.zone_centre_offset * (zone_width/2))
        print "Left: {0}, right {1}, centre: {2}".format(edge_L, edge_R, zone_centre)
        return zone_centre

    def get_zone_centre_y(self):
        zone_center_y = self.pitch_height/2
        return zone_center_y

    def is_ball_in_friend_zone(self):
        friend_zone = self.world.get_zone(self.get_friend().position)
        ball_zone = self.world.get_zone(self.world.get_ball().position)
        return friend_zone == ball_zone

    def get_own_goal(self):
        zone = self.world.get_zone(self.robot.position)
        if zone == Zone.L_ATT or zone == Zone.L_DEF:
            return self.world.left_goal
        else:
            return self.world.right_goal

    def get_enemy_goal(self):
        zone = self.world.get_zone(self.robot.position)
        if zone == Zone.L_ATT or zone == Zone.L_DEF:
            return self.world.right_goal
        else:
            return self.world.left_goal

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
        if my_zone == 0 or my_zone == 1:
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
        if my_zone == 0 or my_zone == 1:
            enemy = self.world.get_robot(Zone.R_DEF)
        else:
            enemy = self.world.get_robot(Zone.L_DEF)
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
        return ball_kicker_vector.length() < self.grab_threshold

    def is_ball_close_x2(self):
        """
        checks whether the ball is in close proximity to the robot's kicker
        :return:
        """
        self.fetch_world_state()

        # check if the balls is in close enough to the robot to be grabbed
        ball_kicker_vector = self.vector_from_kicker_to_ball()
        return ball_kicker_vector.length() < (self.grab_threshold * 1.5)

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

    def dist_to_pass_point(self, x1, y1, x2, y2):
        return self.vector_to_pass_point(x1, y1, x2, y2).length()

    @staticmethod
    def vector_to_pass_point(x1, y1, x2, y2):
        dist_x = -x1 + x2
        dist_y = -y1 + y2
        return Vector2D(dist_x, dist_y)

    @staticmethod
    def get_local_move(to_move, direction):
        """
        For a vector, all that you have to do is rotate it by the angle difference between
        your local and global coordinate systems. You can calculate this by taking the
        inverse cosine of the dot product of your two x-axes
        """

        # angle = -np.arccos(Vector2D(1, 0).dot(Vector2D(direction.x, direction.y)))
        angle = Vector2D.axis_perp_dot_product(direction.square_unit_vector())

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



