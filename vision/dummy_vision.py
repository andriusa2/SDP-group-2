__author__ = 'samdavies'


class DummyRobotModel(object):

    def __init__(self, x, y, angle, velocity):
        self.x = x
        self.y = y
        self.angle = angle
        self.velocity = velocity


class DummyBallModel(object):

    def __init__(self, x, y, velocity, angle, in_possession=False):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.angle = angle
        self.in_possession = in_possession