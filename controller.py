import serial

from util import convert_distance, convert_angle

class Arduino(object):
    """ Basic class for Arduino communications. """
    
    def __init__(self, port='/dev/ttyUSB0', rate=115200, timeOut=1, comms=1, debug=False):
        self.serial = None
        self.comms = comms
        self.port = port
        self.rate = rate
        self.timeout = timeOut
        self.debug = debug
        self.establish_connection()

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

    def _write(self, string):
        print("Trying to run command: '{0}'".format(string));
        if self.comms == 1:
            self.serial.write(string)
        elif not self.debug:
            raise Exception("No comm link established, but trying to send command.")

            
class TestController(Arduino):
    def blink(self):
        self._write("A_BLINK\n");
            
            
class Controller(Arduino):
    """ Implements an interface for Arduino device. """
    
    # TODO: get signs on turning right. Depends on wiring. :/
    ENDL = '\r'  # at least the lib believes so
    
    COMMANDS = {
        'kick': 'A_KICK{term}',
        'move': 'A_SET_MOVE {left_speed:.5} {right_speed:.5}{term}A_RUN_MOVE {left_dist:.5} {right_dist:.5}{term}',
        'set_engine': 'A_SET_ENGINE {engine_id} {speed:.5}{term}',
        'run_engine': 'A_RUN_ENGINE {engine_id} {dist:.5}{term}',
    }
    
    RADIUS = 1.
    """ Radius of the robot, used to determine what distance should it cover when turning. """
    
    MAX_SPEED = 1.
    """ Max speed of any engine. """
    
    def kick(self):
        self._write(self.COMMANDS['kick'].format(term=self.ENDL));
        
    def turn(self, angle):
        """ Turns robot over 'angle' radians in place. """
        angle = convert_angle(angle)  # so it's in [-pi;pi] range
        # if angle is positive move clockwise, otw just inverse it
        speed = self.MAX_SPEED if angle >= 0 else -self.MAX_SPEED
        
        angle = abs(angle)
        distance = angle * self.RADIUS
        
        self.complex_movement(
            left_speed=speed,
            right_speed=-speed,
            left_dist=distance
        )
    
    def go(self, distance):
        """ Makes robot go in a straight line for a distance. """
        self.complex_movement(
            left_speed=self.MAX_SPEED,
            # right_speed=-speed,  # might need this if the second motor is "inversed"
            left_dist=distance
        )
    
    def complex_movement(self, left_speed, left_dist, right_speed=None, right_dist=None):
        """ Moves robot with given parameters, if "right" aren't given, will copy over "left". """
        def fix_pair(speed, dist):
            """ Helper for making sure everything is nice and in correct units. """
            # positive distances
            if dist < 0:
                speed *= -1.0
                dist *= -1.0
            dist = convert_distance(dist)
            speed = min(max(speed, -self.MAX_SPEED), self.MAX_SPEED)
            return speed, dist
            
        assert (left_speed is not None) and (left_dist is not None)
        
        if right_speed is None:
            right_speed = left_speed
        if right_dist is None:
            right_dist = left_dist
        
        left_speed, left_dist = fix_pair(left_speed, left_dist)
        right_speed, right_dist = fix_pair(right_speed, right_dist)
        command = self.COMMANDS['move'].format(term=self.ENDL, **locals())
        self._write(command)
