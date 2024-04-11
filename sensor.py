import math
import time
import serial


class ReadGyro:

    ls1 = ls2 = ls3 = 0
    gyro_deg_g=0.0
    sense_new = 0
    enc1_g = enc2_g = 0.0
    thread_stop = False

    @classmethod
    def getGyro(self):
        return self.gyro_deg_g
    
    @classmethod
    def getEnX(self):
        return self.enc1_g
    
    @classmethod
    def getEnY(self):
        return self.enc2_g
    
    @classmethod
    def threadStop(self):
        self.thread_stop = True
    
    @classmethod
    def readSensorThread(self):
        self.ser = serial.Serial("COM"+str(4), 115200, timeout=3)
        byte = 0
        degr = 0
        byte = 0
        sum = 0
        degr_diff = 0
        degr_old = 0
        enc_diff = 0
        enc1cnt = 0
        enc2cnt = 0
        enc1pre = 0
        enc2pre = 0
        pot1rec = pot2rec = 0
        isFirst = True

        while(True):
            if self.ser.in_waiting > 0:
                data = int.from_bytes(self.ser.read(1), byteorder="big")

                if(( data & 0x80 ) != 0):
                    byte = 1
                    degr = (data & 0x7F) << 4
                    sum = data & 0x7F

                elif byte == 1 :
                    degr |= (data >> 3)
                    degr *= -1
                    self.ls1 = ((data >> 2) & 1)
                    self.ls2 = ((data >> 1) & 1)
                    self.ls2 = (data & 1)
                    sum += data
                    byte += 1

                elif byte == 2 :
                    enc1cnt |= data << 7
                    sum += data
                    byte += 1

                elif byte == 3 :
                    enc1cnt |= data
                    sum += data
                    byte += 1

                elif byte == 4 :
                    enc2cnt = data << 7
                    sum += data
                    byte += 1

                elif byte == 5 :
                    enc2cnt |= data
                    sum += data
                    byte += 1

                elif byte == 6 :
                    if (sum & 0x7f) == data :
                        if(isFirst):
                            degr_diff = 0
                        else:
                            degr_diff = degr - degr_old
                        degr_old = degr
                        if (degr_diff < -0x3FF):
                            degr_diff += 0x7FF
                        if (degr_diff > 0x3FF):
                            degr_diff -= 0x7FF
                        self.gyro_deg_g += degr_diff / 16.0

                        # エンコーダ数値処理
                        # ENC1
                        if (isFirst == 1):
                            enc_diff = 0
                        else:
                            enc_diff = enc1cnt - enc1pre
                        enc1pre = enc1cnt
                        if (enc_diff < -8192):
                            enc_diff += 0x3FFF
                        if (enc_diff > 8192):
                            enc_diff -= 0x3FFF
                        self.enc1_g -= 6.0 * math.pi * enc_diff / 400

                        # ENC2
                        if (isFirst == 1):
                            enc_diff = 0
                        else:
                            enc_diff = enc2cnt - enc2pre
                        enc2pre = enc2cnt
                        if (enc_diff < -8192):
                            enc_diff += 0x3FFF
                        if (enc_diff > 8192):
                            enc_diff -= 0x3FFF
                        self.enc2_g += 6.0 * math.pi * enc_diff / 400

                        isFirst = False
                        byte = 0

                        print(self.gyro_deg_g)
                    else :
                        byte = 0
            else:
                time.sleep(0.01)

RG = ReadGyro()
while(True):
    RG.readSensorThread()

