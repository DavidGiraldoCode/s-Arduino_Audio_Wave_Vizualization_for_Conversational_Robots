import asyncio
import struct
from websockets.asyncio.client import connect

async def listen_to_audio():
    try:
        async with connect("ws://127.0.0.1:8765") as websocket:
            print("Connected to server")

            while True:
                frame = await websocket.recv()
                left, right = struct.unpack('<hh', frame)
                print(f"Audio Frame: L={left}, R={right}")

    except Exception as e:
        print(f"Connection closed: {e}")

if __name__ == "__main__":
    asyncio.run(listen_to_audio())

