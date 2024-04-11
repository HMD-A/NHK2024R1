import time
from .load_param import *
from libs.md03 import comsendA

class Emerg:
    is_sleep = 1
    ser = Param.get_com_em()
    is_sleep = 0
    thread_stop = False
        
    
    @classmethod
    def emergencyThread(self):
        while self.thread_stop == False:
            if self.is_sleep == 0:
                send1 = [0x80]
                send2 = [0x7f]
                comsendA(self.ser, send1)
                comsendA(self.ser, send2)
            time.sleep(0.01)

    @classmethod
    def threadStop(self):
        self.thread_stop = True

    @classmethod
    def emergency(self):
        self.is_sleep = 1
        time.sleep(0.1)
        self.threadStop()
        #wsclose()
        exit(0)
