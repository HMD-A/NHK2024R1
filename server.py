'''Echoサーバの実装'''
import asyncio
import websockets

# この関数に通信しているときに行う処理を書く。
# クライアントが接続している間は下の関数が常に回っている
async def handler(websocket):
    # クライアントからのメッセージを取り出してそのまま送り返す（Echo）
    async for message in websocket:
        await websocket.send("#data r1_(100,100) redball_(20,30)_(40,20)_(100,300)_(200,300) purpleball_(50,70)_(120,220)")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 50001):
        await asyncio.Future()  # run forever

asyncio.run(main())
