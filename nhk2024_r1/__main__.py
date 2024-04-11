import sys
import time
import threading
from threading import Timer
from libs import *
from . import *
import ctypes

# 定数の定義
TIME_PERIODIC = 0x0001
TIME_CALLBACK_FUNCTION = 0x0000

def main():
    #Param.read_txt()
    
    th_server = threading.Thread(target=Serv.launch_server, daemon=True) # 処理を割り当てる
    th_server.start() # スレッドを起動する

    th_emerg = threading.Thread(target=Emerg.emergencyThread, daemon=True) # 処理を割り当てる
    th_emerg.start() # スレッドを起動する


    th_sensor = threading.Thread(target=ReadGyro.readSensorThread, daemon=True) # 処理を割り当てる
    th_sensor.start() # スレッドを起動する


    # タイマー割り込み関数のポインタを取得
    TIMERPROC = ctypes.WINFUNCTYPE(None, ctypes.c_uint, ctypes.c_uint, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong)
    timer_proc = TIMERPROC(SWD.thread_swd)


    # タイマー割り込みの登録
    count = ctypes.c_int(0)
    user_param = ctypes.cast(ctypes.byref(count), ctypes.c_void_p)
    timer_id = ctypes.windll.winmm.timeSetEvent(
        10,  # 間隔[ms]
        0,     # 分解能
        timer_proc,  # 割り込み関数
        user_param,  # ユーザーパラメータ
        ctypes.c_uint(TIME_PERIODIC | TIME_CALLBACK_FUNCTION)  # 動作フラグ
    )

    if not timer_id:
        print("Failed to register timer")
        return -2
    
    try:
        while th_server.is_alive() and th_emerg.is_alive() and th_sensor.is_alive:
            time.sleep(2)
        ctypes.windll.winmm.timeKillEvent(timer_id)
        print("Exit with Emergency")
        ReadGyro.threadStop()
        Emerg.threadStop()

        COM_SWD = Param.get_com_swd()
        MD03SetMotor(COM_SWD,0,0)
        MD03SetMotor(COM_SWD,1,0)
        MD03SetMotor(COM_SWD,2,0)
        MD03SetMotor(COM_SWD,3,0)
        sys.exit()
    except KeyboardInterrupt:
        ctypes.windll.winmm.timeKillEvent(timer_id)
        print("except KeyboardInterrupt")
        ReadGyro.threadStop()
        Emerg.threadStop()

        COM_SWD = Param.get_com_swd()
        MD03SetMotor(COM_SWD,0,0)
        MD03SetMotor(COM_SWD,1,0)
        MD03SetMotor(COM_SWD,2,0)
        MD03SetMotor(COM_SWD,3,0)

        sys.exit()

    return 0

if __name__ == '__main__':
    print("server comp")
    main()