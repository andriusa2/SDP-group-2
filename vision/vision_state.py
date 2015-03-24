class VisionState(object):
    def __init__(self, zone_filter):
    
        self.zones = zone_filter.get_zones()
        ARENA_WIDTH = 212  # how many units
        scale = self.zones[-1][-1] - self.zones[0][0]
        scale = float(ARENA_WIDTH) / float(scale)
        
        self.robots = {
            0: _VisionObject(pixel_scale=scale, smooth_velocity=True),
            1: _VisionObject(pixel_scale=scale, smooth_velocity=True),
            2: _VisionObject(pixel_scale=scale, smooth_velocity=True),
            3: _VisionObject(pixel_scale=scale, smooth_velocity=True),
        }
        self.ball = _VisionObject(pixel_scale=scale, smooth_velocity=True)
    
    def add_robot_position(self, zone_id, frame_time, position):
        self.robots[zone_id].add_position(frame_time, position)
    
    def add_ball_position(self, frame_time, position):
        self.ball.add_position(frame_time, position)
        
    def add_robot_direction(self, zone_id, frame_time, direction):
        self.robots[zone_id].add_direction(frame_time, direction)
    
    def get_robot(self, zone_id):
        return self.robots[zone_id]
    
    def get_ball(self):
        return self.ball
    
    def __repr__(self):
        return "State(Robots:{0!r}, ball:{1!r})".format(self.robots, self.ball)
    

class _VisionObject(object):
    def __init__(self, pixel_scale=None, smooth_position=None, smooth_velocity=None, smooth_direction=None):
        self.position_history = []
        self.direction_history = []
        self.position_buffer = None
        self.smooth_position = smooth_position
        self.smooth_velocity = smooth_velocity
        self.smooth_direction = smooth_direction
        self.pixel_scale = pixel_scale
    
    def __repr__(self):
        return "Obj(Pos:{0!r}, Dir:{1!r}, Vel:{2!r})\n".format(self.get_position(), self.get_direction(), self.get_velocity())
    
    def set_scaling_factor(self, scale):
        self.pixel_scale = scale
    
    def get_position_units(self):
        assert self.pixel_scale, "No pixel scale specified"
        try:
            x, y = self.get_position()
            x *= self.pixel_scale
            y *= self.pixel_scale
            return x, y
        except Exception:
            return None

        
    def get_velocity_units(self):
        assert self.pixel_scale, "No pixel scale specified"
        try:
            x, y = self.get_velocity()
            x *= self.pixel_scale
            y *= self.pixel_scale
            return x, y
        except Exception:
            return None
    
    def get_direction_units(self):
        assert self.pixel_scale, "No pixel scale specified"
        try:
            x, y = self.get_direction()
            x *= self.pixel_scale
            y *= self.pixel_scale
            return x, y
        except Exception:
            return None
    
    def get_position(self, i=-1, smoothing=None):
        if not self.position_history:
            return None
        if smoothing is None:
            smoothing = True
        if not smoothing:
            return self.position_history[i]['pos']
        sz = 3
        pos = self.position_history[-sz+i:i] + [self.position_history[i]]
        x = map(lambda a: a['pos'][0], pos)
        y = map(lambda a: a['pos'][1], pos)
        
        t = map(lambda a: a['time'], pos)
        x = smooth(t, x, deriv=0)
        y = smooth(t, y, deriv=0)
        return float(x), float(y)
    
    def get_velocity(self):
        # don't even bother to calculate a velocity out of 1/2 points
        if len(self.position_history) < 3:
            return None
        if not self.smooth_velocity:
            a, b = self.position_history[-2:]
            dt = b['time'] - a['time']
            dx = b['pos'][0] - a['pos'][0]
            dy = b['pos'][1] - a['pos'][1]
            return dx/dt, dy/dt
        pos = [self.get_position(i) for i in range(-min(4, len(self.position_history)), 0, 1)]
        pos = [p['pos'] for p in self.position_history[-4:]]
        x = map(lambda a: a[0], pos)
        y = map(lambda a: a[1], pos)
        t = map(lambda a: a['time'], self.position_history[-4:])
        dx = smooth(t, x, deriv=1)
        dy = smooth(t, y, deriv=1)
        # small velocities don't really matter (0.1px/s is pathetic)
        dx = 0 if 0.1 > dx > -0.1 else dx
        dy = 0 if 0.1 > dy > -0.1 else dy
        return float(dx), float(dy)
    
    def get_direction(self):
        if not self.direction_history:
            return None
        if not self.smooth_direction:
            self.smooth_direction = self.direction_history[-1]['dir']
        else:
            # exponential filter
            x, y = self.smooth_direction
            nx, ny = self.direction_history[-1]['dir']
            sz = 0.5
            self.smooth_direction = sz*nx + (1 - sz)*x, sz * ny + (1 - sz) * y
        return self.smooth_direction
        
    def add_direction(self, frame_time, direction):
        self.direction_history.append({'time': frame_time, 'dir': direction})
    
    def add_position(self, frame_time, position, dbg=False):
        last_time = self.position_buffer['time'] if self.position_buffer else self.position_history[-1]['time'] if self.position_history else 0
        if self.position_buffer:
            # we have a pending position to be pushed to history
            # do sanity check
            x, y = self.position_buffer['pos']
            nx, ny = position
            dx, dy = x - nx, y - ny
            # distance between position and buffer position
            d = dx * dx + dy * dy
            # last known "good" position
            px, py = self.position_history[-1]['pos']
            # POS - LAST 
            dx, dy = px - x, py - y
            # distance between pos and last
            d1 = dx * dx + dy * dy
            if d1 < d:
                # we came back, reject intermediate position
                self.position_buffer = None
            else:
                self.position_history.append(self.position_buffer)
            
        if self.position_history:
            x, y = self.position_history[-1]['pos']
            nx, ny = position
            dx, dy = x - nx, y - ny
            dx, dy = dx * dx, dy * dy
            # if the actual distance changed by less than two pixels (NB square distance here!)
            if 0 < dx + dy < 4:
                position = x, y
            else:
                # some significant change happened
                self.position_buffer = {'time': frame_time, 'pos': (float(nx), float(ny))}
                return
        x, y = position
        self.position_history.append({'time': frame_time, 'pos': (float(x), float(y))})
        self.truncate()
    
    def dump_positions(self, filename):
        with open(filename, 'w') as f:
            f.write('time,px,py\n')
            for d in self.position_history:
                f.write('{0[time]},{0[pos][0]:.2f},{0[pos][1]:.2f}\n'.format(d))
    
    def truncate(self):
        while len(self.position_history) > 100:
            del self.position_history[0]
        while len(self.direction_history) > 100:
            del self.direction_history[0]
        
import numpy as np
import numpy.linalg
# Savitzky-Golay filtering 
# adapted from http://dsp.stackexchange.com/questions/9498/
def sg_filter(x, m, k=0):
    """
    x = Vector of sample times
    m = Order of the smoothing polynomial
    k = Which derivative
    """
    mid = len(x) / 2  
    x = np.array(x)
    a = x - x[mid]
    expa = lambda x: map(lambda i: i**x, a)    
    A = np.r_[map(expa, range(0,m+1))].transpose()
    Ai = np.linalg.pinv(A)

    return Ai[k]

def smooth(x, y, order=2, deriv=0):

    assert deriv <= order, "deriv must be <= order"
    assert len(x) == len(y), "both axes need to have same amount of pts"

    f = sg_filter(x, order, deriv)
    result = np.dot(f, y)

    if deriv > 1:
        result *= math.factorial(deriv)

    return float(result)
