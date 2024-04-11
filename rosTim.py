import ctypes
import time

# 定数の定義
TIME_PERIODIC = 0x0001
TIME_CALLBACK_FUNCTION = 0x0000

# タイマー割り込み関数
def timer_callback(uTimerID, uMsg, dwUser, dw1, dw2):
    #count = ctypes.cast(dwUser, ctypes.POINTER(ctypes.c_int)).contents
    #count.contents.value += 1
    print(time.time())

# メイン関数
def main():
    # タイマー割り込み関数のポインタを取得
    TIMERPROC = ctypes.WINFUNCTYPE(None, ctypes.c_uint, ctypes.c_uint, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong)
    timer_proc = TIMERPROC(timer_callback)

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

    # タイマーが動作する間はプログラムが終了しないようにする
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Ctrl+C が押されたらタイマーを解除して終了する
        ctypes.windll.winmm.timeKillEvent(timer_id)
        print("Timer stopped.")
        return 0

if __name__ == "__main__":
    main()
