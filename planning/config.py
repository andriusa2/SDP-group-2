import numpy as np


class Config(object):

    ###################
    # Robot Constants #
    ###################

    GRAB_THRESHOLD = 8  # round grab area
    DIST_KICKER_ROBOT = 12
    ROBOT_WIDTH = 5

    SQUARE_ANGLE_THRESHOLD = 0.005
    MOVE_DAMPENING = 0.7
    TURN_DAMPENING = 0.4

    MAX_MOVE = 15
    MAX_TURN = np.pi/4

    BALL_VELOCITY_GRABBER_TRIGGER = 20
    BALL_DISTANCE_GRABBER_TRIGGER = 2

    ###################
    # World Constants #
    ###################

    ZONE_CENTRE_WIDTH = 8
    PITCH_HEIGHT = 110
    ZONE_CENTRE_OFFSET = -0.1  # a percentage of the zone width


class TestingConfig(Config):

    #####################
    # Testing Constants #
    #####################

    DIST_KICKER_ROBOT = 0
    MOVE_DAMPENING = 1
    TURN_DAMPENING = 1
    MAX_MOVE = 1000
    MAX_TURN = 2 * np.pi
    BALL_VELOCITY_GRABBER_TRIGGER = 10
    BALL_DISTANCE_GRABBER_TRIGGER = 1

    ZONE_CENTRE_OFFSET = 0.5
