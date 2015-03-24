__author__ = 'Sam Davies'


class Other(object):

    def __int__(self, strategy):
        self.strategy = strategy

    def shoot(self):
        """
        We are facing the goal so just kick
        :return: duration that the motors are on
        """
        self.strategy.world.is_grabber_down = False
        return self.strategy.actual_robot.kick(), "Kicking"  # kick

    def raise_cage(self):
        """
        opens the grabber arms
        :return: time it takes for the grabbers to open
        """
        self.strategy.world.is_grabber_down = False
        return self.strategy.actual_robot.kick(), "Kicking and opening grabber"

    def lower_cage(self):
        """
        closes the grabber in an attempt to collect the ball
        :return: time it takes for the grabbers to close
        """
        self.strategy.world.is_grabber_down = True
        return self.strategy.actual_robot.grab(), "Closing grabber"