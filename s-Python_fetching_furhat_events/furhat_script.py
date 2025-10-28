from furhat_realtime_api import AsyncFurhatClient, Events
import asyncio

import os
from dotenv import load_dotenv

# 1. Load the .env file
# This command pulls the secrets from the .env file (which has API_KEY="...")
# and temporarily adds them to your program's "environment."
load_dotenv()

# 2. Access the variable
# The os.getenv() function looks into that environment and reads the value 
# associated with the key you provide ("API_KEY").
# We store that value in a Python variable called API_KEY_SECRET.
API_KEY_SECRET = os.getenv("API_KEY", "Key Not Found!")

# 3. Use the variable
print(f"The loaded API Key is: {API_KEY_SECRET}")
#http://localhost:8080/#/
#127.0.0.1:
furhat = AsyncFurhatClient("127.0.0.1:9000", API_KEY_SECRET)

async def on_speak_start(event):
    print("Furhat started speaking:", event)

async def on_speak_end(event):
    print("Furhat finished speaking:", event)

async def main():
    await furhat.connect()
    # Register handlers
    furhat.add_handler(Events.response_speak_start, on_speak_start)
    furhat.add_handler(Events.response_speak_end, on_speak_end)
    
    #await furhat.request_speak_text("Hello! Please say something.")
    #await furhat.disconnect()

asyncio.run(main())