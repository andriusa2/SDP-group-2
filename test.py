from controller import Controller, TestController
import time
from math import pi

params = {
    'debug': True,
    'port': '/dev/ttyUSB0',  # linux (might be /dev/acm...)
    # 'port': 'COM3', # windows
}

def sleep(seconds):
    print("Sleeping {0:.2}s".format(seconds))
    time.sleep(seconds)

def blink_test():
    # just use default parameters
    tc = TestController(**params)
    # tc.consume_input()
    print("Trying to blink")
    tc.blink()
    sleep(40.)
    print("Blinking again")
    tc.blink()
    sleep(20.)
    print("done")

   
def move_test():
    c = Controller(**params)
    print("Turning by pi/2")
    c.turn(pi/2.0)
    sleep(5.)
    print("Turning by -pi/2")
    c.turn(-pi/2.0)
    sleep(5.)
    print("Trying kick")
    c.kick()
    sleep(5.)
    print("Trying go(4)")
    c.go(4.)
    sleep(5.)
    
def main():
    move_test()
    blink_test()
    