import numpy as np
from lib.math.vector import Vector2D
from planning.strategies.state_machine import StateMachine
from planning.world.world_state import Zone

__author__ = 'Sam'


class Strategy(object):

    def __init__(self, world, robot_tag, actual_robot):
        self.actual_robot = actual_robot
        self.robot_tag = robot_tag
        self.world = world

        self.grab_threshold_x = 10  # we need to define these (based on kicker)
        self.grab_threshold_y = 5
        self.dist_kicker_robot = 12

        self.ROBOT_WIDTH = 4

        # initialise state attributes
        self.robot = None
        self.ball = None
        self.goal = None
        self.m = StateMachine()

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

        print "friend pos ({0}, {1})".format(friend.position.x, friend.position.y)
        return friend

    def get_enemy(self):
        self.fetch_world_state()
        my_zone = self.world.get_zone(self.robot.position)
        if my_zone == 0 or 1:
            enemy = self.world.get_robot(Zone.L_ATT)
        else:
            enemy = self.world.get_robot(Zone.R_ATT)
        print "enemy pos ({0}, {1})".format(enemy.position.x, enemy.position.y)
        return enemy

    def shoot(self):
        """
        We are facing the goal so just kick
        :return: duration that the motors are on
        """
        self.world.is_grabber_down = False
        return self.actual_robot.kick()  # kick

    def turn_robot_to_goal(self):
        to_turn = self.robot.angle_to_point(self.goal)
        return self.actual_robot.turn(to_turn)  # turn towards the the goal

    def turn_robot_to_ball(self):
        """
        Turn the robot to face the ball
        :return: duration that the motors are on
        """
        to_turn = self.robot.angle_to_point(self.ball.position)
        return self.actual_robot.turn(to_turn)  # turn towards the the ball

    def move_robot_to_ball(self):
        """
        Move the robot forward in a straight line to the ball
        :return: duration that the motors are on
        """
        dist_to_ball = self.distance_from_kicker_to_ball() * 0.8  # only move 90%
        return self.actual_robot.move(dist_to_ball)

    def raise_cage(self):
        """
        opens the grabber arms
        :return: time it takes for the grabbers to open
        """
        self.world.is_grabber_down = False
        return self.actual_robot.kick()

    def lower_cage(self):
        """
        closes the grabber in an attempt to collect the ball
        :return: time it takes for the grabbers to close
        """
        self.world.is_grabber_down = True
        return self.actual_robot.grab()

    def is_ball_in_robot_zone(self):
        zone_ball = self.world.get_zone(self.ball.position)
        zone_robot = self.world.get_zone(self.robot.position)
        return zone_ball == zone_robot

    def is_robot_facing_goal(self):
        """
        Check if the angle between the robot and
        the centre of the goal is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        goal = self.goal
        robot = self.world.get_robot(self.robot_tag)
        return robot.can_see(point=goal, beam_width=self.ROBOT_WIDTH)

    def is_robot_facing_ball(self):
        """
        Check if the angle between the robot and
        the ball is less than a threshold
        :return: whether or not the robot is facing the ball
        """
        robot = self.world.get_robot(self.robot_tag)
        ball_pos = self.world.get_ball().position
        return robot.can_see(point=ball_pos, beam_width=self.ROBOT_WIDTH/2)

    def is_robot_facing_up(self):
        """
        Check the up position is
        inside the beam projected from the robot
        :return: whether or not the robot is facing the ball
        """
        up_pos = Vector2D(self.robot.position.x, 150)
        robot = self.world.get_robot(self.robot_tag)
        return robot.can_see(point=up_pos, beam_width=self.ROBOT_WIDTH * 5)

    def is_robot_facing_point(self, point, beam_width=None):
        """
        Check to see if a point is in the robots beam
        :return: whether or not the robot is facing the point
        """
        if not beam_width:
            beam_width = self.ROBOT_WIDTH
        print "pass point ({0}, {1})".format(point.x, point.y)
        robot = self.world.get_robot(self.robot_tag)
        return robot.can_see(point=point, beam_width=beam_width)

    def fetch_world_state(self):
        """
        grab the latest state of the world and set this objects attribute
        :return: nothing
        """
        self.robot = self.world.get_robot(self.robot_tag)
        self.ball = self.world.get_ball()
        self.goal = self.get_goal()

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

    def ball_going_quickly(self):
        """
        Check is ball is going quicker than a threshold velocity
        """
        velocity_threshold = 10
        ball_velocity = self.world.get_ball().velocity.length()
        return ball_velocity > velocity_threshold

    def get_zone_centre(self):
        return Vector2D(0, 0)  # TODO

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

    @staticmethod
    def y_intercept_of_ball_goal(robot_pos, goal_pos, ball_pos):
        to_move_x = robot_pos.x

        m = 1.0*(goal_pos.y - ball_pos.y)/(goal_pos.x - ball_pos.x)

        to_move_y = (m * (robot_pos.x - goal_pos.x)) + goal_pos.y

        return to_move_x, to_move_y



