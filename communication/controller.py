import serial
from multiprocessing import Value, Process, Pipe
import struct
import itertools
import time
import atexit
from lib.math.util import convert_angle, get_duration
import numpy as np

# polynomial approximating low angle durations
angle_poly = np.poly1d([-0.1735, 0.279, 0])
LOG_FILE = None


def log_write(msg, flush=False):
    msg_format = "[{time:.3f}] {msg}\n"
    msg = msg.replace('\r', '\\r').replace('\n', '\\n')
    LOG_FILE.write(msg_format.format(time=time.time(), msg=msg))
    LOG_FILE.flush()


def send_msg(s, msg, timeout, retries, ack):
    global LOG_FILE
    if not LOG_FILE:
        LOG_FILE = open("msg_log_{0}.log".format(int(time.time())), 'w+')
    buff = ''
    for i in range(retries):
        s.write(msg)
        log_write("Sending out '{0}' to arduino, retry {1}".format(msg, i))
        s.flush()
        start_time = time.time()
        end_time = time.time()
        while end_time - start_time < timeout:
            r = s.readline()
            log_write("Got back '{0}' from arduino, time left till timeout: {1:f}s".format(r, timeout - time.time() + start_time))
            buff += r
            if r:
                print 'Got msg "{0}" from upstream'.format(r)
                if 'FAIL' in r:
                    print 'Found failure condition in response, resending'
                    log_write("Matched failure condition, resending")
                    break

                if ack in buff:
                    print 'Found ACK condition in response, accepting'
                    log_write("Found ACK condition, accepting")
                    break
            end_time = time.time()
        if ack in buff:
            return True
    else:
        log_write("no msg was ack'd, giving up")
        return False


def ready_waiter(s, avail, timeout, retries=None):
    if avail.value == 1:
        return True
    if not retries:
        retries = 100  # big number till we give up on it
    if send_msg(s, '\t\t', timeout, retries, 'READY'):
        print 'Arduino seems to be ready'
        avail.value = 1
        return True
    print 'Arduino not ready :/'
    avail.value = 0
    return False


class MockSerial(object):
    def __init__(self, *args, **kwargs):
        self.buff = None

    def flush(self):
        pass

    def write(self, msg):
        self.buff = msg

    def readline(self):
        if not self.buff:
            return ''
        if self.buff.startswith('\t\t'):
            return 'READY\n'
        return 'ACK\n'


def msg_sender(pipe, avail, port, rate, timeout, retries):
    # establish serial connection
    s = serial.Serial(port, rate, timeout=timeout)
    #s = MockSerial(port, rate, timeout=timeout)
    print 'Established connection, commencing initial wait for handshakes(5s)'
    time.sleep(5)
    print 'Connection should be up now, testing with ready'
    if not ready_waiter(s, avail, timeout):
        print 'Arduino not ready, what is going on??'
        print 'waiting more'
        time.sleep(10)
        if not ready_waiter(s, avail, timeout):
            raise Exception("Arduino down for good")
    # we should be fine now
    while True:
        t, msg = pipe.recv()
        if 'HEARTBEAT' in msg:
            # special case, try to update avail value if it's not available
            if avail.value == 0:
                ready_waiter(s, avail, timeout, retries=10)
                if avail.value == 1:
                    avail.value = 0
                    time.sleep(1.0/10.0)
                    avail.value = 1
            continue
        if 'TERMINATE' in msg:
            print 'exitting...'
            return
        if time.time() - t > timeout * 4:
            print 'Got msg {0} which is {1:.2f}s old, rejecting'.format(msg, time.time() - t)
            log_write("Rejected msg '{0}' as it was {1:.2f}s old".format(msg, time.time() - t))
            continue
        print 'Trying to send msg "{0}"'.format(msg)

        if 'STOP' not in msg:
            ready_waiter(s, avail, timeout, retries=2)
            if avail.value == 0:
                print "Can't send msg to arduino as it is not available, try again"
                continue
        avail.value = 0
        if send_msg(s, msg, timeout, retries, 'ACK'):
            print 'msg properly sent to arduino'
            continue


class Arduino(object):
    """ Basic class for Arduino communications. """

    def __init__(self, port='/dev/ttyUSB0', rate=115200, timeOut=0.06, comms=1, debug=False, is_dummy=False,
                 ack_tries=4):
        self.port = port
        self.rate = rate
        self.timeout = timeOut
        self.is_dummy = is_dummy
        self.ack_tries = ack_tries
        self.available = Value('i', 0)
        self.serial_thread = None
        self.pipe = None
        self.establish_connection()
        self.avail_check = -1

    def establish_connection(self):
        pipe_in, pipe_out = Pipe()
        self.serial_thread = Process(target=msg_sender, args=(
        pipe_out, self.available, self.port, self.rate, self.timeout, self.ack_tries))
        self.serial_thread.start()
        atexit.register(self.destr)
        self.pipe = pipe_in

    def _write(self, string, important=False):
        # NB - the sender thread will try to check whether it can run it actually, so it should probably work
        print("Trying to run command: '{0}'".format(string))
        string += '\n'
        self.pipe.send((time.time(), string))

    def is_available(self):
        # if not available - query just in case
        if self.available.value == 0 and self.avail_check < time.time():
            self._write('HEARTBEAT')
            self.avail_check = time.time() + 0.1
        return self.available.value != 0

    def destr(self):
        self.pipe.send((time.time(), 'TERMINATE'))
        self.serial_thread.terminate()
        self.serial_thread.join()


def scale_list(scale, l):
    return map(lambda a: scale * a, l)

    
LAST_MSG = 0

class Controller(Arduino):
    """ Implements an interface for Arduino device. """

    COMMANDS = {
        'kick': '{ts}K{0}{1}{parity}{te}',
        'move_straight': '{ts}F{0}{1}{parity}{te}',
        'move_left': '{ts}L{0}{1}{parity}{te}',
        'move': '{ts}V{0}{1}{2}{3}{4}{5}{6}{7}{8}{te}',
        'turn': '{ts}T{0}{1}{parity}{te}',
        'run_engine': '{ts}R{0}{1}{2}{3}{te}',
        'grab_open': '{ts}O{0}{1}{parity}{te}',
        'grab_close': '{ts}C{0}{1}{parity}{te}',
        'stop': '{ts}S{0}{1}{parity}{te}',
    }

    # NB not a real radius, just one that worked
    RADIUS = 5
    """ Radius of the robot, used to determine what distance should it cover when turning. """
    FWD = [1, 1, 1, 1]
    LEFT = [-1, 1, 1, -1]
    TURN = [1, 1, -1, -1]
    MAX_POWER = 1.
    """ Max speed of any engine. """

    @staticmethod
    def get_command(cmd, *params):
        """
        Fills cmd with *params converted to byte-length fields.
        :param params: a list of parameters of form (value, struct.pack format).
        """
        bytes = []
        for param in params:
            try:
                v, fmt = param
            except TypeError:
                print 'get_command got parameter {0}, assuming that this needs to be a short'.format(param)
                v, fmt = param, 'h'
            v = int(v)
            # arduino is little endian!
            r = list(struct.pack('<' + fmt, v))
            bytes += r
            # print r
            # print struct.unpack('<h', ''.join(r))
        def xor_bytes(a, b):
            b = struct.unpack('B', b)[0]
            return a ^ b

        parity = reduce(xor_bytes, bytes, 0)
        parity = chr(parity)
        global LAST_MSG
        if LAST_MSG > 128:
            LAST_MSG = 0
        parity = chr(LAST_MSG)
        LAST_MSG += 1
        return cmd.format(*bytes, parity=parity, ts='\t', te='\t')

    def kick(self, power=None):
        if power is None:
            power = 1.0
        power = int(abs(power) * 255.)
        cmd = self.COMMANDS['kick']
        cmd = self.get_command(cmd, (abs(power), 'B'), (0, 'B'))  # uchar
        self._write(cmd)
        return 0.4

    def move(self, x=None, y=None, direction=None, power=None):
        """
        Moves robot for a given distance on a given axis.
        NB. currently doesn't support movements on both axes (i.e. one of x and y must be 0 or None)
        :param x: distance to move in x axis (+x is towards robot's shooting direction)
        :param y: distance to move in y axis (+y is 90' ccw from robot's shooting direction)
        :param power: deprecated
        :return: duration it will be blocked
        """
        print "attempting move ({0}, {1})".format(x, y)
        x = None if -0.01 < x < 0.01 else x
        y = None if -0.01 < y < 0.01 else y
        print "clamp move ({0}, {1})".format(x, y)

        if power is not None:
            print "I don't support different powers, defaulting to 1"
        try:
            assert x or y, "You need to supply some distance"
            assert not (x and y), "You can only supply distance in one axis"
        except Exception as e:
            print e
            return 0

        distance = x or y
        if distance < 0:
            duration = -get_duration(-distance, 1)
        else:
            duration = get_duration(distance, 1)
        try:
            assert -6000 < duration < 6000, 'Something looks wrong in the distance calc'
        except Exception as e:
            print e
            print "Calculated duration {duration}ms for distance {distance:.2f}".format(duration=duration,
                                                                                        distance=distance)
            return 0
        if x:
            cmd = self.COMMANDS['move_straight']
        else:
            cmd = self.COMMANDS['move_left']
        cmd = self.get_command(cmd, (duration, 'h'))  # short
        self._write(cmd)
        return duration * 0.001 + 0.07

    def go(self, duration):
        cmd = self.get_command(self.COMMANDS['move_straight'], (duration, 'h'))
        self._write(cmd)
        return duration * 0.001 + 0.07

    def stop(self):
        cmd = self.get_command(self.COMMANDS['stop'], (ord('T'), 'B'), (ord('O'), 'B'))
        self._write(cmd, important=True)
        return 0.01

    def turn(self, angle):
        """ Turns robot over 'angle' radians in place. """

        angle = convert_angle(-angle)  # so it's in [-pi;pi] range
        # if angle is positive move clockwise, otw just inverse it
        power = self.MAX_POWER if angle >= 0 else -self.MAX_POWER

        angle = abs(angle)
        if angle < 0.67:
            duration = int(angle_poly(angle) * 1000)
        else:
            # pi/2 -> 200, pi/4 -> 110
            # ax+b=y, api/2+b = 200, api/4+b=150, b=20, a=360/pi
            duration = int(360.0 / 3.14 * angle + 20.0)
        duration = -duration if power < 0 else duration
        print duration
        cmd = self.COMMANDS['turn']
        cmd = self.get_command(cmd, (duration, 'h'))  # short
        self._write(cmd)
        return duration * 0.001 + 0.07

    def special_move(self, lf, lb, rf, rb):
        cmd = self.COMMANDS['move']
        cmd = self.get_command(cmd, *zip((lf, lb, rf, rb), itertools.repeat('h')))
        self._write(cmd)
        return max(map(abs, [lf, lb, rf, rb])) * 0.001 + 0.1  # typically motors lag for that much

    def run_engine(self, id, power, duration):
        assert (-1.0 <= power <= 1.0) and (0 <= id <= 5) and abs(duration) <= 30000
        power = int(power * 127)
        cmd = self.COMMANDS['run_engine']
        cmd = self.get_command(cmd, (id, 'B'), (power, 'b'), (duration, 'h'))
        self._write(cmd)
        return float(duration) / 1000.0

    def grab(self, power=None):
        """ power is negative atm """
        if power is None:
            power = 1.0
        power = int(abs(power) * 255.0)
        cmd = self.COMMANDS['grab_close']
        cmd = self.get_command(cmd, (power, 'B'), (0, 'B'))
        self._write(cmd)
        return 0.3

    def open_grabber(self, power=None):
        """ power is negative atm """
        if power is None:
            power = 1.0
        power = int(abs(power) * 255.0)
        cmd = self.COMMANDS['grab_open']
        cmd = self.get_command(cmd, (power, 'B'), (0, 'B'))
        self._write(cmd)
        return 0.3

    def close_grabber(self, power=None):
        if power is None:
            power = self.MAX_POWER
        power = int(abs(power) * 255.0)
        cmd = self.COMMANDS['grab_close']
        cmd = self.get_command(cmd, (power, 'B'), (0, 'B'))
        self._write(cmd)
        return 0.3
