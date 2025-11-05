
#import os
#from dotenv import load_dotenv



# 1. Load the .env file
# This command pulls the secrets from the .env file (which has API_KEY="...")
# and temporarily adds them to your program's "environment."
#load_dotenv()

# 2. Access the variable
# The os.getenv() function looks into that environment and reads the value 
# associated with the key you provide ("API_KEY").
# We store that value in a Python variable called API_KEY_SECRET.
#API_KEY_SECRET = os.getenv("API_KEY", "Key Not Found!")

# 3. Use the variable
#print(f"The loaded API Key is: {API_KEY_SECRET}")
#http://localhost:8080/#/
#127.0.0.1:

#self.furhat.add_handler(Events.response_audio_data, self.furhat_microphone_data)
#await self.furhat.request_audio_start(sample_rate=16000, microphone=False, speaker=True)
import asyncio, struct
from furhat_realtime_api import AsyncFurhatClient, Events
import base64 # <--- 1. Import base64 module

furhat = AsyncFurhatClient("130.237.67.202", "test")

async def furhat_microphone_data():
     print("Event activated")
     #print(data.get("speaker"))

async def on_speak_start(event):
    print("Furhat started speaking:", event)

async def on_speak_end(event):
    print("Furhat finished speaking:", event)

async def on_audio_stream(event):
    #print("streaming")
    print(event)

async def furhat_microphone_data(data):
    """
    Handler for the raw audio stream data.
    'data' is the event dictionary (e.g., {'speaker': 'base64_string', 'type': '...'}).
    """
    # 2. Safely get the base64 string from the 'speaker' key
    base64_audio_data = data.get('speaker')
    
    # NEW: Print the raw base64 data fragment
    print(f"Getting raw (first 30 chars): {base64_audio_data[:30]}...")
          
    if base64_audio_data:
        try:
            # 3. Decode the base64 string back into raw binary audio bytes
            raw_audio_bytes = base64.b64decode(base64_audio_data)
            
            # Now, raw_audio_bytes is the 16-bit PCM audio you can process
            print(f"Received audio chunk: {len(raw_audio_bytes)} raw bytes.")
            
            # --- NEW LOGIC: Calculate RMS for Left Channel ---
            l_channel_samples = []
            
            # The audio format is 16-bit signed little-endian stereo (L, R)
            # Each stereo frame is 4 bytes (2 bytes for L, 2 bytes for R).
            frame_size = 4
            
            # Iterate over the raw bytes, stepping by the frame size
            for i in range(0, len(raw_audio_bytes) - frame_size + 1, frame_size):
                # Unpack the first 2 bytes (Left channel sample) as a signed short ('h')
                # '<' ensures little-endian
                l_sample = struct.unpack('<h', raw_audio_bytes[i:i+2])[0]
                l_channel_samples.append(l_sample)
                
            # Calculate RMS (Root Mean Square) for the left channel samples
            if l_channel_samples:
                # RMS = sqrt(mean(samples^2)) - This measures the signal energy (loudness)
                sum_of_squares = sum(s**2 for s in l_channel_samples)
                rms = (sum_of_squares / len(l_channel_samples))**0.5
                # The RMS value is printed as a measure of "frequency/activity"
                print(f"L-Channel Activity (RMS Amplitude): {rms:.2f}")
            else:
                print("Not enough samples to process L-Channel data.")
            # --- END NEW LOGIC ---
            
        except Exception as e:
            print(f"Failed to decode or process audio data: {e}")
    else:
        print("Received audio event without 'speaker' (Base64 data).")



async def main():
    try:
        await furhat.connect()
        # Register handlers
        #Async only
        await furhat.request_audio_start(16000, False, True)
        furhat.add_handler(Events.response_audio_data, furhat_microphone_data)
        #furhat.add_handler(Events.response_audio_data, on_audio_stream)
        

        await furhat.request_speak_text("Sending audio to test the streaming data", wait=True)
        await asyncio.sleep(1) 

        
        await asyncio.sleep(1)
        await furhat.request_audio_stop
        await furhat.disconnect()

    except Exception as e:
        print(f"An error occurred during execution: {e}")
    finally:
        # 6. Disconnect cleanly
        print("Disconnecting from Furhat.")
        await furhat.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

#async def run_example():
#    await furhat.connect()
#    await furhat.request_speak_text("Hello world, I am Furhat.", wait=True)
#    await furhat.disconnect()

#asyncio.run(run_example())