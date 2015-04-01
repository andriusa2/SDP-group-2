from serial import Serial
import time
from multiprocessing import Process
import atexit


def serial_worker(port):
    s = Serial(port, timeout=0.1)
    while True:
        line = s.readline()
        if line:
            print line
        else:
            time.sleep(0.1)


class TestAir(object):
    def __init__(self, port='/dev/ttyACM0'):
        self.serial_thread = Process(target=serial_worker, args=(port,))
        self.serial_thread.start()
        atexit.register(self.destr)

    def destr(self):
        self.serial_thread.terminate()
        self.serial_thread.join()
