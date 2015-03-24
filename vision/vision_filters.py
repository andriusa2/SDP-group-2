import json
import cv2
import numpy as np
"""
TODO: filter for distortion.
"""


class VisionFilter(object):
    """ ABC for vision filters. Describes a relevant interface. """
    
    def __init__(self, serialize_slots):
        self.loaded = False
        self.filename = "{0}.json".format(self.__class__.__name__)
        self.serialize_slots = serialize_slots or []
        self.load_from_file()
        
    def load_from_file(self):
        try:
            with open(self.filename) as f:
                data = json.load(f)
            
            for key in data:
                if key in self.serialize_slots or not self.serialize_slots:
                    self.__dict__[key] = data[key]
            self.loaded = True
        except IOError:
            print "No file dump '{0}' found.".format(self.filename)
            self.loaded = False
    
    def dump_to_file(self):
        dump_dict = {}
        if self.serialize_slots:
            for key in self.serialize_slots:
                dump_dict[key] = self.__dict__[key]
        else:
            self.dump_dict = self.__dict__
        with open(self.filename, 'w') as f:
            json.dump(dump_dict, f)

    def setup(self, img):
        raise NotImplementedError
    
    def filter(self, img):
        pass


def close_by((x,y), (a, b)):
    return abs(x - a) + abs(y - b) < 10  # manhattan distance
    
class CropFilter(VisionFilter):
    """ A filter for all sorts of cropping things. Filtering logic is abstract, gives uniform way to set up it. """
    def __init__(self, window_name, serialize_slots=None):
        self.points = []
        self.redraw = True
        self.window_name = window_name
        slots = serialize_slots or []
        slots += ['points']
        super(CropFilter, self).__init__(slots)
    
    def add_point(self, x, y):
        if self.points and close_by(self.points[-1], (x, y)):
            return False
        print "Adding point {0!r}".format( (x, y) )
        self.points.append((x, y))
        self.redraw = True
        return True

    def remove_last_point(self):
        if self.points:
            print "Removing point {0!r}".format(self.points[-1])
            del self.points[-1]
            self.redraw = True
    
    def draw_points(self, img):
        return img
        
    def get_img_with_points(self, img, old_img):
        if self.redraw:
            old_img = self.draw_points(img.copy())
            self.redraw = False
        return old_img
        
    @staticmethod
    def mouse_cb(event, x, y, flags, param):
        """ param == self """
        if flags & cv2.EVENT_FLAG_LBUTTON:
            param.add_point(x, y)
    
    def setup(self, img):
        cv2.namedWindow(self.window_name)
        self.redraw = True
        draw_img = self.get_img_with_points(img, img)
        image = img.copy()  # we need this for brightness messing and whatnot
        cv2.imshow(self.window_name, draw_img)
        if self.points:
            print "Press 'y' to accept current points, any key to start over"
            key = cv2.waitKey(0) & 0xFF
            if key == ord('y'):
                print "Using loaded setup."
                cv2.destroyWindow(self.window_name)
                return
        
        self.points = []
        self.redraw = True
        cv2.setMouseCallback(self.window_name, self.mouse_cb, self)
        print "Press 'q' to finish placing points, 'b' to revert last point, '+' or '-' to adjust brightness"
        boost_brightness = 0  # just so we don't lose too many details and can recover if need be
        while(1):
            draw_img = self.get_img_with_points(image, draw_img)
            cv2.imshow(self.window_name, draw_img)
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break
            elif key == 27:
                print "Exiting"
                exit(0)
            elif key == ord('b'):
                self.remove_last_point()
            elif key == ord('+'):
                boost_brightness += 1
                image = img.copy()
                image = cv2.add(img, np.array([boost_brightness * 5.0]))
                self.redraw = True
            elif key == ord('-'):
                boost_brightness -= 1
                image = img.copy()
                image = cv2.add(img, np.array([boost_brightness * 5.0]))
                self.redraw = True
        self.process_points(img)
        cv2.destroyWindow(self.window_name)
        if not self.loaded:
            self.dump_to_file()
            
    def process_points(self, img):
        pass

class CropArena(CropFilter):
    def __init__(self, padding=(10, 10)):
        self.padding = padding
        self.top = None
        self.bot = None
        super(CropArena, self).__init__("Setup arena bounds", ['top', 'bot', 'padding'])
    
    def draw_points(self, img):
        if not self.points:
            return img
        if len(self.points) == 1:
            cv2.circle(img, tuple(self.points[0]), 2, (0, 255, 0), -1)
        for p1, p2 in zip(self.points[:-1], self.points[1:]):
            cv2.line(img, tuple(p1), tuple(p2), (0, 255, 0), 2)
        return img
    
    def _add_padding(self, wx, wy):
        px, py = self.padding
        self.top = (
            max(0, self.top[0] - px),
            max(0, self.top[1] - py)
        )
        self.bot = (
            min(wx, self.bot[0] + px),
            min(wy, self.bot[1] + py)
        )
    
    def process_points(self, img):
        assert self.points, "No points got out from the setup phase, what."
        h, w = img.shape[:2]
        
        self.top = (min(self.points, key=lambda a: a[0])[0], min(self.points, key=lambda a: a[1])[1])
        self.bot = (max(self.points, key=lambda a: a[0])[0], max(self.points, key=lambda a: a[1])[1])
        self._add_padding( w, h )
    
    def filter(self, img):
        return img[self.top[1]:self.bot[1], self.top[0]:self.bot[0]]
        
class CropZone(CropFilter):
    def __init__(self, x_padding=30, crop_filter=None):
        self.px = x_padding
        self.zones = []
        self.img_x_padding = None
        super(CropZone, self).__init__("Setup zone bounds", ['zones', 'px'])
        # must be reset from the actual filter if it exists
        self.img_x_padding = crop_filter.padding[0] if crop_filter else 10
        self.w = None
        
    def draw_points(self, img):
        h = img.shape[0]
        for x, _ in self.points:
            cv2.line(img, (x, 0), (x, h), (0, 255, 0), 2)
        return img
    
    def process_points(self, img):
        # width of the image
        w = img.shape[1]
        self.w = w
        # width of arena
        wx = w - 2 * self.img_x_padding
        self.zones = []
        # sort all points based on their X coordinate
        self.points.sort(key=lambda a: a[0])
        print self.points
        print self.get_zones()
        
        for s, e in self.get_zones():
            start = max(0, (s - self.img_x_padding - self.px)) / float(wx)
            end = min(w, (e - self.img_x_padding + self.px)) / float(wx)
            self.zones.append( (start, end) )
        print self.zones
        
    def filter(self, img):
        w = img.shape[1]
        
        self.w = w
        wx = w - 2 * self.img_x_padding
        retval = []
        for s, e in self.zones:
            start = int(s * wx)
            end = int(min(w, e * wx))
            # returns zone_img, top_left_point
            retval.append((img[:, start:end].copy(), (start, 0)))
        return retval

    def get_zones(self):
    
        wx = self.w - 2 * self.img_x_padding
        zones = zip([(self.img_x_padding,0)] + self.points, self.points + [(wx + self.img_x_padding,0)])
        zones = map(lambda a: (a[0][0], a[1][0]), zones)
        return zones