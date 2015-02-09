_author__ = 'Sam Davies'
import unittest
from lib.world.world_state import Robot, Ball, WorldState, Zone
from lib.strategy.attacker1 import Attacker1
from communication.dummy_robot import DummyRobot
from lib.math.vector import Vector2D
from numpy import pi
import time


class TestWorldState(unittest.TestCase):

    def setUp(self):
        pass

    # ensure that a bad robot can be added
    def test_bad_robot(self):
        bad_robot = Robot(direction=(0, 1), position=(0, 0), velocity=(0, 0), enemy=True)
        self.assertTrue(bad_robot.is_enemy())


class TestAttacker1(unittest.TestCase):

    def setUp(self):
        # create a robot and a ball
        robot_1 = Robot(direction=(0, 1), position=(8.0, 8.0), velocity=(0.0, 0.0), enemy=True)
        robot_2 = Robot(direction=(0, 1), position=(15.0, 15.0), velocity=(0.0, 0.0), enemy=True)
        robot_3 = Robot(direction=(0, 1), position=(25, 25), velocity=(0, 0), enemy=True)
        robot_4 = Robot(direction=(0, 1), position=(35, 35), velocity=(0, 0), enemy=True)
        ball = Ball(position=(5, 5), velocity=(0, 0), in_possession=False)

        # set the list of robots
        robots = [robot_1, robot_2, robot_3, robot_4]

        # create a world object
        self.world_state = WorldState(robots=robots, ball=ball, zone_boundaries=[10, 20, 30, 40])
        # make a dummy robot which can change the world
        actual_robot = DummyRobot(self.world_state, Zone.L_ATT)
        # give the strategy the world the dummy and the zone of the dummy
        self.attacker1 = Attacker1(self.world_state, Zone.L_ATT, actual_robot)

    # ensure that the world state is fetched
    def test_fetch_world_state(self):
        self.attacker1.fetch_world_state()
        # check that the correct location is fetched for robot and ball
        self.assertEquals(self.attacker1.robot.position, Vector2D(15, 15))
        self.assertEquals(self.attacker1.ball.position, Vector2D(5, 5))

    # ensure that a close ball is found to be close
    def test_close_ball(self):
        self.change_ball_location(15.0, 15.0+self.attacker1.dist_kicker_robot)
        # check that the ball is close
        self.assertTrue(self.attacker1.is_ball_close())

    def test_vector_ball_kicker(self):
        self.change_ball_location(15.0, 15.0+self.attacker1.dist_kicker_robot)
        vec = self.attacker1.vector_from_kicker_to_ball()
        self.assertEquals(vec.x, 0.0)
        self.assertEquals(vec.y, 0.0)

    def change_ball_location(self, new_ball_x, new_ball_y):
        ball = Ball(position=(new_ball_x, new_ball_y), velocity=(0, 0), in_possession=False)
        self.world_state.set_ball(ball)
        # refresh the robot's world
        self.attacker1.fetch_world_state()

    # ensure that a non close ball is found to be not close
    def test_non_close_ball(self):
        self.change_ball_location(19, 19)
        # check that the ball is close
        self.assertFalse(self.attacker1.is_ball_close())

    # ensure that a robot will turn towards the ball
    def test_robot_turns_towards_ball(self):
        # set up the world so that the robot has to turn
        ball = Ball(position=(15, 15), velocity=(0, 0), in_possession=False)
        robot_2 = Robot(direction=(1, 0), position=(15, 0), velocity=(0, 0), enemy=False)
        self.world_state.set_ball(ball)
        self.world_state.add_robot(Zone.L_ATT, robot_2)
        # raise cage
        self.attacker1.act()
        # turn
        self.attacker1.act()
        # refresh the robot's world
        self.attacker1.fetch_world_state()
        # check that robot if facing the ball
        self.assertTrue(self.attacker1.is_robot_facing_ball())

    # ensure that the robot will move towards the ball when facing it
    def test_robot_moves_to_ball(self):
        # set up the world so that the robot does not have to turn
        ball = Ball(position=(15, 15), velocity=(0, 0), in_possession=False)
        robot_2 = Robot(direction=(0, 1), position=(15, 0), velocity=(0, 0), enemy=False)
        self.world_state.set_ball(ball)
        self.world_state.add_robot(Zone.L_ATT, robot_2)
        # raise cage
        self.attacker1.act()
        # move
        self.attacker1.act()
        # refresh the robot's world
        self.attacker1.fetch_world_state()
        # check that the robot has reached the ball
        self.assertTrue(self.attacker1.is_ball_close())

    # ensure the the robot will lower cage on a close ball
    def test_will_lower_cage(self):
        # set up the world so that the robot does not have to turn or move
        ball = Ball(position=(15, 15), velocity=(0, 0), in_possession=False)
        robot_2 = Robot(direction=(1, 0), position=(15, 12.5), velocity=(0, 0), enemy=False)
        self.world_state.set_ball(ball)
        self.world_state.add_robot(Zone.L_ATT, robot_2)
        # do the next action
        self.attacker1.act()
        # refresh the robot's world
        self.attacker1.fetch_world_state()
        # check that the robot has reached the ball
        self.assertTrue(self.attacker1.is_ball_close())
        self.assertTrue(self.attacker1.is_grabber_down)


    # ensure that a robot not facing goal is false


    # ensure that a robot facing goal is true

    # ensure that robot will turn towards the goal
    def test_turn_to_goal(self):
        ball = Ball(position=(15, 15), velocity=(0, 0), in_possession=False)
        robot_2 = Robot(direction=(1, 0), position=(15, 13), velocity=(0, 0), enemy=False)
        self.world_state.set_ball(ball)
        self.world_state.add_robot(Zone.L_ATT, robot_2)
        self.attacker1.is_grabber_down = True
        # do the next action
        self.attacker1.act()
        # refresh the robot's world
        self.attacker1.fetch_world_state()
        # check that the robot has reached the ball
        self.assertTrue(self.attacker1.is_robot_facing_goal())



if __name__ == '__main__':
    unittest.main()
