from controller import Controller

"""
10cm fwd
50cm fwd
20cm bwd
kick to goal
kick to pass
"""

class ControllerM1(Controller):
    def fwd_short(self):
        self.go(1000)  # TODO: test!
    
    def fwd_long(self):
        self.go(5000)  # TODO: test!
        
    def bwd_short(self):
        self.go(2000, power=-1.0)
    
    def kick_goal(self):
        self.kick()
    
    def kick_pass(self):
        self.kick(0.1)  # maybe
