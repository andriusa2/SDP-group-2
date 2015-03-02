import datetime
import serial

from lib.math.util import convert_angle, get_duration


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
            
            
class Controller(Arduino):
    """ Implements an interface for Arduino device. """
    
    # TODO: get signs on turning right. Depends on wiring. :/
    ENDL = '\r\n'  # at least the lib believes so
    
    COMMANDS = {
        'kick': 'KICK {term}',
        'move': 'MOVE {left_power:.5} {right_power:.5} {left_duration} {right_duration}{term}',
        'run_engine': 'RUN_ENGINE {engine_id} {power:.5} {duration}{term}',
        'grab': 'GRAB{term}',
        'stop': 'STOP{term}',
    }

    # NB not a real radius, just one that worked
    RADIUS = 7.2
    """ Radius of the robot, used to determine what distance should it cover when turning. """
    
    MAX_POWER = 1.
    """ Max speed of any engine. """

    def kick(self, power=None):
        if power is None:
            power = self.MAX_POWER
        self._write(self.COMMANDS['kick'].format(power=float(power), term=self.ENDL))
        return 0.6

    def move(self, distance, power=None):
        if power is not None:
            print "I don't support different powers, defaulting to 1"
        power = 1
        if distance < 0:
            duration = get_duration(-distance, 1)
            power = -1
        else:
            duration = get_duration(distance, 1)
        assert 0 < duration < 6000, 'Something looks wrong in the distance calc'
        return self.go(duration, power)

    def stop(self):
        self._write(self.COMMANDS['stop'].format(term=self.ENDL))
        return 0.01

    def turn(self, angle):
        """ Turns robot over 'angle' radians in place. """
        angle = convert_angle(angle)  # so it's in [-pi;pi] range
        # if angle is positive move clockwise, otw just inverse it
        power = self.MAX_POWER if angle >= 0 else -self.MAX_POWER
        
        angle = abs(angle)
        distance = angle * self.RADIUS
        duration = get_duration(distance, abs(power))  # magic...
        # print('Trying to turn for {0} seconds'.format(duration))
        return self.complex_movement(
            left_power=power,
            right_power=power,
            left_duration=duration
        )

    def go(self, duration, power=None):
        """ Makes robot go in a straight line for a given duration. """
        if power is None:
            power = self.MAX_POWER
        return self.complex_movement(
            left_power=-min(power, self.MAX_POWER),
            right_power=power,  # might need this if the second motor is "inversed"
            left_duration=duration
        )
    
    def complex_movement(self, left_power, left_duration, right_power=None, right_duration=None):
        """ Moves robot with given parameters, if "right" aren't given, will copy over "left". """
        def fix_pair(power, duration):
            """ Helper for making sure everything is nice and in correct units. """
            # positive durations
            if duration < 0:
                power *= -1.0
                duration *= -1.0
            power = min(max(power, -self.MAX_POWER), self.MAX_POWER)
            return float(power), int(duration)
            
        assert (left_power is not None) and (left_duration is not None)
        
        if right_power is None:
            right_power = left_power
        if right_duration is None:
            right_duration = left_duration

        left_power, left_duration = fix_pair(left_power, left_duration)
        right_power, right_duration = fix_pair(right_power, right_duration)
        assert 0 <= left_duration <= 6000, "Wrong left duration"
        assert 0 <= right_duration <= 6000, "Wrong right duration"
        #self.stop()
        command = self.COMMANDS['move'].format(term=self.ENDL, **locals())
        self._write(command)
        wait_time = float(max(left_duration, right_duration)) / 1000.0 + 0.3
        # print("waiting " + str(wait_time) + " for motors")
        return wait_time
        
    def run_engine(self, id, power, duration):
        assert (-1.0 <= power <= 1.0) and (0 <= id <= 5)
        command = self.COMMANDS['run_engine'].format(engine_id=int(id), power=float(power), duration=int(duration), term=self.ENDL)
        self._write(command)
        return float(duration) / 1000.0

    def grab(self, power=None):
        """ power is negative atm """
        if power is None:
            power = -self.MAX_POWER
        self._write(self.COMMANDS['grab'].format(power=float(power), term=self.ENDL))
        return 0.3
    
    def open_grabber(self, power=None):
        return self.grab(power)
