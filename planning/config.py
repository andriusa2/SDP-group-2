import numpy as np


class Config(object):

    ###################
    # Robot Constants #
    ###################

    GRAB_THRESHOLD = 8  # square grab area
    DIST_KICKER_ROBOT = 12
    ROBOT_WIDTH = 4
    SQUARE_ANGLE_THRESHOLD = 0.005
    MOVE_DAMPENING = 0.9
    TURN_DAMPENING = 0.9
    MAX_MOVE = 15
    MAX_TURN = np.pi/4

    ###################
    # World Constants #
    ###################

    ZONE_CENTRE_WIDTH = 8
    PITCH_HEIGHT = 110
    ZONE_CENTRE_OFFSET = 0.5  # a percentage of the zone width
    DEAD_ZONE_WIDTH = 4
    DEAD_CORNER_WIDTH_HEIGHT = [27.0, 14.0]


class TestingConfig(Config):

    #####################
    # Testing Constants #
    #####################

    DIST_KICKER_ROBOT = 0
    MOVE_DAMPENING = 1
    TURN_DAMPENING = 1
    MAX_MOVE = 1000
    MAX_TURN = 2 * np.pi

    DEAD_ZONE_WIDTH = 0
    DEAD_CORNER_WIDTH_HEIGHT = [0, 0]