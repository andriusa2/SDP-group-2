from vision.vision import Vision, Camera, GUI
# from planning.planner import Planner
from postprocessing.postprocessing import Postprocessing
from preprocessing.preprocessing import Preprocessing
import vision.tools as tools
from cv2 import waitKey
import cv2
import serial
import warnings
import time


warnings.filterwarnings("ignore", category=DeprecationWarning)


class Controller:
    """
    Primary source of robot control. Ties vision and planning together.
    """

    def __init__(self, pitch, color, our_side, video_port=0, comm_port='/dev/ttyUSB0', comms=1):
        """
        Entry point for the SDP system.

        Params:
            [int] video_port                port number for the camera
            [string] comm_port              port number for the arduino
            [int] pitch                     0 - main pitch, 1 - secondary pitch
            [string] our_side               the side we're on - 'left' or 'right'
            *[int] port                     The camera port to take the feed from
            *[Robot_Controller] attacker    Robot controller object - Attacker Robot has a RED
                                            power wire
            *[Robot_Controller] defender    Robot controller object - Defender Robot has a YELLOW
                                            power wire
        """
        assert pitch in [0, 1]
        assert color in ['yellow', 'blue']
        assert our_side in ['left', 'right']

        self.pitch = pitch

        # Set up the Arduino communications
        # self.arduino = Arduino(comm_port, 115200, 1, comms)

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

        # Set up main planner
        # self.planner = Planner(our_side=our_side, pitch_num=self.pitch)

        # Set up GUI
        # self.GUI = GUI(calibration=self.calibration, arduino=self.arduino, pitch=self.pitch)
        self.GUI = GUI(calibration=self.calibration, arduino=None, pitch=self.pitch)

        self.color = color
        self.side = our_side

        self.preprocessing = Preprocessing()

        # self.attacker = Attacker_Controller()
        # self.defender = Defender_Controller()

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

                # Find appropriate action
                # self.planner.update_world(model_positions)
                # attacker_actions = self.planner.plan('attacker')
                # defender_actions = self.planner.plan('defender')

                # if self.attacker is not None:
                    # self.attacker.execute(self.arduino, attacker_actions)
                # if self.defender is not None:
                    # self.defender.execute(self.arduino, defender_actions)

                # Information about the grabbers from the world
                # grabbers = {
                    # 'our_defender': self.planner._world.our_defender.catcher_area,
                    # 'our_attacker': self.planner._world.our_attacker.catcher_area
                # }

                # Information about states
                # attackerState = (self.planner.attacker_state, self.planner.attacker_strat_state)
                # defenderState = (self.planner.defender_state, self.planner.defender_strat_state)

                # Use 'y', 'b', 'r' to change color.
                c = waitKey(2) & 0xFF
                actions = []
                fps = float(counter) / (time.clock() - timer)
                # Draw vision content and actions

                # self.GUI.draw(
                #     frame, model_positions, actions, regular_positions, fps, attackerState,
                #     defenderState, attacker_actions, defender_actions, grabbers,
                #     our_color=self.color, our_side=self.side, key=c, preprocess=pre_options)
                self.GUI.draw(
                    frame, model_positions, actions, regular_positions, fps, 
                    our_color=self.color, our_side=self.side, key=c, preprocess=pre_options)
                counter += 1

        except:
            # if self.defender is not None:
            #     self.defender.shutdown(self.arduino)
            # if self.attacker is not None:
            #     self.attacker.shutdown(self.arduino)
            raise

        finally:
            # Write the new calibrations to a file.
            tools.save_colors(self.pitch, self.calibration)
            # if self.attacker is not None:
            #     self.attacker.shutdown(self.arduino)
            # if self.defender is not None:
            #     self.defender.shutdown(self.arduino)


class Robot_Controller(object):
    """
    Robot_Controller superclass for robot control.
    """

    def __init__(self):
        """
        Connect to Brick and setup Motors/Sensors.
        """
        self.current_speed = 0

    def shutdown(self, comm):
        # TO DO
            pass


# class Defender_Controller(Robot_Controller):
#     """
#     Defender implementation.
#     """

#     def __init__(self):
#         """
#         Do the same setup as the Robot class, as well as anything specific to the Defender.
#         """
#         super(Defender_Controller, self).__init__()

#     def execute(self, comm, action):
#         """
#         Execute robot action.
#         """

#         if 'turn_90' in action:
#             comm.write('D_RUN_ENGINE %d %d\n' % (0, 0))
#             time.sleep(0.2)
#             comm.write('D_RUN_SHOOT %d\n' % int(action['turn_90']))
#             time.sleep(2.2)

#         #print action
#         left_motor = int(action['left_motor'])
#         right_motor = int(action['right_motor'])
#         speed = action['speed']

#         comm.write('D_SET_ENGINE %d %d\n' % (speed, speed))
#         comm.write('D_RUN_ENGINE %d %d\n' % (left_motor, right_motor))
#         if action['kicker'] != 0:
#             try:
#                 comm.write('D_RUN_KICK\n')
#                 time.sleep(0.5)
#             except StandardError:
#                 pass
#         elif action['catcher'] != 0:
#             try:
#                 comm.write('D_RUN_CATCH\n')
#             except StandardError:
#                 pass

#     def shutdown(self, comm):
#         comm.write('D_RUN_KICK\n')
#         comm.write('D_RUN_ENGINE %d %d\n' % (0, 0))


# class Attacker_Controller(Robot_Controller):
#     """
#     Attacker implementation.
#     """

#     def __init__(self):
#         """
#         Do the same setup as the Robot class, as well as anything specific to the Attacker.
#         """
#         super(Attacker_Controller, self).__init__()

#     def execute(self, comm, action):
#         """
#         Execute robot action.
#         """
#         if 'turn_90' in action:
#             comm.write('A_RUN_ENGINE %d %d\n' % (0, 0))
#             time.sleep(0.2)
#             comm.write('A_RUN_SHOOT %d\n' % int(action['turn_90']))
#             # time.sleep(1.2)
#         else:
#             left_motor = int(action['left_motor'])
#             right_motor = int(action['right_motor'])
#             speed = int(action['speed'])
#             comm.write('A_SET_ENGINE %d %d\n' % (speed, speed))
#             comm.write('A_RUN_ENGINE %d %d\n' % (left_motor, right_motor))
#             if action['kicker'] != 0:
#                 try:
#                     comm.write('A_RUN_KICK\n')
#                 except StandardError:
#                     pass
#             elif action['catcher'] != 0:
#                 try:
#                     comm.write('A_RUN_CATCH\n')
#                 except StandardError:
#                     pass

#     def shutdown(self, comm):
#         comm.write('A_RUN_KICK\n')
#         comm.write('A_RUN_ENGINE %d %d\n' % (0, 0))


# class Arduino:

#     def __init__(self, port, rate, timeOut, comms):
#         self.serial = None
#         self.comms = comms
#         self.port = port
#         self.rate = rate
#         self.timeout = timeOut
#         self.setComms(comms)

#     def setComms(self, comms):
#         if comms > 0:
#             self.comms = 1
#             if self.serial is None:
#                 try:
#                     self.serial = serial.Serial(self.port, self.rate, timeout=self.timeout)
#                 except:
#                     print "No Arduino detected!"
#                     print "Continuing without comms."
#                     self.comms = 0
#                     #raise
#         else:
#             #self.write('A_RUN_KICK\n')
#             self.write('A_RUN_ENGINE %d %d\n' % (0, 0))
#             #self.write('D_RUN_KICK\n')
#             self.write('D_RUN_ENGINE %d %d\n' % (0, 0))
#             self.comms = 0

#     def write(self, string):
#         if self.comms == 1:
#             self.serial.write(string)


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
        c = Controller(
            pitch=int(args.pitch), color=args.color, our_side=args.side, comms=0).wow()
    else:
        c = Controller(
            pitch=int(args.pitch), color=args.color, our_side=args.side).wow()
