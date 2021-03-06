from planning.planner import Planner
from planning.world_state import WorldState, Zone, Robot, Ball
from vision.vision_controller import VisionController
from communication import Controller as CommController
import cv2
__author__ = "Sam Davies"


class Controller(object):

    def __init__(self, side, debug):

        if side == "left":
            self.side = Zone.L_DEF
        else:
            if side == "right":
                self.side = Zone.R_DEF
            else:
                raise Exception("Please select a side. (left or right)")

        if debug == 'pro':
            debug = False
            step = False
        else:
            if debug == 'debug':
                debug = True
                step = False
            else:
                if debug == 'step':
                    debug = True
                    step = True
                else:
                    raise Exception("Please specify a valid debug mode (pro, debug or step)")

        self.debug = debug
        self.step = step

        # boundaries = [47, 106, 165, 212]
        self.world = WorldState()

        self.actual_robot = CommController("/dev/ttyACM0", ack_tries=10)
        from time import sleep
        sleep(5)

        # actual_robot.open_grabber()

        # this is our chosen strategy
        """R_ATT, L_ATT, R_DEF, L_DEF"""
        self.vision = VisionController(video_port=0, draw_debug=('pos', 'vel', 'dir'))

        # set the boundaries
        points = [x for (x, y) in self.vision.zone_filter.points]
        w = self.vision.get_frame().shape[1]
        wx = w - 2 * self.vision.zone_filter.img_x_padding
        self.world.set_zone_boundaries([47, 106, 165, 212])
        self.state = None
        # self.world.set_zone_boundaries(self.vision.zone_filter.points + [self.vision.zone_filter.w])

        self.planner = None

    def main(self):
        """
        grabs the latest frame from vision, update the
        world based on that frame and runs the next plan
        :return: nothing
        """
        # let the vision update the world
        self.state = None

        while True:
            self.state = self.vision.analyse_frame(previous_state=self.state)

            key = cv2.waitKey(1) & 0xFF
            self.update_world_state(self.state, self.step, key)

    @staticmethod
    def fetch_our_zone(zone_num):
        """
        choose our robot's zone, with 1 being at the left and 4 being at the right
        :param zone_num
        """
        assert zone_num in [1, 2, 3, 4]

    def update_world_state(self, state, step, key):
        """
        Change the state of the world based on the current frame
        """
        robot1 = Robot(state.get_robot(0).get_direction(),
                       state.get_robot(0).get_position_units(),
                       state.get_robot(0).get_velocity_units(),
                       enemy=False)
        robot2 = Robot(state.get_robot(1).get_direction(),
                       state.get_robot(1).get_position_units(),
                       state.get_robot(1).get_velocity_units(),
                       enemy=False)
        robot3 = Robot(state.get_robot(2).get_direction(),
                       state.get_robot(2).get_position_units(),
                       state.get_robot(2).get_velocity_units(),
                       enemy=False)
        robot4 = Robot(state.get_robot(3).get_direction(),
                       state.get_robot(3).get_position_units(),
                       state.get_robot(3).get_velocity_units(),
                       enemy=False)

        robots = [robot1, robot2, robot3, robot4]

        ball = Ball(state.get_ball().get_position_units(smoothing=False),
                    state.get_ball().get_velocity_units())

        # change the states of the robots in the world
        self.world.set_robots_list(robots)
        # change the position of the ball
        self.world.set_ball(ball)

        if not self.planner:
            self.planner = Planner(self.world, self.side, self.actual_robot, False, debug=self.debug)

        if not step:
                    self.planner.plan()
        else:
            if key == 10:
                self.planner.plan()

        return self.planner

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("side", help="Should we run commands manually")
    parser.add_argument("debug", help="Should we run commands manually")
    args = parser.parse_args()
    contr = Controller(debug=args.debug, side=args.side)
    contr.main()
