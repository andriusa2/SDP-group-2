from math import pi

CLICKS_PER_CM = 1.0  # hm...


def get_duration(distance, power):
    """ Calculates how long does a bot need to move at power to cover distance. """
    return distance / power  * CLICKS_PER_CM


def convert_angle(radians):
    """ Maps given angle to [-pi;pi] range. """
    while radians > pi:
        radians -= pi
    while radians < -pi:
        radians += pi
    return radians