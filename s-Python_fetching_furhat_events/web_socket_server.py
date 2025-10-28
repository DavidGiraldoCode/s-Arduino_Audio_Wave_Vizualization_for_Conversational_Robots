import asyncio
import struct
import numpy as np
from websockets.asyncio.server import serve

SAMPLE_RATE = 16000
FREQUENCY = 440
AMPLITUDE = 30000  # Max for 16-bit
DT = 1.0 / SAMPLE_RATE

async def audio_stream_handler(websocket):
    print("Client connected")

    t = 0.0
    try:
        while True:
            sample_value = int(AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t))
            t += DT

            frame = struct.pack('<hh', sample_value, sample_value)  # 16-bit stereo
            await websocket.send(frame)

            await asyncio.sleep(DT)  # match audio sample timing

    except Exception as e:
        print(f"Client disconnected: {e}")

async def main():
    print("Server starting on ws://127.0.0.1:8765")
    async with serve(audio_stream_handler, "127.0.0.1", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
