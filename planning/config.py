import numpy as np


class Config(object):

    ###################
    # Robot Constants #
    ###################

    GRAB_THRESHOLD = 6  # square grab area
    DIST_KICKER_ROBOT = 11
    ROBOT_WIDTH = 6
    SQUARE_ANGLE_THRESHOLD = 0.01
    MOVE_DAMPENING = 1
    TURN_DAMPENING = 0.5
    MAX_MOVE = 15
    MAX_TURN = np.pi/360

    ###################
    # World Constants #
    ###################

    ZONE_CENTRE_WIDTH = 16
    PITCH_HEIGHT = 110
    ZONE_CENTRE_OFFSET = 0.1  # a percentage of the zone width

class TestingConfig(Config):

    #####################
    # Testing Constants #
    #####################

    DIST_KICKER_ROBOT = 0
    MOVE_DAMPENING = 1
    TURN_DAMPENING = 1
    MAX_MOVE = 1000
    MAX_TURN = 2 * np.pi

    ZONE_CENTRE_OFFSET = 0.5
