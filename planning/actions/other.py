__author__ = 'Sam Davies'


class Other(object):

    def __int__(self, strategy):
        self.strategy = strategy

    def shoot(self):
        """
        We are facing the goal so just kick
        :return: duration that the motors are on
        """
        self.strategy.world.is_grabber_closed = False
        return self.strategy.actual_robot.kick(), "Kicking"  # kick

    def open_grabber(self):
        """
        opens the grabber arms
        :return: time it takes for the grabbers to open
        """
        self.strategy.world.is_grabber_closed = False
        return self.strategy.actual_robot.open_grabber(), "Kicking and opening grabber"

    def close_grabber(self):
        """
        closes the grabber in an attempt to collect the ball
        :return: time it takes for the grabbers to close
        """
        self.strategy.world.is_grabber_closed = True
        return self.strategy.actual_robot.close_grabber(), "Closing grabber"