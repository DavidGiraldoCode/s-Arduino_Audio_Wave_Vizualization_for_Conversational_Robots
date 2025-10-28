import sys
from PySide6.QtWidgets import QApplication
import asyncio 

# --- FIX: Reverting to the robust community-maintained bridge ---
# The official PySide6.QtAsyncio is incomplete for network connections.
# We will use 'qasync' which fully implements the required networking hooks 
# needed by libraries like 'websockets'.
from qasync import QApplication as QAsyncApplication, run

# Import the AppController class
from app_controller import AppController

# --- Coroutine that keeps the asyncio loop alive indefinitely (required by qasync) ---
async def wait_for_tasks():
    """Keeps the asyncio event loop running until the Qt application exits."""
    await asyncio.Future()
# -------------------------------------------------------------------

def main():
    # 1. Standard PySide6 App setup
    # CRITICAL FIX: Use QAsyncApplication when using qasync to properly integrate the main loop.
    app = QAsyncApplication(sys.argv)
    
    # 2. Instantiate the Controller (which creates the Model and View)
    controller = AppController()
    
    # Display the GUI
    controller.show()
    
    print("Starting merged Qt and asyncio event loops using qasync...")
    
    # 3. CRITICAL FIX: Use qasync.run() with a coroutine.
    # This function merges the loops and keeps the asyncio loop running indefinitely.
    try:
        # Pass the coroutine entry point to qasync.run()
        sys.exit(run(wait_for_tasks()))
    except Exception as e:
        print(f"An error occurred during application runtime: {e}")



def mainTwo():
    """
    Application entry point. Initializes the Qt environment and the AppController.
    """
    # 1. Initialize the Qt Application instance
    app = QApplication(sys.argv)
    
    # 2. Instantiate the Controller (which creates the Model and View)
    controller = AppController()
    
    # Display the GUI
    controller.show()
    
    print("Starting merged Qt and asyncio event loops using PySide6.QtAsyncio...")
    
    # 3. Use QtAsyncio.run() instead of app.exec().
    # This function starts the Qt loop AND injects the asyncio loop handler.
    # The application now stays alive until the user closes the main window.
    try:
        sys.exit(QtAsyncio.run(handle_sigint=True))
    except Exception as e:
        print(f"An error occurred during application runtime: {e}")
    
    # Without asynchronism
    #sys.exit(app.exec())


if __name__ == "__main__":
    main()
