import asyncio
import struct
import sys
from websockets.asyncio.client import connect

# --- Qt/qasync Imports (Required for QTimer) ---
# NOTE: You will need 'pip install PySide6 qasync' for this to run.
from PySide6.QtCore import QTimer, QCoreApplication
from PySide6.QtWidgets import QApplication
import qasync

ws_server_instance = None
ws_data_queue = asyncio.Queue()
# Ensure initial data point is a tuple (L, R) for consistency
ws_latest_data_point = (0, 0) 
TIME_UNTIL_STARTS_LISTENING = 0.1
LISTENING_TIME = 0.05 # seconds
GUI_SIMULATOR_RENDER_TIMEOUT = 50 #milliseconds
WEB_SOCKET_SERVER_URL = "ws://127.0.0.1:8765"

async def connect_to_server():
    """Establishes and stores a persistent WebSocket connection."""
    global ws_server_instance # MINIMAL FIX 1: Required to modify the global variable
    if ws_server_instance and not ws_server_instance.closed:
        print("Client already connected.")
        return True

    try:
        # Use await connect() directly, bypassing the context manager (async with)
        ws_server_instance = await connect(WEB_SOCKET_SERVER_URL)
        print("Connected and stored persistent WebSocket client.")
        return True
    except Exception as e:
        print(f"Connection attempt failed: {e}")
        ws_server_instance = None
        return False


async def disconnect_from_server():
    """Gracefully closes the persistent WebSocket connection."""
    global ws_server_instance # MINIMAL FIX 1: Required to modify the global variable
    if ws_server_instance:
        await ws_server_instance.close()
        ws_server_instance = None
        print("Disconnected WebSocket client.")


async def listen_indefinitely():
    """HELPER: Fetches and unpacks data until cancelled by an external signal."""
    global ws_server_instance # Access the global connection instance
    try:
        while True:
            # This await is where the execution pause/cancellation occurs
            frame = await ws_server_instance.recv()
            
            # Unpack the 16-bit stereo frame
            if len(frame) == 4:
                left, right = struct.unpack('<hh', frame)
                #print(f"Audio Frame: L={left}, R={right}")
                await ws_data_queue.put((left, right)) 
            else:
                print(f"Warning: Received frame of unexpected size {len(frame)}. Expected 4 bytes.")
    except asyncio.CancelledError:
        # This is the expected exception when the task is cancelled after 50ms
        print("Listener: Task received cancellation signal.")
        raise # Re-raise to cleanly exit the task


async def process_websocket_data_continuously():
    """Fast-running task: Drains the queue and updates the state variable."""
    global ws_latest_data_point # MINIMAL FIX 1: Must declare global for assignment
    while True:
        #print(f"Queue size: {ws_data_queue.qsize()}")
        # 1. Wait until at least ONE item is available (blocks non-blockingly)
        first_frame = await ws_data_queue.get() 
        
        # 2. Aggressively empty the rest of the queue to find the freshest frame
        latest_frame = first_frame
        while True:
            try:
                # Use get_nowait to avoid blocking on empty queue
                latest_frame = ws_data_queue.get_nowait()
            except asyncio.QueueEmpty:
                print(f"Emptying queue!")
                # We found the most recent frame—break out and process it
                break

        # 3. Process ONLY the 'latest_frame' and update the single state variable
        # In a real app, this is where you'd calculate RMS and normalization
        ws_latest_data_point = latest_frame
        print(f"Queue data point: {latest_frame}")
        # Yield control back to the event loop briefly after processing a burst
        await asyncio.sleep(0) 

async def main_client_workflow():
    """
    The orchestrator, now using loop.create_task() to manage the listening job.
    """
    # 1. Connect to the server
    if await connect_to_server():
        
        # 2. Wait 1 second (Sequential Await)
        print(f"Waiting {TIME_UNTIL_STARTS_LISTENING} second...")
        await asyncio.sleep(TIME_UNTIL_STARTS_LISTENING) # REQUIREMENT: Wait 1 second

        # --- Concurrency Block (Create Task) ---
        print(f"Starting {LISTENING_TIME} data reception burst using loop.create_task()...")
        
        # Get the running event loop
        loop = asyncio.get_running_loop()
        
        # MINIMAL FIX 3: Use create_task() to start the listening job concurrently
        listener_task = loop.create_task(listen_indefinitely())
        processor_task = loop.create_task(process_websocket_data_continuously())
        
        try:
            # 3. Wait for just 50ms (Allow listener task to run concurrently)
            await asyncio.sleep(LISTENING_TIME)
            
            # 4. Stop the task after the duration
            listener_task.cancel()
            processor_task.cancel()

            # Wait for the cancellation to propagate and the task to finish cleanup
            # We use wait_for here to ensure the cancellation finishes within a reasonable time
            # Wait for both cancellations to propagate
            await asyncio.wait_for(asyncio.gather(listener_task, processor_task), timeout=0.5) 

        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass 
        except Exception as e:
            print(f"Error during listening phase: {e}")
        finally:
            print("Finished data test (Tasks stopped).")
            
        # 5. Disconnect
        await disconnect_from_server()
        
    # We must keep the loop running indefinitely for qasync, so we await a Future
    # that is canceled when the Qt app shuts down (handled by setup_and_run_app below)
        
    # 6. Close the app (implicit when this coroutine finishes)

# --- SYNCHRONOUS LOGIC (The Poller/QTimer) ---

def update_gui_simulation():
    """
    QTimer Slot: Runs every 50ms on the main thread (simulating the render loop).
    This safely reads the globally updated data point.
    """
    global ws_latest_data_point
    print(f"Updating data point {ws_latest_data_point}")
    # This print statement emulates the Matplotlib canvas update call
    # We use \r to overwrite the line, simulating a real-time update
    output = f"GUI Render Loop (50ms): Polling Latest Data L/R: {ws_latest_data_point}"
    sys.stdout.write('\r' + output.ljust(80))
    sys.stdout.flush()
    print('\n')


def setup_and_run_app():
    """
    The synchronous entry point that sets up Qt and uses qasync to bridge the loops.
    """
    # Initialize the Qt Application
    app = QApplication(sys.argv)
    
    # Setup the QTimer (the regulated polling mechanism)
    gui_timer = QTimer()
    gui_timer.timeout.connect(update_gui_simulation)
    gui_timer.start(GUI_SIMULATOR_RENDER_TIMEOUT) # 50ms interval (20 FPS)
    
    # Start the asyncio workflow concurrently
    try:
        # qasync.run() merges the QTimer/Qt loop with the asyncio tasks
        # It takes the main_client_workflow coroutine as the entry point
        qasync.run(main_client_workflow()) 
    except Exception as e:
        # Note: exceptions are sometimes masked by qasync's internal cleanup
        print(f"\n\nApplication Shutdown Complete.")
        
    # Ensure the timer is stopped on exit
    gui_timer.stop()


if __name__ == "__main__":
    setup_and_run_app()