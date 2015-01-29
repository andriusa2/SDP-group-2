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
        self.go(380, power=-1.0)  # TODO: test!
    
    def fwd_long(self):
        self.go(1500, power=-1.0)  # TODO: test!
        
    def bwd_short(self):
        self.go(560)
    
    def kick_goal(self):
        self.kick(0.48)
    
    def kick_pass(self):
        self.kick(0.48)  # maybe


def sam_main():
    m1 = ControllerM1("/dev/tty.usbmodem000001")

    # m1.fwd_short()
    # m1.fwd_long()
    # m1.bwd_short()

    # m1.kick_goal()
    m1.kick_pass()

if __name__ == '__main__':
    sam_main()

