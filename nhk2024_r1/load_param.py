import os
import serial

class Param:
    MAX_ACC=9.8
    MAX_SPD=4.9
    MAX_ROT_SPD=90.0
    MAX_ACC_DEG=800
    WHEEL_RADIUS=37.45
    COM_SWD=6
    COM_KINECT=150
    COM_EM=4
    COM_LINE=50
    P_ROT_GAIN=12.0
    D_ROT_GAIN=1.8
    P_GAIN=0.045
    D_GAIN=0.0008
    ROT_OK_MAX_DIF=0.1
    WHEEL_THETA_0 = -30
    WHEEL_THETA_1 = 150
    WHEEL_THETA_2 = 270
    ser_swd = serial.Serial("COM"+str(COM_SWD), 115200, timeout=3)
    ser_em = serial.Serial("COM"+str(COM_EM), 115200, timeout=3)

    @classmethod
    def get_max_spd(self):
        return float(self.MAX_SPD)
    
    @classmethod
    def get_max_rot_spd(self):
        return float(self.MAX_ROT_SPD)
    
    @classmethod
    def get_max_acc(self):
        return float(self.MAX_ACC)
    
    @classmethod
    def get_max_acc_deg(self):
        return float(self.MAX_ACC_DEG)

    @classmethod
    def get_wheel_radius(self):
        return float(self.WHEEL_RADIUS)

    @classmethod
    def get_p_rot_gain(self):
        return float(self.P_ROT_GAIN)

    @classmethod
    def get_d_rot_gain(self):
        return float(self.D_ROT_GAIN)

    @classmethod
    def get_p_gain(self):
        return float(self.P_GAIN)

    @classmethod
    def get_d_gain(self):
        return float(self.D_GAIN)

    @classmethod
    def get_com_swd(self):
        return self.ser_swd

    @classmethod
    def get_com_em(self):
        return self.ser_em

    @classmethod
    def get_com_kinect(self):
        return int(self.COM_KINECT)

    @classmethod
    def get_com_line(self):
        return int(self.COM_LINE)
    
    @classmethod
    def get_rot_ok_max_dif(self):
        return float(self.ROT_OK_MAX_DIF)

    @classmethod
    def get_wheel_theta_0(self):
        return int(self.WHEEL_THETA_0)

    @classmethod
    def get_wheel_theta_1(self):
        return int(self.WHEEL_THETA_1)

    @classmethod
    def get_wheel_theta_2(self):
        return int(self.WHEEL_THETA_2)
