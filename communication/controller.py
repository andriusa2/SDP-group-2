import serial
from multiprocessing import Value, Process
import struct
import itertools
import time

from lib.math.util import convert_angle, get_duration
import numpy as np

# polynomial approximating low angle durations
angle_poly = np.poly1d([-0.1735, 0.279, 0])


def msg_resender(s, msg, avail, timeout, retries):
    if not retries:
        retries = 30

    avail.value = 0  # set as unavailable now
    retval = True
    for i in range(retries):
        print 'Attempt {0}'.format(i)
        if s:
            s.write(msg)
            s.flush()

        start_time = time.time()
        end_time = time.time()
        r = ''
        buff = ''
        while end_time - start_time < timeout:
            if s:
                r = s.readline()
            else:
                time.sleep(timeout)
            buff += r
            if r:
                print 'msg from upstream: {0}'.format(r)
                if 'FAIL' in r:
                    print "Found FAIL, resending"
                    break
                if 'ACK' in buff:
                    break
            end_time = time.time()
        if 'ACK' in buff:
            break
    else:
        retval = False
    if retval:
        print 'Got ack for msg, waiting for ready now'
    else:
        print 'No ack for msg, waiting for ready now'
    if not Arduino.ready_waiter(s, avail, retries):
        return False
    return retval


class Arduino(object):
    """ Basic class for Arduino communications. """
    
    def __init__(self, port='/dev/ttyUSB0', rate=115200, timeOut=0.2, comms=1, debug=False, is_dummy=False, ack_tries=4):
        self.serial = None
        self.comms = comms
        self.port = port
        self.rate = rate
        self.timeout = timeOut
        self.debug = debug
        self.establish_connection()
        self.is_dummy = is_dummy
        self.ack_tries = ack_tries
        self.available = Value('i', 0)
        self.processes = []

    @staticmethod
    def ready_waiter(s, avail, retries=None):
        if not retries:
            retries = 255  # big number till we give up on it
        buff = ''
        for _ in range(retries):
            if avail.value != 0:
                break
            # empty message will trigger READY response if available
            if s:
                s.write('{0}{1}'.format('\t', chr(0)))
                s.flush()
                r = s.readline()
            else:
                r = 'READY'

            buff += r
            if r:
                print 'msg from upstream: {0}'.format(r)
                if 'READY' in buff:
                    print 'Arduino seems to be ready'
                    avail.value = 1
            else:
                print 'no msg from upstream :['
        else:
            return False
        return True

    def establish_connection(self):
        self.comms = 1
        assert self.serial is None, "Serial connection is already established."
        try:
            self.serial = serial.Serial(self.port, self.rate, timeout=self.timeout)
            # wait till it's actually ready
            if not self.ready_waiter(self.serial, self.available):
                raise Exception("Not ready...")
        except Exception:
            print("No Arduino detected, dying!")
            self.comms = 0
            if not self.debug:
                raise

    def maintain_processes(self):
        self.processes = [p for p in self.processes if p.is_alive()]

    def _write(self, string, important=False):
        print("Trying to run command: '{0}'".format(string))
        if not self.is_available() and not important:
            print "Available flag is set to {0}, can't send a message".format(self.available.value)
            return
        self.maintain_processes()
        if len(self.processes) > 0 and not important:
            print "There are some things happening already, failing"
            return
        if self.comms != 1 and not self.debug:
            raise Exception("No comm link established.")
        if important:
            # BAD BAD BAD
            for p in self.processes:
                p.terminate()
            self.processes = []
        self.available.value = 0
        self.processes.append(
            Process(target=msg_resender, args=(self.serial, string, self.available, self.timeout, self.ack_tries))
        )
        self.processes[-1].start()

    def is_available(self):
        return self.available.value != 0


def scale_list(scale, l):
    return map(lambda a: scale * a, l)


class Controller(Arduino):
    """ Implements an interface for Arduino device. """

    COMMANDS = {
        'kick': '{ts}K{0}0{parity}{te}',
        'move_straight': '{ts}F{0}{1}{parity}{te}',
        'move_left': '{ts}L{0}{1}{parity}{te}',
        'move': '{ts}V{0}{1}{2}{3}{4}{5}{6}{7}{8}{te}',
        'turn': '{ts}T{0}{1}{parity}{te}',
        'run_engine': '{ts}R{0}{1}{2}{3}{te}',
        'grab_open': '{ts}O{0}0{parity}{te}',
        'grab_close': '{ts}C{0}0{parity}{te}',
        'stop': '{ts}STOP{te}',
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
            bytes += list(struct.pack('<' + fmt, v))

        def xor_bytes(a, b):
            b = struct.unpack('B', b)[0]
            return a ^ b

        parity = reduce(xor_bytes, bytes, 0)
        parity = chr(parity)
        return cmd.format(*bytes, parity=parity, ts=chr(0), te=chr(0))

    def kick(self, power=None):
        if power is None:
            power = self.MAX_POWER
        if abs(power) < 1.0:
            power = int(power * 255.)
        cmd = self.COMMANDS['kick']
        cmd = self.get_command(cmd, (abs(power), 'B'))  # uchar
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
            assert not(x and y), "You can only supply distance in one axis"
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
            print "Calculated duration {duration}ms for distance {distance:.2f}".format(duration=duration, distance=distance)
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
        self._write(self.COMMANDS['stop'].format(ts=chr(0), te=chr(0)), important=True)
        return 0.01

    def turn(self, angle):
        """ Turns robot over 'angle' radians in place. """
        
        angle = convert_angle(angle)  # so it's in [-pi;pi] range
        # if angle is positive move clockwise, otw just inverse it
        power = self.MAX_POWER if angle >= 0 else -self.MAX_POWER

        angle = abs(angle)
        if angle < 0.67:
            duration = int(angle_poly(angle) * 1000)
        else:
            # pi/2 -> 200, pi/4 -> 110
            # ax+b=y, api/2+b = 200, api/4+b=150, b=20, a=360/pi
            duration = int(360.0/3.14 * angle + 20.0)
        duration = -duration if power < 0 else duration
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
        cmd = self.get_command(cmd, (power, 'B'))
        self._write(cmd)
        return 0.3
    
    def open_grabber(self, power=None):
        """ power is negative atm """
        if power is None:
            power = 1.0
        power = int(abs(power) * 255.0)
        cmd = self.COMMANDS['grab_open']
        cmd = self.get_command(cmd, (power, 'B'))
        self._write(cmd)
        return 0.3

    def close_grabber(self, power=None):
        if power is None:
            power = self.MAX_POWER
        power = int(abs(power) * 255.0)
        cmd = self.COMMANDS['grab_close']
        cmd = self.get_command(cmd, (power, 'B'))
        self._write(cmd)
        return 0.3