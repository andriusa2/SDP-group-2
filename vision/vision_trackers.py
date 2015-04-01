import cv2
import numpy as np
import itertools
def denoiseMask(mask):
    kernel =  cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    po = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    po = cv2.morphologyEx(po, cv2.MORPH_OPEN, kernel)
    return po
    
def getInRange(h, s, v, hsv):
    """ Different order of parameters compared to cv2.inRange, also now exhibits proper ring behaviour. """
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
    
def getPointNeighbourhood(point, image, padding=None):
    if padding is None:
        padding = (10, 10)
    px, py = padding
    x, y = point
    h, w = image.shape[:2]
    wx = int(min(w, x + px))
    wy = int(min(h, y + py))
    x = int(max(0, x - px))
    y = int(max(0, y - py))
    return image[y:wy, x:wx, :], (x, y)

def myBoundingRect(cnt):
    x = np.min(cnt[:, :, 0])
    y = np.min(cnt[:, :, 1])
    tx = np.max(cnt[:, :, 0])
    ty = np.max(cnt[:, :, 1])
    return x, y, tx - x, ty - y

def getContourNeighbourhood(contour, image, padding=None):
    if padding is None:
        padding = (0, 0)
    px, py = padding
    try:
        x, y, w, h = myBoundingRect(contour)
    except Exception:
        contour = np.array(map(lambda a: np.array([a]), contour))
        x,y,w,h = myBoundingRect(contour)
    x = max(0, x - px)
    y = max(0, y - py)
    return image[y:y+h+2*py, x:x+w+2*px, :], (x, y)

class TrackingException(Exception):
    pass

    
class Tracker(object):
    def __init__(self, name, tgt, sz_range, sz_target, search_space, ch_width_range=None, manual_mode=None):
        self.tgt = tgt  # NB: initial tgt doesn't get to history until it matches something
        self.history = []
        self.sz_range = sz_range
        self.sz_target = sz_target
        self.hsv_ranges = search_space
        self.width = ch_width_range if ch_width_range else (range(11, 20, 3), (255, ), (255, ))
        self.manual_mode = manual_mode
        self.name = str(name)
        self.mask = None
        self.recalibrated = False
        
    def _find_element(self, mask, dbg=None, local_hit=None):
        raise NotImplementedError
        
    def _hit_fitness(self, hit):
        raise NotImplementedError
    
    def _single_hit(self, hsv, dbg=None, mask=None, local_hit=None):
        h, s, v = self.tgt
        mask_ = denoiseMask(getInRange(h, s, v, hsv))
        if mask is not None:
            mask_ = cv2.bitwise_and(mask_, 255, mask=mask)
        hit = self._find_element(mask_, dbg=dbg, local_hit=local_hit)
        
        if hit:
            self.tgt = h, s, v
            if self.tgt not in self.history:
                self.history.append(self.tgt)
                if len(self.history) > 5:
                    del self.history[0]  # prune at this place now
            elif self.tgt != self.history[-1]:
                self.history.remove(self.tgt)
                self.history.append(self.tgt)
            return hit
        else:
            raise TrackingException
    
    def _adjust_hit(self, hit, origin):
        raise NotImplementedError
    
    def my_print(self, *args):
        print self.name, ">> ", 
        for a in args:
            print a, 
        print 
    
    def _get_local_area(self, hsv, origin, previous_center):
        raise NotImplementedError
    
    def find(self, hsv, origin=None, previous_center=None, dbg=None, mask=None, local_hit=False):
        """ tries to find an object which matches whatever is the test. """
        self.recalibrated = False
        if previous_center:
            local, top_left = self._get_local_area(hsv, origin=origin, previous_center=previous_center)
            
            if mask is not None:
                mask_, _ = self._get_local_area(mask, origin=origin, previous_center=previous_center)
            else:
                mask_ = None
            ret = None
            if dbg:
                cv2.imshow("local view", cv2.cvtColor(local, cv2.COLOR_HSV2BGR))
                if mask_ is not None:
                    cv2.imshow("local mask", mask_)
                if cv2.waitKey(0) & 0xFF == 27:
                    exit(0)
                cv2.destroyWindow("local view")
                if mask_ is not None:
                    cv2.destroyWindow("local mask")
            try:
                ret = self.find(local, previous_center=None, origin=top_left, dbg=dbg, mask=mask_, local_hit=True)
            except TrackingException:
                pass
            else:
                if ret:
                    if origin:
                        ret = self._adjust_hit(ret, origin)
                    return ret
                else:
                    self.my_print("Fail in neighb, we global search now")
        # nothing in the neighbourhood, try out current tgt and historical values
        # before recalibration cycle
        if dbg:
            cv2.imshow("HSV_channel", cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
            
        for h, s, v in itertools.chain([self.tgt], reversed(self.history)):
            self.tgt = h, s, v
            try:
                hit = self._single_hit(hsv, dbg=dbg, mask=mask, local_hit=local_hit)
                if origin:
                    hit = self._adjust_hit(hit, origin)
                return hit
            except TrackingException:
                continue
            
        else:
            if local_hit:
                raise TrackingException
            # need to recalibrate now
            if not self.manual_mode:
                self.recalibrate(hsv, mask=mask)
            
            hit = self._single_hit(hsv, dbg=dbg, mask=mask)
                
            if origin:
                hit = self._adjust_hit(hit, origin)
            return hit

    def recalibrate(self, hsv, mask=None):
        self.recalibrated = True
        values = dict()
        h, s, v = self.hsv_ranges
        dh, ds, dv = self.width
        hs = [(h1, h1 + d) for h1 in h for d in dh]
        ss = [(s1, min(255, s1 + d)) for s1 in s for d in ds]
        vs = [(v1, min(v1 + d, 255)) for v1 in v for d in dv]
        self.my_print("Recalibration will use: ", len(hs) * len(ss) * len(vs), " values")
        for v1, v2 in vs:
            for s1, s2 in ss:
                for h1, h2 in hs:
                    self.tgt = (h1, h2), (s1, s2), (v1, v2)
                    try:
                        hit = self._single_hit(hsv, mask=mask, dbg=False)
                    except TrackingException:
                        continue
                    val = self._hit_fitness(hit)
                    if val == 0:
                        self.my_print("early out")
                        return
                    values[val] = self.tgt
        if values:
            self.tgt = values[min(values.keys())]
            self.my_print("val deviation found {0}".format(min(values.keys())))
            return
            
        self.my_print("Failed to recalibrate")
        self.my_print(self.history)
        raise TrackingException
        
        
class CircleTracker(Tracker):
    def __init__(self, name, tgt, sz_range, sz_target, search_space, ch_width_range=None, manual_mode=None, circle_fit=0.4):
        super(CircleTracker, self).__init__(name, tgt, sz_range, sz_target, search_space, ch_width_range, manual_mode)
        self.circle_fit = circle_fit

    def _find_element(self, mask, dbg=None, local_hit=None):
        try:
            c1, c2 = self.circle_fit
        except Exception:
            c1 = c2 = self.circle_fit
        if local_hit:
            circle_fit = c2
        else:
            circle_fit = c1
        s1, s2 = self.sz_range
        if dbg:
            cv2.imshow("Circle mask", mask)
            self.my_print('Current HSV ranges', self.tgt)
            self.my_print('Last few tried HSV ranges', self.history)
            if cv2.waitKey(0) & 0xFF == 27:
                exit(0)
            cv2.destroyWindow("Circle mask")
        cnt, h = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if dbg:
            m1 = mask.copy()
            cv2.drawContours(m1, cnt, -1, 255, 2)
            cv2.imshow("Contours", m1)
            if cv2.waitKey(0) & 0xFF == 27:
                exit(0)
            cv2.destroyWindow("Contours")
        
        cnt = [(c, cv2.minEnclosingCircle(c)) for c in cnt]
        if dbg:
            for c, p in cnt:
                self.my_print('-' * 10)
                self.my_print('Cnt area:', cv2.contourArea(c))
                self.my_print('Min enclosing circle:', p)
                self.my_print('-' * 10)
        cnt = [c for c, (_, r) in cnt if s2 >= r >= s1]

        def test(c):
            _, r = cv2.minEnclosingCircle(c)
            c_area = np.pi * r ** 2
            cnt_area = cv2.contourArea(c)
            if dbg:
                self.my_print( 'circle_area', c_area)
                self.my_print( 'contour area', cnt_area)
                self.my_print( 'ratio cnt/circle', float(cnt_area) / float(c_area))
            return float(cnt_area) / float(c_area)
        cnt = [ (test(c), c) for c in cnt]
        # fullest circle is the first one
        cnt = [(t, c) for t, c in cnt if t > circle_fit]

        cnt.sort(key=lambda a: a[0] * cv2.contourArea(a[1]), reverse=True)
        if not cnt:
            if dbg:
                self.my_print("no hits after ecc test")
            raise TrackingException("No circle hits after box test")

        if dbg:
            for t, c in cnt:
                self.my_print('-' * 10)
                self.my_print('Fitness:', t)
                self.my_print('Adjusted fitness:', t * cv2.contourArea(c))
                self.my_print('Cnt area:', cv2.contourArea(c))
                self.my_print('Min enclosing circle:', cv2.minEnclosingCircle(c))
                self.my_print('-' * 10)
            cv2.drawContours(mask, map(lambda a: a[1], cnt), -1, 255, 2)
            cv2.imshow("Contours filtered", mask)
            if cv2.waitKey(0) & 0xFF == 27:
                exit(0)
            cv2.destroyWindow("Contours filtered")
        cnt = map(lambda a: a[1], cnt)
        # find candidates
        cnt = [cv2.minEnclosingCircle(c) for c in cnt]
        cnt = [(pos, r) for pos, r in cnt if s2 >= r >= s1]
        if len(cnt) != 1:
            if not cnt:
                self.my_print("No hits after refine")
                raise TrackingException("No circle hits after refining")
            # self.my_print("Too many hits")
            # self.my_print(cnt)
            # pick the biggest fill if one exists
            return cnt[0]
        p, r = cnt[0]
        return p, r
    
    def _get_local_area(self, hsv, origin, previous_center):
        if origin:
            x, y = previous_center
            ox, oy = origin
            previous_center = x - ox, y - oy
        # do things with neighbourhood at first
        return getPointNeighbourhood(
            previous_center,
            hsv,
            padding=(self.sz_target * 3, self.sz_target * 3)  # not a great assumption tbh.
        )
    
    def _hit_fitness(self, hit):
        _, r = hit
        return int(r - self.sz_target) ** 2  # casting to ints as that helps a wee bit
        
    def _adjust_hit(self, hit, origin):
        (x, y), r = hit
        ox, oy = origin
        return (x + ox, y + oy), r
        
ballTracker = CircleTracker(
    name="BallTracker",
    tgt=((160, 185), (100, 255), (40, 255)),
    sz_range=(2, 12),
    sz_target=7.5,
    search_space=(range(160, 175, 7), range(70, 200, 50), range(40, 200, 60)),
    ch_width_range=(range(11, 20, 5), (255,), (255,)),
    circle_fit=(0.4, 0.2)
)


class RectTracker(Tracker):
    """
    finds clusters which fit into a given rectangle
    """
    def __filter_correct(self, cnt):
        s1, s2 = self.sz_range
        return [((p, (w, h), a), c) for (p, (w, h), a), c in cnt if s2 >= w >= s1 and s2 >= h >= s1]
    
    def _postprocess_hit(self, hit):
        (_, (w, h), _), cnt = hit
        return self.get_centroid(cnt), (w, h)
    
    def _get_local_area(self, hsv, origin, previous_center):
        if origin:
            x, y = previous_center
            ox, oy = origin
            previous_center = x - ox, y - oy
        # do things with neighbourhood at first
        return getPointNeighbourhood(
            previous_center,
            hsv,
            padding=(self.sz_target[0], self.sz_target[1])  # not a great assumption tbh.
        )
        
    def _find_element(self, mask, dbg=None, local_hit=None):
        s1, s2 = self.sz_range
        if dbg:
            self.my_print(self.tgt)
            cv2.imshow("rect mask", mask)
            if cv2.waitKey(0) & 0xFF == 27:
                exit(0)
            cv2.destroyWindow("rect mask")
          
        cnt, h = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
        if dbg:
            self.my_print(self.tgt)
            cv2.drawContours(mask, cnt, -1, 255, 1)
            cv2.imshow("rect mask", mask)
            if cv2.waitKey(0) & 0xFF == 27:
                exit(0)
            cv2.destroyWindow("rect mask")
        cnt = [(cv2.minAreaRect(c), c) for c in cnt]
        
        if dbg:
            self.my_print(cnt)
        cnt = self.__filter_correct(cnt)
        
        if dbg:
            self.my_print(cnt)
        if len(cnt) != 1:
            if not cnt:
                if dbg:
                    self.my_print("No rects")
                raise TrackingException("No rect hits after refining")
            # self.my_print("too many rects")

            def get_box_fitness(box):
                _, (w, h), _ = box
                x, y = self.sz_target
                return (w * h - x * y) ** 2
            # self.my_print(map(lambda a: get_box_fitness(a[0]), cnt))
            # approximate thing, CARE
            cnt.sort(key=lambda a: get_box_fitness(a[0]))

            for _, c in cnt if dbg else []:
                msk = np.zeros(mask.shape)
                cv2.drawContours(msk, [c], -1, 255, 1)
                cv2.imshow("cnt mask", msk)
                if cv2.waitKey(0) & 0xFF == 27:
                    exit(0)
                cv2.destroyWindow("cnt mask")

            # raise TrackingException("Too many rect hits")
        return self._postprocess_hit(cnt[0])
    
    def _hit_fitness(self, hit):
        _, (w, h) = hit
        x, y = self.sz_target 
        return int((w * h) - x * y) ** 2
    
    def _adjust_hit(self, hit, origin):
        (x, y), d = hit
        ox, oy = origin
        return (x + ox, y + oy), d
        
    def get_centroid(self, cnt):
        M = cv2.moments(cnt)
        return float(M['m10']/M['m00']), float(M['m01']/M['m00'])


class PlateTracker(Tracker):
    """
    Major differences from RectTracker:
    - acceps "split" rectangles (so two contours, which could form a fitting rect)
    - tester searches for color indicator and black dot
    - centroid is WRT indicator and black dot, not the plate
    - gets angle out
    """
    def __init__(self, preferred_tag=None, **kwargs):
        self.ytag_tracker = RectTracker(
            name=''.join([str(kwargs['name']), "-ytag"]),
            tgt=((10, 25), (160, 255), (65, 255)),  # NB - yellow
            sz_range=(4, 20),
            sz_target=(5, 15),
            search_space=(range(10, 20, 4), range(70, 200, 50), (65, )),  # no range, SHOULD work
            ch_width_range=(range(5, 15, 5), (255,), (255,))
        )
        self.btag_tracker = RectTracker(
            name=''.join([str(kwargs['name']), "-btag"]),
            tgt=((70, 100), (0, 255), (65, 255)),  # NB - blue
            sz_range=(4, 20),
            sz_target=(5, 15),
            search_space=(range(55, 90, 10), (0, ), (65, )),
            ch_width_range=((30, ), (255,), (255,))
        )
        self.dot_tracker = CircleTracker(
            name=''.join([str(kwargs['name']), "-dot"]),
            tgt=((24, 90), (0, 255), (0, 70)),
            sz_range=(2, 7),
            sz_target=5,
            search_space=((24, ), (0, ), (0, )),
            ch_width_range=((66,), (255,), range(40, 130, 10))
        )
        self.tag_order = (self.btag_tracker, self.ytag_tracker) if preferred_tag == 'b' else (self.ytag_tracker, self.btag_tracker)
        self.ordered = False
        self.hsv = None
        self.circle_bound = 2.4
        super(PlateTracker, self).__init__(**kwargs)
        
    def find(self, hsv, origin=None, previous_center=None, dbg=None, mask=None, local_hit=False):
        """ Cheating here, but helps to keep interfaces a wee bit cleaner. """
        prev_hsv = self.hsv
        self.hsv = hsv
        try:
            r = super(PlateTracker, self).find(hsv, origin=origin, previous_center=previous_center, dbg=False, mask=mask, local_hit=local_hit)
        finally:
            self.hsv = prev_hsv
        return r
    
    def __filter_correct(self, cnt):
        s1, s2 = self.sz_range
        # size test
        cnt = [((p, (w, h), a), c) for (p, (w, h), a), c in cnt if s2 >= w >= s1 and s2 >= h >= s1]
        # dot test
        retval = []
        for box, c in cnt:
            tgt_hsv, _ = getContourNeighbourhood(c, self.hsv)
            mask = np.zeros(tgt_hsv.shape[:2], dtype=np.int8)
            cv2.circle(mask, (tgt_hsv.shape[1]/2, tgt_hsv.shape[0]/2), int(min(mask.shape[:2])/self.circle_bound), 255, -1)

            try:
                self.dot_tracker.find(tgt_hsv, dbg=False, mask=mask)
            except TrackingException:
                self.my_print("failed with dot")
                continue
            # self.my_print("found dot")
            retval.append((box, c)) 
        
        return retval
        
    def _postprocess_hit(self, hit):
        (_, (w, h), _), cnt = hit
        plate_hsv, top = getContourNeighbourhood(cnt, self.hsv)
        mask = np.zeros(plate_hsv.shape[:2], dtype=np.int8)
        cv2.circle(mask, (plate_hsv.shape[1]/2, plate_hsv.shape[0]/2), int(min(mask.shape[:2])/self.circle_bound), 255, -1)
            
        (dx, dy), dr = self.dot_tracker.find(plate_hsv, origin=top, mask=mask, dbg=False)
        reorder = False
        tags = zip(self.tag_order, (False, True))
        for tag, r in tags:
            try:
                ((tx, ty), _), reorder = tag.find(plate_hsv, dbg=False, origin=top, mask=mask), r
                break
            except TrackingException:
                continue
        else:
            self.my_print("Failed with tags")
            raise TrackingException("No tag found")
        if reorder:
            self.my_print("reordering tags")
            self.tag_order = self.tag_order[1], self.tag_order[0]
        self.ordered = True
        cx = tx * 2 / 3 + dx / 3
        cy = ty * 2 / 3 + dy / 3
        return (cx, cy), (dx, dy), (tx, ty)
    
    def _find_element(self, mask, dbg=None, local_hit=None):
        s1, s2 = self.sz_range
        if dbg:
            cv2.imshow("muh mask", mask)
            cv2.waitKey()
            cv2.destroyWindow("muh mask")
        cnt, h = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnt = [(cv2.minAreaRect(c), c) for c in cnt]
        # we might want to keep some smaller hits too and group them if no proper one is present
        cnt = [((p, (w, h), a), c) for (p, (w, h), a), c in cnt if s2 >= w > s1/3 and s2 >= h > s1/3]
        cnt_full = self.__filter_correct(cnt)
        if not cnt_full and len(cnt) > 1:
            # no full hits. Pick some 2-permutation of leftovers
            # boxpoints does not really return a valid contour, just a pointset, convert to contour

            cnt = [(cv2.minAreaRect(np.append(a, b, axis=0)), np.append(a, b, axis=0)) for (_, a), (_, b) in itertools.combinations(cnt, 2)]
            # self.my_print("Partial rect sz: {0}".format(len(cnt_full)))
            # okay, now there might
            try:
                cnt = self.__filter_correct(cnt)
                # self.my_print("Partial rect hits: {0}".format(len(cnt_full)))
            except TrackingException:
                raise
        else:
            # self.my_print("Full rect hits: {0}".format(len(cnt_full)))
            cnt = cnt_full
        if len(cnt) != 1:
            if not cnt:
                raise TrackingException("No rect hits after refining")

            raise TrackingException("Too many rect hits")
        return self._postprocess_hit(cnt[0])
    
    def _hit_fitness(self, hit):
        return 0  # it should be structurally sound now, __filter_correct doesn't let wrong structures in
    
    def _get_local_area(self, hsv, origin, previous_center):
        if origin:
            x, y = previous_center
            ox, oy = origin
            previous_center = x - ox, y - oy
        return getPointNeighbourhood(
            previous_center,
            hsv,
            padding=(self.sz_target, self.sz_target)  # not a great assumption tbh.
        )

    def _adjust_hit(self, hit, origin):
        (x, y), (dx, dy), (tx, ty) = hit
        ox, oy = origin
        return (x + ox, y + oy), (dx + ox, dy + oy), (tx + ox, ty + oy)
        
plateTracker = lambda a: PlateTracker(
    name=a,
    tgt=((70, 80), (200, 255), (56, 255)),
    sz_range=(27, 45),
    sz_target=31,
    search_space=(range(42, 75, 10), range(50, 150, 25), range(50, 150, 25)),
    ch_width_range=(range(19, 55, 10), (255,), (255,))
)
