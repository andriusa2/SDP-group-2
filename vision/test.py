import cv2
import numpy as np
ip = 0

def getPos(n):
    return cv2.getTrackbarPos(n, 'Things')
    
def setHSVsliders(h,s,v):
    H1, H2 = h
    S1, S2 = s
    V1, V2 = v
    cv2.setTrackbarPos('H1', 'Things', H1)
    cv2.setTrackbarPos('H2', 'Things', H2)
    cv2.setTrackbarPos('S2', 'Things', S2)
    cv2.setTrackbarPos('V2', 'Things', V2)
    cv2.setTrackbarPos('S1', 'Things', S1)
    cv2.setTrackbarPos('V1', 'Things', V1)
    
def denoiseMask(mask):
    kernel =  cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    po = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    po = cv2.morphologyEx(po, cv2.MORPH_OPEN, kernel)
    return po
    
def wrapInRange(hsv, lo, hi):
    h1,s1,v1 = lo
    h2,s2,v2 = hi
    return getInRange((h1,h2),(s1,s2),(v1,v2),hsv)
    
def getInRange(h, s, v, hsv):
    h1, h2 = h
    h1 = h1 % 360
    h2 = h2 % 360
    if h1 > 179:
        h1 -= 179
    if h2 > 179:
        h2 -= 179
    if h2 < h1:
        return cv2.bitwise_or(getInRange( (0, h2), s, v, hsv), getInRange( (h1, 179), s, v, hsv))
    s1, s2 = s
    v1, v2 = v
    return cv2.inRange(hsv, (h1, s1, v1), (h2, s2, v2))
    
def recalibrate(h,s,v, hsv, test_fun, h_bound=(0,179), target_val=10):
    # do a linear scan with 5 increments and whatever was the previous window size
    h1, h2 = h
    dh = 20
    h_m, h_max = h_bound
    values = dict()
    for dh in range(11, 20, 3):
        for h1 in range(h_m, h_max):
            h2 = h1 + dh
            m = denoiseMask(getInRange((h1,h2),s,v,hsv))
            val = test_fun(m)
            #print "{};{} -> {}".format(h1,h2,val)
            if val > 0:
                tg = int(np.abs(target_val - val))
                if tg == 0:
                    # early out as we have close match
                    return (h1, h2), s, v
                values[tg] = (h1, h2), s, v
                #print "Insert {}".format(int(np.abs(target_val - val)))
    if values:
        # select the closest approximation
        v = values[min(values.keys())]
        print "val deviation found {0}".format(min(values.keys()))
        return v
    s1,s2 = s
    if s1 >= s2:
        raise Exception("Couldn't properly find stuff")
    else:
        s1 += 25
        return recalibrate(h, (s1, s2), v, hsv, test_fun, h_bound, target_val)

def find_dot_size(mask, sz):
    s1, s2 = sz
    cnt, h = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    # lets assume that they should fit into the box of size s1..s2
    cnt = [c for c in cnt if 4*s2*s2 >= cv2.contourArea(c) >= 4*s1*s1]
    if not cnt:
        #print "no hits1"
        return (0,0), 0
    # find all candidates now
    cnt = [cv2.minEnclosingCircle(c) for c in cnt]
    cnt = [(pos, r) for pos, r in cnt if s2 >= r >= s1]
    if len(cnt) != 1:
        if cnt:
            print "multiple hits"
        else:
            print "no hits"
        return (0,0), 0
    return cnt[0]

import time
set_id = 0
paths = [
    "tmp",   
    r"SideArena\sample1",   # check things
    r"SideArena\sample2",
    r"SideArena\sample3",
    r"SideArena\sample4",
    "SideArena\sample5",
    "CentralArena\sample1","CentralArena\sample2","CentralArena\sample3","CentralArena\sample4",
    "CentralArena\sample5", # check things
]
images = [cv2.imread("{0}/{1:08}.png".format(paths[set_id], i), 1) for i in range(1, 11)]
#images = [cv2.imread("in{}.jpg".format(i), 1) for i in range(1, 4)]
from vision_trackers import ballTracker, RectTracker
ball = ballTracker
r_test = RectTracker("hodr", ((0,100),(0,100),(0,100)), (8, 19), 10, search_space=([],[],[]), manual_mode=True)

#ball = BallTracker()
class RobotAngleTester(object):
    def __init__(self):
        pass
        
    def get_angle(self, img, plate_box):
        # plate box must be a contour
        # find a dark-ish spot there
        pass
        
from vision_trackers import plateTracker
rect = [plateTracker(1), plateTracker(2), plateTracker(3),plateTracker(4)]

from vision_filters import CropZone, CropArena
c = CropArena()
c.setup(images[0])
a = CropZone(crop_filter=c)
a.setup(c.filter(images[0]))

"""c = CropFilter()
a = ArenaFilter(pad=c.padding[0])
c.setup(images[0])
a.setup(c, c.filter(images[0]))
"""
cv2.namedWindow("Things")

cv2.createTrackbar('H1', 'Things', 0, 199,lambda a: a)
cv2.createTrackbar('S1', 'Things', 0, 255,lambda a: a)
cv2.createTrackbar('V1', 'Things', 40, 255,lambda a: a)
cv2.createTrackbar('H2', 'Things', 0, 199,lambda a: a)
cv2.createTrackbar('S2', 'Things', 0, 255,lambda a: a)
cv2.createTrackbar('V2', 'Things', 0, 255,lambda a: a)

def getNeighbourhood(contour, image, padding=None):
    if padding is None:
        padding = (0, 0)
    px, py = padding
    print contour
    try:
        x, y, w, h = cv2.boundingRect(contour)
    except Exception:
        contour = np.array(map(lambda a: np.array([a]), contour))
        print contour
        x,y,w,h = cv2.boundingRect(contour)
    x = max(0, x - px)
    y = max(0, y - py)
    return image[y:y+h+2*py, x:x+w+2*px, :]
    
ball_pos = None
no_auto=False
rec_pos = {0: None, 1: None, 2: None, 3: None}
while(1):
     
    input = images[(ip / 10) % len(images)].copy()
    print (ip / 10) % len(images)
    input = c.filter(input)
    arenas = a.filter(input)
    
    input = cv2.GaussianBlur(input,(3,3),0)
    st = time.time()
    ip += 1
    low = np.array([
        getPos('H1'), getPos('S1'), getPos('V1')
    ])
    hi = np.array([getPos('H2'), getPos('S2'), getPos('V2')])
    #low,hi = arena
    hsv = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
    arenas = [(ar, p) for ar, p in arenas]
    arenas_hsv = [(cv2.cvtColor(ar, cv2.COLOR_BGR2HSV), p) for ar, p in arenas]
    
    try:
        (x,y), radius = ball.find(hsv, previous_center=ball_pos)
        ball_pos = x, y
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        (x,y), radius = ball.find(hsv)
    try:
        #r_test.find(hsv)
        pass
    except Exception:
        pass
    #print r_test.tgt
    #cv2.imshow("manual test", r_test.mask)
    if no_auto:
        ip -= 1
    #print "frame took {}s".format(time.time() - st)
    
    cv2.circle(input,(int(x),int(y)),2,(0,255,0),-1)
    rs = dict()
    for i, (a_hsv, pos) in enumerate(arenas_hsv):
        try:
            #print "{0}".format(i)
            #if i in (0, 1,  3): continue
            #if a_hsv is not None:
            #    print a_hsv.shape
            rs[i] = rect[i].find(a_hsv, origin=pos, previous_center=rec_pos[i])
            center, _, _, _ = rs[i]
            rec_pos[i] = center
        except Exception:
            raise
            print "{} failed to do stuff".format(i)
    for i, (center, d, dot, tag) in rs.items():
        cv2.circle(input, center, 2, (0, 255, 0), -1)
        cv2.circle(input, dot, 2, (0, 255, 0), -1)
        cv2.circle(input, tag, 2, (0, 255, 0), -1)
        vx, vy = tag
        vx -= dot[0]
        vy -= dot[1]
        cx, cy = center
        cx += vx * 3
        cy += vy * 3
        cv2.line(input, center, (cx, cy), (255,0,0), 1)
        #cv2.circle(arenas[i][0], center, 5, (0, 255, 0), -1, offset=(-arenas[i][1][0], arenas[i][1][1]))
    
    
    cv2.imshow("view", input)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    if key == ord('e'):
        path = paths[set_id]
        set_id += 1
        set_id %= len(paths)
        images = [cv2.imread("{}\{:08}.png".format(path, i), 1) for i in range(1, 11)]
        c.setup(images[0])
        a.setup(c.filter(images[0]))
    elif key == ord('m'):
        no_auto=not no_auto
    elif key == ord('n'):
        ip += 10
    elif key == ord('s'):
        print "dumping cropping data"
        c.dump_to_file('crop.json')
