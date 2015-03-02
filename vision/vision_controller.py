import warnings
import time

from vision import Vision, Camera, GUI
from postprocessing.postprocessing import Postprocessing
from preprocessing.preprocessing import Preprocessing
import tools as tools
from cv2 import waitKey
import cv2


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

    def send_model_to_planner(self, planning_function):
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
                planner = planning_function(model_positions)
                print_list = (planner.m.state_trace[len(planner.m.state_trace)-2],
                              planner.m.state_trace[len(planner.m.state_trace)-1])
                # print print_list
                #----------------------------------------------------------

                # Use 'y', 'b', 'r' to change color.
                c = waitKey(2) & 0xFF
                actions = []
                fps = float(counter) / (time.clock() - timer)
                # Draw vision content and actions
                self.GUI.draw(
                    frame, model_positions, actions, regular_positions, fps, (print_list[0],print_list[1]),
                    our_color=self.color, our_side=self.side, key=c, preprocess=pre_options)
                counter += 1

        except:
            raise

        finally:
            # Write the new calibrations to a file.
            tools.save_colors(self.pitch, self.calibration)

