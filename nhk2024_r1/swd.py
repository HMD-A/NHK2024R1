from .load_param import * 
from .read_gyro import *
from libs.md03 import *
import math

class SWD:
    # cm/s
    vx =  vy = rot = 0.0
    vx_g = vy_g = 0.0

    # rad/s/s
    deg_goal_g = 0.0

    MAX_SPD = Param.get_max_spd()
    count = 0
    p_gain = 0.008
    d_gain = 0.05
    arm_lift = 0
    arm_open = 0

    @classmethod
    def swdV(self, vx_, vy_, deg, arm_lift = 0, arm_open = 0):
        self.deg_goal_g = deg
        #print(vx_,vy_,deg)
        
        if (vx_ * vx_ + vy_ * vy_) > (self.MAX_SPD * self.MAX_SPD) :
            rate = self.MAX_SPD / math.sqrt(vx_ * vx_ + vy_ * vy_)
            vx_ *= rate
            vy_ *= rate
        
        # m/s→cm/s
        self.vx_g = vx_ * 100
        self.vy_g = vy_ * 100
        self.arm_lift = arm_lift*200
        self.arm_open = arm_open

    @classmethod
    def gain(self,a,b,c,d):
        self.d_gain += a*0.001
        self.d_gain -= b*0.001
        self.p_gain += c*0.001
        self.p_gain -= d*0.001
        #print(self.p_gain,self.d_gain)

    @classmethod
    def thread_swd(self, a,b,c,d,e):
        vx0 = vx1 = vx2 = vx3 = vy0 = vy1 = vy2 = vy3 = 0.0
        v0 = v1 = v2 = v3 = 0.0
        dv1 = dv2 = 0.0

        dvx = dvy = drot = 0.0

        rot_g = 0.0

        #cm
        wheel_r = 5.1
        frame_r = 24.65

        deg_goal_g_for_timer = math.degrees(self.deg_goal_g)


        #now_deg_gはジャイロから得た値を代入
        now_deg_g = ReadGyro.getGyro()
        print(now_deg_g,end="")
        ##   print(now_deg_g,end="")

        while (deg_goal_g_for_timer - now_deg_g) > 180:
            deg_goal_g_for_timer -= 360
        while (deg_goal_g_for_timer - now_deg_g) < -180:
            deg_goal_g_for_timer += 360
        #print(now_deg_g)

        # ここに角度制御埋め込む
        if 1 :
            #pd制御で決定される角速度
            rot_g = (deg_goal_g_for_timer - now_deg_g) * self.p_gain - self.rot * self.d_gain
            #print(rot_g)

            MAX_ROT_SPD = Param.get_max_rot_spd()
            if rot_g > MAX_ROT_SPD:
                rot_g = MAX_ROT_SPD

            if rot_g < -1*MAX_ROT_SPD:
                rot_g = -1*MAX_ROT_SPD

            ROT_OK_MAX_DIFF = Param.get_rot_ok_max_dif()

            #角度が許容誤差内だったら角速度を0に
            if (math.fabs(deg_goal_g_for_timer - now_deg_g) < ROT_OK_MAX_DIFF):
                rot_g = 0


        #コントローラーの接続が切れた時1に
        if 0 :
            self.vx_g = 0
            self.vy_g = 0
            dvx = -self.vx
            dvy = -self.vy
            drot = -self.rot
        else:
            #vx_gがコントローラからの値,vxが前回の指令値
            dvx = self.vx_g - self.vx
            dvy = self.vy_g - self.vy
            drot = rot_g - self.rot

        # 加速度制限
        # m/s^2で100fpsでcm/sなので 100/100=1倍
        dv = math.sqrt(dvx * dvx + dvy * dvy)

        MAX_ACC = Param.get_max_acc()

        if dv > MAX_ACC * 1 :
            dvx = dvx * MAX_ACC * 1 / dv
            dvy = dvy * MAX_ACC * 1 / dv

        MAX_ACC_DEG = Param.get_max_acc_deg()
        # drot/0.01で制御周期で割ることで角加速度に
        if drot > MAX_ACC_DEG / 100 :
            drot = MAX_ACC_DEG / 100
        if drot < -MAX_ACC_DEG / 100:
            drot = -MAX_ACC_DEG / 100

        self.vx += dvx
        self.vy += dvy
        self.rot += drot

        WHEEL_THETA_0 = Param.get_wheel_theta_0()
        WHEEL_THETA_1 = Param.get_wheel_theta_1()
        WHEEL_THETA_2 = Param.get_wheel_theta_2()

        '''
        v0 = 1 / wheel_r * ( -1 * math.sin(math.radians(now_deg_g + WHEEL_THETA_0))*math.cos(math.radians(now_deg_g))*(self.vx)+math.cos(math.radians(now_deg_g + WHEEL_THETA_0))*math.cos(math.radians(now_deg_g))*(self.vy)+frame_r*self.rot)
        v1 = 1 / wheel_r * ( -1 * math.sin(math.radians(now_deg_g + WHEEL_THETA_1))*math.cos(math.radians(now_deg_g))*(self.vx)+math.cos(math.radians(now_deg_g + WHEEL_THETA_1))*math.cos(math.radians(now_deg_g))*(self.vy)+frame_r*self.rot)
        v2 = 1 / wheel_r * ( -1 * math.sin(math.radians(now_deg_g + WHEEL_THETA_2))*math.cos(math.radians(now_deg_g))*(self.vx)+math.cos(math.radians(now_deg_g + WHEEL_THETA_2))*math.cos(math.radians(now_deg_g))*(self.vy)+frame_r*self.rot)
        '''

        v0 = 1 / wheel_r * ( -1 * math.sin(math.radians(now_deg_g + WHEEL_THETA_0))*(self.vx)+math.cos(math.radians(now_deg_g + WHEEL_THETA_0))*(self.vy)+frame_r*self.rot)
        v1 = 1 / wheel_r * ( -1 * math.sin(math.radians(now_deg_g + WHEEL_THETA_1))*(self.vx)+math.cos(math.radians(now_deg_g + WHEEL_THETA_1))*(self.vy)+frame_r*self.rot)
        v2 = 1 / wheel_r * ( -1 * math.sin(math.radians(now_deg_g + WHEEL_THETA_2))*(self.vx)+math.cos(math.radians(now_deg_g + WHEEL_THETA_2))*(self.vy)+frame_r*self.rot)
        
        
        wv_max = math.fabs(v0)
        if wv_max < math.fabs(v1):
            wv_max = math.fabs(v1)
        if wv_max < math.fabs(v2):
            wv_max = math.fabs(v2)

        if (wv_max > self.MAX_SPD * 100):
            v0 *= self.MAX_SPD * 100 / wv_max
            v1 *= self.MAX_SPD * 100 / wv_max
            v2 *= self.MAX_SPD * 100 / wv_max


        #if で分岐させることでコンパイルするかしないかを分岐 if 1と書けばコンパイルされるので
        if 0 :
            self.count += 1
            if self.count > 10:
                self.count = 0
                print(self.p_gain,self.d_gain,v0)

        self.SetSWD((v0 * 10.0), (v1 * 10.0), (v2 * 10.0))
                
    @classmethod
    def SetSWD (self, spd1,  spd2,  spd3):
        k_deg = 2000.0 / ( 270 * 3 ) # 角度を500〜2500に直すための係数
        k_spd = 500 / 172              # mm/s→速度用の係数

        spd1 *= k_spd
        spd2 *= k_spd
        spd3 *= k_spd

        COM_SWD = Param.get_com_swd()

        MD03SetMotor(COM_SWD,0,-1*int(spd1))
        MD03SetMotor(COM_SWD,1,-1*int(spd2))
        MD03SetMotor(COM_SWD,2,-1*int(spd3))

        #MD03SetMotor(COM_SWD,0,100)
        #MD03SetMotor(COM_SWD,1,100)
        #MD03SetMotor(COM_SWD,2,100)

        #MD03SetMotor(COM_SWD,3,int(self.arm_lift))
        MD03SetMotorDeg(COM_SWD,3,int(self.arm_lift),200)
        input_data = 15*self.arm_open + 240
        COM_SWD.write(input_data.to_bytes())     

        if  1 :
            self.count += 1
            if self.count > 10:
                self.count = 0
                print(spd1,spd2,spd3,self.d_gain,self.p_gain,self.arm_lift,self.arm_open)
    

