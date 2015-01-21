from math import pi

CLICKS_PER_CM = 1.0  # hm... we could probably count everything in robot turn units, if possible, but that is wheel/motor dependent.

def convert_distance(distance):
    """ Converts distance the robot needs to cover to spins of motor. """
    return distance * CLICKS_PER_CM
    
def convert_angle(radians):
    """ Maps given angle to [-pi;pi] range. """
    while radians > pi:
        radians -= pi
    while radians < -pi:
        radians += pi
    return radians