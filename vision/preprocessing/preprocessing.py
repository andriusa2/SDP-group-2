import cv2


class Preprocessing(object):

    def __init__(self, options=None):
        if not options:
            # Which methods to run
            self.options = {
                'normalize': False,
                'background_sub': False
            }

        # Default setting for background subtractor
        self.background_sub = None

    def get_options(self):
        return self.options;

    def run(self, frame, options):

        self.options = options

        results = {
            'frame': frame
        }

        # Apply normalization
        if self.options['normalize']:
            # Normalize only the saturation channel
            results['frame'] = self.normalize(frame)
            # print 'Normalizing frame'

        # Apply background subtraction
        if self.options['background_sub']:
            frame = cv2.blur(frame, (2,2))
            # print 'running sub'
            if self.background_sub is not None:
                bg_mask = self.background_sub.apply(frame)
            else:
                self.background_sub = cv2.BackgroundSubtractorMOG2(0, 30, False)
                bg_mask = self.background_sub.apply(frame)
            results['background_sub'] = bg_mask

        return results

    def normalize(self, frame):
        """
        Normalize an image based on its Saturation channel. Returns BGR version
        of the image.
        """
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame[:, :, 1] = cv2.equalizeHist(frame[:, :, 1])
        return cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
