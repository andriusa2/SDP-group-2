import cv2
import numpy as np
import tools
import argparse

FRAME_NAME = 'ConfigureWindow'

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

distort_data = tools.get_radial_data()
NCMATRIX = distort_data['new_camera_matrix']
CMATRIX = distort_data['camera_matrix']
DIST = distort_data['dist']


class Configure(object):

        def __init__(self, pitch, width=640, height=480):
                self.width = width
                self.height = height
                self.pitch = pitch
                self.camera = cv2.VideoCapture(0)
                self.new_polygon = True
                self.polygon = self.polygons = []
                self.points = []

                keys = ['outline', 'Zone_0', 'Zone_1', 'Zone_2', 'Zone_3']
                self.data = self.drawing = {}

                # Create keys
                for key in keys:
                        self.data[key] = []
                        self.drawing[key] = []

                self.color = RED


        def run(self, camera=False):
                frame = cv2.namedWindow(FRAME_NAME)

                # Set callback
                cv2.setMouseCallback(FRAME_NAME, self.draw)

                if camera:
                        cap = cv2.VideoCapture(0)
                        for i in range(10):
                                status, image = cap.read()
                else:
                        image = cv2.imread('00000001.jpg')

                self.image = cv2.undistort(image, CMATRIX, DIST, None, NCMATRIX)

                # Get various data about the image from the user
                self.get_pitch_outline()

                self.get_zone('Zone_0', 'draw LEFT Defender')
                self.get_zone('Zone_1', 'draw LEFT Attacker')
                self.get_zone('Zone_2', 'draw RIGHT Attacker')
                self.get_zone('Zone_3', 'draw RIGHT Defender')

                self.get_goal('Zone_0')
                self.get_goal('Zone_3')

                print 'Press any key to finish.'
                cv2.waitKey(0)
                cv2.destroyAllWindows()

                # Write out the data
                # self.dump('calibrations/calibrate.json', self.data)
                tools.save_croppings(pitch=self.pitch, data=self.data)

        def reshape(self):
                return np.array(self.data[self.drawing], np.int32).reshape((-1,1,2))

        def draw_poly(self, points):
                cv2.polylines(self.image, [points], True, self.color)
                cv2.imshow(FRAME_NAME, self.image)

        def get_zone(self, key, message):
                print '%s. %s' % (message, "Continue by pressing q")
                self.drawing, k = key, True

                while k != ord('q'):
                        cv2.imshow(FRAME_NAME, self.image)
                        k = cv2.waitKey(100) & 0xFF

                self.draw_poly(self.reshape())

        def get_pitch_outline(self):
                """
                Let user select points that corespond to the pitch outline.
                End selection by pressing 'q'.
                Result is masked and cropped.
                """
                self.get_zone('outline', 'Draw the outline of the pitch. Contine by pressing \'q\'')

                # Setup black mask to remove overflows
                self.image = tools.mask_pitch(self.image, self.data[self.drawing])

                # Get crop size based on points
                size = tools.find_crop_coordinates(self.image, self.data[self.drawing])
                # Crop
                self.image = self.image[size[2]:size[3], size[0]:size[1]]

                cv2.imshow(FRAME_NAME, self.image)

        def draw(self, event, x, y, flags, param):
                """
                Callback for events
                """
                if event == cv2.EVENT_LBUTTONDOWN:
                        color = self.color
                        cv2.circle(self.image, (x-1, y-1), 2, color, -1)
                        self.data[self.drawing].append((x,y))

        def get_goal(self, zone):
                """
                Returns the top and bottom corner of the goal in zone.
                """
                coords = self.data[zone]
                reverse = int(zone[-1]) % 2
                goal_coords = sorted(coords, reverse=reverse)[:2]
                if goal_coords[0][1] > goal_coords[1][1]:
                        topCorner = goal_coords[1]
                        bottomCorner = goal_coords[0]
                else:
                        topCorner = goal_coords[0]
                        bottomCorner = goal_coords[1]
                self.data[zone + '_goal'] = [topCorner, bottomCorner]


if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('pitch', help='Select pitch to be cropped [0, 1]')
        args = parser.parse_args()
        pitch_num = int(args.pitch)
        assert pitch_num in [0, 1]

        c = Configure(pitch=pitch_num)
        c.run(camera=True)
