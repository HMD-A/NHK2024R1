'''Echoサーバの実装'''
import asyncio
import websockets
from .swd import SWD
from .emergency import Emerg

class Serv:
    joy1x = 0.0
    joy1y = 0.0
    joy2x = 0.0
    emerg = 0
    up = 0
    down = 0
    left = 0
    right = 0
    stop_g = 0
    lift = 0.0

    # この関数に通信しているときに行う処理を書く。
    # クライアントが接続している間は下の関数が常に回っている
    @classmethod
    async def handler(self,websocket):
        # クライアントからのメッセージを取り出してそのまま送り返す（Echo）
        async for message in websocket:
            try:
                #print(message)
                message_s = message.split()
                self.joy1x = float(message_s[0])
                self.joy1y = -1.0*float(message_s[1])
                self.joy2x = -1.0 * float(message_s[2])
                self.emerg = int(message_s[4])
                self.up = int(message_s[5])
                self.down = int(message_s[6])
                self.left = int(message_s[7])
                self.right = int(message_s[8])
                self.lift = float(message_s[11])

                SWD.swdV(self.joy1x,  self.joy1y, self.joy2x,self.lift,self.up)
                SWD.gain(self.up,self.down,self.right,self.left)

                if self.emerg == 1:
                    Emerg.emergency()
                #SWD.SetSWD ( joy1x,  joy1y,  joy2x)

                await websocket.send("#data r1_(100,100) redball_(20,30)_(40,20)_(100,300)_(200,300) purpleball_(50,70)_(120,220)")
            except KeyboardInterrupt:
                raise
    @classmethod
    async def server(self):
        async with websockets.serve(self.handler, "0.0.0.0", 50001):
            try:
                await asyncio.Future()  # run forever
            except KeyboardInterrupt:
                raise

    @classmethod
    def launch_server(self):
        asyncio.run(self.server())

    @classmethod
    def directButton(self,a):
        if a == 1 :
            return self.up
        elif a == 2 :
            return self.down
        elif a == 3 :
            return self.right
        elif a == 4 :
            return self.left
