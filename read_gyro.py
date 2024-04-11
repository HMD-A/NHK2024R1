import math
import time
import serial

class ReadGyro:

    pot1vol = 0
    pot2vol = 0
    ls1 = 0
    ls2 = 0
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
        self.ser = serial.Serial("COM"+str(7), 115200, timeout=3)
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
                data = int.from_bytes(self.ser.read(1),byteorder="big")
                print(data)

                if(( data & 0x80 ) != 0):
                    byte = 1
                    degr = data & 0x7F
                    sum = data & 0x7F

                elif byte == 1 :
                    degr |= data << 7
                    degr *= -1
                    sum += data
                    byte += 1

                elif byte == 2 :
                    enc1cnt = data
                    sum += data
                    byte += 1

                elif byte == 3 :
                    enc1cnt |= data << 7 
                    sum += data
                    byte += 1

                elif byte == 4 :
                    enc2cnt = data
                    sum += data
                    byte += 1

                elif byte == 5 :
                    enc2cnt |= data << 7 
                    sum += data
                    byte += 1

                elif byte == 6 :
                    pot1rec = data
                    sum += data
                    byte += 1

                elif byte == 7 :
                    pot1rec |= (data & 0x1F) << 7
                    self.ls1 = (data & 0x20) >> 5
                    self.ls2 = (data & 0x40) >> 6
                    sum += data
                    byte += 1

                elif byte == 8 :
                    pot2rec = data
                    sum += data
                    byte += 1

                elif byte == 9 :
                    pot2rec |= data << 7
                    sum += data
                    byte += 1

                elif byte == 10 :
                    if (sum & 0x7f) == data :
                        # ポテンショメーター
                        self.pot1vol = pot1rec
                        self.pot2vol = pot2rec

                        if(isFirst):
                            degr_diff = 0
                        else:
                            degr_diff = degr - degr_old
                        degr_old = degr
                        if (degr_diff < -180 * 16):
                            degr_diff += 360 * 16
                        if (degr_diff > 180 * 16):
                            degr_diff -= 360 * 16
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

                        #print(self.gyro_deg_g)
                    else :
                        byte = 0
            else:
                time.sleep(0.01)

RG = ReadGyro()
while(True):
    RG.readSensorThread()

