from vision.vision import Vision, Camera, GUI
from postprocessing.postprocessing import Postprocessing
from preprocessing.preprocessing import Preprocessing
import vision.tools as tools
from cv2 import waitKey
import cv2
import warnings
import time

from lib.strategy.attacker1 import Attacker1
from lib.world.world_state import WorldState, Zone


warnings.filterwarnings("ignore", category=DeprecationWarning)


class VisionController:
    """
    Primary source of robot control. Ties vision and planning together.
    """

    def __init__(self, pitch, color, our_side, video_port=0):
        """
        Entry point for the SDP system.

        Params:
            [int] video_port                port number for the camera
            [int] pitch                     0 - main pitch, 1 - secondary pitch
            [string] our_side               the side we're on - 'left' or 'right'
        """
        assert pitch in [0, 1]
        assert color in ['yellow', 'blue']
        assert our_side in ['left', 'right']

        self.pitch = pitch

        # Set up camera for frames
        self.camera = Camera(port=video_port, pitch=self.pitch)
        frame = self.camera.get_frame()
        center_point = self.camera.get_adjusted_center(frame)

        # Set up vision
        self.calibration = tools.get_colors(pitch)
        self.vision = Vision(
            pitch=pitch, color=color, our_side=our_side,
            frame_shape=frame.shape, frame_center=center_point,
            calibration=self.calibration)

        # Set up postprocessing for vision
        self.postprocessing = Postprocessing()

        # Set up GUI
        self.GUI = GUI(calibration=self.calibration, arduino=None, pitch=self.pitch)

        self.color = color
        self.side = our_side

        self.preprocessing = Preprocessing()

        #---------------------- PLANNER ---------------------------
        boundries = [47, 106, 165, 212]
        actual_robot = None
        self.world = WorldState()

        # set the initial state
        self.update_world_state()
        # set the boundries
        self.world.set_zone_boundaries(boundries)

        # this is our chosen strategy
        self.attacker1 = Attacker1(self.world, Zone.L_ATT, actual_robot)

        #----------------------------------------------------------

    def wow(self):
        """
        Ready your sword, here be dragons.
        """
        counter = 1L
        timer = time.clock()
        try:
            c = True
            while c != 27:  # the ESC key

                frame = self.camera.get_frame()
                pre_options = self.preprocessing.options
                # Apply preprocessing methods toggled in the UI
                preprocessed = self.preprocessing.run(frame, pre_options)
                frame = preprocessed['frame']
                if 'background_sub' in preprocessed:
                    cv2.imshow('bg sub', preprocessed['background_sub'])
                # Find object positions
                # model_positions have their y coordinate inverted

                model_positions, regular_positions = self.vision.locate(frame)
                model_positions = self.postprocessing.analyze(model_positions)

                #---------------------- PLANNER ---------------------------
                self.update_world_state()
                self.attacker1.act()
                #----------------------------------------------------------

                # Use 'y', 'b', 'r' to change color.
                c = waitKey(2) & 0xFF
                actions = []
                fps = float(counter) / (time.clock() - timer)
                # Draw vision content and actions
                self.GUI.draw(
                    frame, model_positions, actions, regular_positions, fps, 
                    our_color=self.color, our_side=self.side, key=c, preprocess=pre_options)
                counter += 1

        except:
            raise

        finally:
            # Write the new calibrations to a file.
            tools.save_colors(self.pitch, self.calibration)

    def update_world_state(self):
        """
        Change the state of the world based on the current frame
        :param world: the world which has to be chaged
        :return: none
        """
        # create a robot and a ball
        robot_1 = Robot(direction=(0, 1), position=(8.0, 8.0), velocity=(0.0, 0.0), enemy=True)
        robot_2 = Robot(direction=(0, 1), position=(15.0, 15.0), velocity=(0.0, 0.0), enemy=True)
        robot_3 = Robot(direction=(0, 1), position=(25, 25), velocity=(0, 0), enemy=True)
        robot_4 = Robot(direction=(0, 1), position=(35, 35), velocity=(0, 0), enemy=True)
        ball = Ball(position=(5, 5), velocity=(0, 0), in_possession=False)

        # set the list of robots
        robots = [robot_1, robot_2, robot_3, robot_4]

        # change the states of the robots in the world
        self.world.set_robots_list(robots)
        # change the position of the ball
        self.world.set_ball(ball)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Main pitch, [1] Secondary pitch")
    parser.add_argument("side", help="The side of our defender ['left', 'right'] allowed.")
    parser.add_argument("color", help="The color of our team - ['yellow', 'blue'] allowed.")
    parser.add_argument(
        "-n", "--nocomms", help="Disables sending commands to the robot.", action="store_true")

    args = parser.parse_args()
    if args.nocomms:
        c = VisionController(
            pitch=int(args.pitch), color=args.color, our_side=args.side, comms=0).wow()
    else:
        c = VisionController(
            pitch=int(args.pitch), color=args.color, our_side=args.side).wow()
