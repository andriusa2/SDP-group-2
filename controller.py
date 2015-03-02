from planning.planner import Planner
from planning.world.world_state import WorldState, Zone, Robot, Ball
from vision.vision_controller import VisionController
from communication import Controller as CommController
__author__ = "Sam Davies"


class Controller(object):

    def __init__(self, pitch, color, our_side):

        boundaries = [47, 106, 165, 212]
        self.world = WorldState()
        self.actual_robot = CommController("/dev/ttyACM0", ack_tries=10)
        from time import sleep
        sleep(5)
        # actual_robot.open_grabber()
        # set the boundaries
        self.world.set_zone_boundaries(boundaries)

        # this is our chosen strategy
        """R_ATT, L_ATT, R_DEF, L_DEF"""
        self.vision = VisionController(pitch, color, our_side)

        self.planner = None

    def main(self):
        """
        grabs the latest frame from vision, update the
        world based on that frame and runs the next plan
        :return: nothing
        """
        # let the vision update the world
        self.vision.send_model_to_planner(self.update_world_state)

    def fetch_our_zone(self, zone_num):
        """
        choose our robot's zone, with 1 being at the left and 4 being at the right
        :param zone_num
        """
        assert zone_num in [1, 2, 3, 4]

    def update_world_state(self, model_positions):
        """
        Change the state of the world based on the current frame
        :param model_positions: the values to change to world to
        :return: none
        """
        scale_factor = 0.4

        robot_models = [model_positions['our_defender'], model_positions['our_attacker'],
                        model_positions['their_defender'], model_positions['their_attacker']]
        robot1 = Robot().convert_from_model(robot_models[0], scale_factor)
        robot2 = Robot().convert_from_model(robot_models[1], scale_factor)
        robot3 = Robot().convert_from_model(robot_models[2], scale_factor)
        robot4 = Robot().convert_from_model(robot_models[3], scale_factor)

        robots = [robot1, robot2, robot3, robot4]

        model_ball = model_positions['ball']
        ball = Ball().convert_from_model(model_ball, scale_factor)

        # change the states of the robots in the world
        self.world.set_robots_list(robots)
        # change the position of the ball
        self.world.set_ball(ball)

        # do the next plan
        # self.planner.plan_defence()
        if not self.planner:
            self.planner = Planner(self.world, Zone.L_DEF, self.actual_robot, False)
        self.planner.plan()

        return self.planner

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Main pitch, [1] Secondary pitch")
    parser.add_argument("side", help="The side of our defender ['left', 'right'] allowed.")
    parser.add_argument("color", help="The color of our team - ['yellow', 'blue'] allowed.")

    args = parser.parse_args()
    c = Controller(pitch=int(args.pitch), color=args.color, our_side=args.side)
    c.main()
