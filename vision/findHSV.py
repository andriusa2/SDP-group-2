import cv2
import numpy as np

CONTROLS = ["LH", "UH", "LS", "US", "LV", "UV", "CT", "BL"]
MAXBAR = {"LH":360,
          "UH":360,
          "LS":255,
          "US":255,
          "LV":255,
          "UV":255,
          "CT":100,
          "BL":100
        }

INDEX = {"LH":0,
         "UH":0,
         "LS":1,
         "US":1,
         "LV":2,
         "UV":2
        }

KEYS = {ord('y'):'yellow',
        ord('r'):'red',
        ord('b'):'blue',
        ord('d'):'dot',
        ord('p'):'plate'}

def nothing(x):
    pass

class CalibrationGUI(object):

    def __init__(self, calibration):
        self.color = 'plate'
        # self.pre_options = pre_options
        self.calibration = calibration
        self.maskWindowName = "Mask " + self.color

        self.setWindow()

    def setWindow(self):

        cv2.namedWindow(self.maskWindowName)

        createTrackbar = lambda setting, value: cv2.createTrackbar(setting, self.maskWindowName, int(value), \
                MAXBAR[setting], nothing)
        createTrackbar('LH', self.calibration[self.color]['min'][0])
        createTrackbar('UH', self.calibration[self.color]['max'][0])
        createTrackbar('LS', self.calibration[self.color]['min'][1])
        createTrackbar('US', self.calibration[self.color]['max'][1])
        createTrackbar('LV', self.calibration[self.color]['min'][2])
        createTrackbar('UV', self.calibration[self.color]['max'][2])
        createTrackbar('CT', self.calibration[self.color]['contrast'])
        createTrackbar('BL', self.calibration[self.color]['blur'])

    def change_color(self, color):

        cv2.destroyWindow(self.maskWindowName)
        self.color = color
        self.maskWindowName = "Mask " + self.color
        self.setWindow()

    def show(self, frame, key=None):

        if key != 255:
            try:
                self.change_color(KEYS[key])
            except:
                pass

        getTrackbarPos = lambda setting: cv2.getTrackbarPos(setting, self.maskWindowName)

        values = {}
        for setting in CONTROLS:
            values[setting] = float(getTrackbarPos(setting))
        values['BL'] = int(values['BL'])

        self.calibration[self.color]['min'] = np.array([values['LH'], values['LS'], values['LV']])
        self.calibration[self.color]['max'] = np.array([values['UH'], values['US'], values['UV']])
        self.calibration[self.color]['contrast'] = values['CT']
        self.calibration[self.color]['blur'] = values['BL']

        mask = self.get_mask(frame)
        cv2.imshow(self.maskWindowName, mask)

    # Duplicated from tracker.py
    def get_mask(self, frame):
        blur = self.calibration[self.color]['blur']
        if blur > 1:
            frame = cv2.blur(frame, (blur,blur))

        contrast = self.calibration[self.color]['contrast']
        if contrast > 1.0:
            frame = cv2.add(frame, np.array([contrast]))

        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        min_color = self.calibration[self.color]['min']
        max_color = self.calibration[self.color]['max']
        frame_mask = cv2.inRange(frame_hsv, min_color, max_color)

        return frame_mask