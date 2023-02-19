# more details at: https://websockets.readthedocs.io/en/6.0/intro.html
# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import websockets

async def time(websocket, path):
    print("new connection path " + path)
    while True:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        #print(now)
        await websocket.send(now)
        await asyncio.sleep(random.random() * 3)

start_server = websockets.serve(time, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

