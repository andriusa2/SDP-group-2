import datetime
import serial

from lib.math.util import convert_angle, get_duration
import numpy as np

angle_poly = np.poly1d([-0.1735, 0.279, 0])

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

    def establish_connection(self):
        self.comms = 1
        assert self.serial is None, "Serial connection is already established."
        try:
            self.serial = serial.Serial(self.port, self.rate, timeout=self.timeout)
        except Exception:
            print("No Arduino detected, dying!")
            self.comms = 0
            if not self.debug:
                raise

    def _write(self, string, retry=True):
        print("Trying to run command: '{0}'".format(string))
        if self.comms == 1:
            ret_msg = ''
            for _ in range(self.ack_tries if self.ack_tries else 1):
                if 'ACK' in ret_msg:
                    break
                self.serial.flushInput()  # if this breaks ACK - comment out
                self.serial.write(string)
                if not self.is_dummy and self.ack_tries != 0:
                    self.serial.flush()
                    ret_msg = self.serial.readline()
                    if ret_msg:
                        print "Got msg from upstream: '{0}'".format(ret_msg)
                    else:
                        print "Timed out while waiting for msg from upstream"
                else:
                    ret_msg = 'ACK'
            else:
                if retry:
                    print "Retrying connection"
                    self.serial.close()
                    self.serial = None
                    self.establish_connection()
                    self.serial.readline()
                    return self._write(string, retry=False)
                else:
                    raise Exception("No answer from UPSTREAM, something is wrong")
        elif not self.debug:
            raise Exception("No comm link established, but trying to send command.")


def scale_list(scale, l):
    return map(lambda a: scale * a, l)


class Controller(Arduino):
    """ Implements an interface for Arduino device. """

    ENDL = '\r\n'  # at least the lib believes so
    
    COMMANDS = {
        'kick': '{term}KICK {power:.2}{term}',
        'move': '{term}MOVE {lf} {lb} {rf} {rb}{term}',
        'run_engine': '{term}RUN_ENGINE {engine_id} {power:.2} {duration}{term}',
        'grab_open': '{term}OPEN {power:.2}{term}',
        'grab_close': '{term}CLOSE {power:.2}{term}',
        'stop': '{term}STOP{term}',
    }

    # NB not a real radius, just one that worked
    RADIUS = 5
    """ Radius of the robot, used to determine what distance should it cover when turning. """
    FWD = [1, 1, 1, 1]
    LEFT = [-1, 1, 1, -1]
    TURN = [1, 1, -1, -1]
    MAX_POWER = 1.
    """ Max speed of any engine. """

    def kick(self, power=None):
        if power is None:
            power = self.MAX_POWER
        self._write(self.COMMANDS['kick'].format(power=float(power), term=self.ENDL))
        return 0.4

    def move(self, x=None, y=None, power=None):
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
        assert x or y, "You need to supply some distance"
        assert not(x and y), "You can only supply distance in one axis"
        distance = x or y
        if distance < 0:
            duration = -get_duration(-distance, 1)
        else:
            duration = get_duration(distance, 1)
        assert -6000 < duration < 6000, 'Something looks wrong in the distance calc'

        return self.special_move(*scale_list(duration, self.FWD if x else self.LEFT))

    def go(self, duration):
        return self.special_move(*scale_list(duration, self.FWD))

    def stop(self):
        self._write(self.COMMANDS['stop'].format(term=self.ENDL))
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
        # print('Trying to turn for {0} seconds'.format(duration))
        return self.special_move(*scale_list(duration, self.TURN))

    def special_move(self, lf, lb, rf, rb):

        self._write(
            self.COMMANDS['move'].format(term=self.ENDL, **locals())
        )
        return max(map(abs, [lf, lb, rf, rb])) * 0.001 + 0.1  # typically motors lag for that much
        
    def run_engine(self, id, power, duration):
        assert (-1.0 <= power <= 1.0) and (0 <= id <= 5)
        command = self.COMMANDS['run_engine'].format(engine_id=int(id), power=float(power), duration=int(duration), term=self.ENDL)
        self._write(command)
        return float(duration) / 1000.0

    def grab(self, power=None):
        """ power is negative atm """
        if power is None:
            power = -self.MAX_POWER
        self._write(self.COMMANDS['grab_close'].format(power=float(power), term=self.ENDL))
        return 0.3
    
    def open_grabber(self, power=None):
        """ power is negative atm """
        if power is None:
            power = self.MAX_POWER
        self._write(self.COMMANDS['grab_open'].format(power=float(power), term=self.ENDL))
        return 0.3

    def close_grabber(self, power=None):
        if power is None:
            power = self.MAX_POWER
        self._write(self.COMMANDS['grab_close'].format(power=float(power), term=self.ENDL))
        return 0.3