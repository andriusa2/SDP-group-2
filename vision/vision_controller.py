import itertools
import cv2
import time
from vision_trackers import plateTracker, ballTracker, TrackingException
from vision_filters import CropArena, CropZone
from vision_state import VisionState


class VisionController(object):
    def __init__(self, video_port=None, draw_debug=None, **kwargs):
        self.robots = {
            0: plateTracker(0),
            1: plateTracker(1),
            2: plateTracker(2),
            3: plateTracker(3),
        }
        # an iterable with any of 'pos', 'dir', 'vel'
        self.draw_debug = tuple() if not draw_debug else draw_debug
        self.try_these = [0, 1, 2, 3]
        self.zone_in_hits = {}
        self.ball = ballTracker
        
        self.crop_filters = [CropArena()]
        self.zone_filter = CropZone(crop_filter=self.crop_filters[0])
        self.capture = cv2.VideoCapture(video_port) if video_port is not None else None
        self.kwargs = kwargs
        self.demo = itertools.cycle([
            # cv2.imread("SideArena\sample{0}\{1:08}.png".format(kwargs.get('id', 1), i), 1) for i in range(1, 11)
            # cv2.imread("CentralArena\sample{0}\{1:08}.png".format(kwargs.get('id', 1), i), 1) for i in range(1, 11)
            cv2.imread("tmp2\{0:08}.jpg".format(i), 1) for i in range(1, 22)
            # cv2.imread("tmp1\{0:08}.png".format(i), 1) for i in range(1, 58)
            # cv2.imread("tmp\{0:08}.png".format(i), 1) for i in range(1, 97)
            # cv2.imread("tmp3\{0:08}.jpg".format(i), 1) for i in range(2, 6)
            # cv2.imread("tmp3\{0:08}.jpg".format(i), 1) for i in range(2, 14)
            # cv2.imread("tmp3\{0:08}.jpg".format(i), 1) for i in range(6, 10)
        ]) if video_port is None else []
        _ = self.get_frame()
        frame = self.get_frame()
        for f in self.crop_filters:
            f.setup(frame)
            f.dump_to_file()
            frame = f.filter(frame)
        self.zone_filter.setup(frame)
        self.zone_filter.dump_to_file()

    def get_frame(self):
        if self.capture:
            return self.capture.read()[1]
        else:
            # implement nicer file loading
            time.sleep(1.0/10.0)
            return next(self.demo)
    
    def analyse_frame(self, previous_state=None):
        frame = self.get_frame()
        frame_time = time.time()
        for c in self.crop_filters:
            frame = c.filter(frame)
        arenas = self.zone_filter.filter(frame)
        
        if not previous_state:
            previous_state = VisionState(self.zone_filter)
        # helps with ball recognition
        frame = cv2.GaussianBlur(frame,(3,3),0)
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        arenas_hsv = [(cv2.cvtColor(ar, cv2.COLOR_BGR2HSV), p) for ar, p in arenas]
        for i, (a_hsv, pos) in enumerate(arenas_hsv):
            #print "Tracking robot in {0} zone".format(i)
            if i not in self.try_these:
                #print "This zone is ignored"
                continue
            if self.zone_in_hits.get(i, 0):
                self.zone_in_hits[i] -= 1
                continue
            try:
                center, dot, tag = self.robots[i].find(
                    a_hsv,
                    origin=pos,
                    previous_center=previous_state.get_robot(i).get_position()
                )
                cx, cy = center
                cy = frame_hsv.shape[0] - cy
                center = cx, cy
            except TrackingException as e:
                print "{0} : Error in tracking:".format(i), e
                self.zone_in_hits[i] = 24
                continue
            previous_state.add_robot_position(i, frame_time, center)
            dx, dy = tag
            dx -= dot[0]
            dy -= dot[1]
            dy = -dy
            previous_state.add_robot_direction(i, frame_time, (dx, dy))
        try:
            if self.zone_in_hits.get('ball', 0):
                self.zone_in_hits['ball'] -= 1
                x = None
            else:
                (x, y), r = self.ball.find(frame_hsv, previous_center=previous_state.get_ball().get_position())
                y = frame_hsv.shape[0] - y
        except Exception as e:
            self.zone_in_hits['ball'] = 24
            print "Error in tracking:", e
        else:
            if x is not None:
                previous_state.add_ball_position(frame_time, (x, y), ignore_noise=False)
        
        self.draw_frame_details(frame, previous_state)
        return previous_state
        
    def draw_frame_details(self, frame, state):
        toint = lambda a: tuple(map(int, a))
        try:
            pos = state.get_ball().get_position(smoothing=False)
            px, py = pos
            py = frame.shape[0] - py
            pos = px, py
            vel = state.get_ball().get_velocity()
            vx, vy = vel
            vy = -vy
            vel = vx, vy
            if pos:
                # position
                cv2.circle(frame, toint(pos), 2, (0,255,0),-1)
            
            if vel:
                vx, vy = vel
                vx += pos[0]
                vy += pos[1]
                cv2.line(frame, toint(pos), toint((vx, vy)), (255,255,0),1)
            for i in self.robots.keys():
                pos = state.get_robot(i).get_position()
                px, py = pos
                py = frame.shape[0] - py
                pos = px, py
                dir = state.get_robot(i).get_direction()
                dx, dy = dir
                dy = -dy
                dir = dx, dy
                vel = state.get_robot(i).get_velocity()
                vx, vy = vel
                vy = -vy
                vel = vx, vy
                if pos and 'pos' in self.draw_debug:
                    # position
                    cv2.circle(frame, toint(pos), 2, (0,255,0),-1)
                if dir and 'dir' in self.draw_debug:
                    vx, vy = dir
                    vx *= 3
                    vy *= 3
                    vx += pos[0]
                    vy += pos[1]
                    cv2.line(frame, toint(pos), toint((vx, vy)), (0,255,0),2)
                if vel and 'vel' in self.draw_debug:
                    vx, vy = vel
                    vx += pos[0]
                    vy += pos[1]
                    cv2.line(frame, toint(pos), toint((vx, vy)), (255,255,0),1)
            
        except Exception:
            pass
        cv2.imshow("view", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            exit(0)
