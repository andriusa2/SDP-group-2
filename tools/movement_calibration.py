from communication.controller import Controller
from vision.vision_controller import VisionController
from math import sqrt
import time
import json
from multiprocessing import Value, Process
import atexit

def vc_worker(my_zone, px, py):
    # init vision
    vc = VisionController(0, draw_debug=('pos', 'dir'))
    vc.try_these = [my_zone] if my_zone is not None else [1]
    state = None
    while True:
        state = vc.analyse_frame(state)
        try:
            x, y = state.get_robot(vc.try_these[0]).get_position_units()
            px.value = x
            py.value = y
        except Exception as e:
            print e


def avg(l):
    if not l:
        return 0
    return sum(l) / len(l)


class MovementCalibration(object):
    def __init__(self, my_zone=None, port='/dev/ttyACM0'):
        self.px = Value('f', -1)
        self.py = Value('f', -1)
        self.vc_thread = Process(target=vc_worker, args=(my_zone, self.px, self.py))
        self.vc_thread.start()
        atexit.register(self.destr)
        self.c = Controller(port)
        self.dist_points = {}
        self.turn_points = {}
        
    def destr(self):
        self.vc_thread.terminate()
        self.vc_thread.join()
        
    def try_move(self, duration):
        # will block till the action is done and for .3s afterwards for vision to settle down
        while not self.c.is_available():
            print 'Arduino not available, waiting 300ms'
            time.sleep(0.3)
        # SHOULD BE AVAILABLE NOW
        self.c.go(duration)
        while not self.c.is_available():
            print 'Arduino not available, waiting 300ms'
            time.sleep(0.3)
        time.sleep(1)
        
    
    def get_dist(self, duration):
        # will try to calculate distance moved over duration
        px, py = self.px.value, self.py.value
        self.try_move(duration)
        ex, ey = self.px.value, self.py.value
        print 'Moved from {0:.2f};{1:.2f} to {2:.2f};{3:.2f}'.format(px, py, ex, ey)
        return sqrt((px - ex) ** 2 + (py - ey) ** 2)
    
    def sample_dist(self, duration):
        pts = []
        for _ in range(4):
            print 'Trying duration {0}'.format(duration)
            pts.append(self.get_dist(duration))
            duration *= -1
        # pick avg duration
        print 'Duration: ', abs(duration)
        print 'Distances: ', pts
        print 'avg: ', avg(pts)
        return avg(pts)
        
    def gather_points(self, start_duration=10, end_duration=500):
        while self.px.value < 0:
            print 'Vision not picking up position, waiting 300ms'
            time.sleep(0.3)
            
        for duration in range(start_duration, end_duration, (end_duration - start_duration) / 30):
            print 'Trying out duration ', duration
            dist = self.sample_dist(duration)
            print '{0}ms -> {1:.2f}cm'.format(duration, dist)
            self.dist_points[duration] = dist
        with open('dist_points.json', 'w') as f:
            json.dump(self.dist_points, f)
    