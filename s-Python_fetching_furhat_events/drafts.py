import serial # For serial communication
import serial.tools.list_ports
import os     # For path manipulation
import numpy as np # For array manipulation
from scipy.io import wavfile # <-- FIX: Now imported at module level
from PySide6.QtCore import Qt, QAbstractListModel, Signal 
import asyncio # New import for async functionality
import struct # For unpacking binary data
from websockets.client import connect # For WebSocket connection

from scipy.io import wavfile # <-- FIX: Now imported at module level

# --- GLOBAL CONSTANTS ---
SERIAL_BAUDRATE = 9600
# Example options list for the QComboBox
COMBO_OPTIONS = [f"Item {i}" for i in range(1, 11)] 


class AppModel(QAbstractListModel):
    """
    Manages application state, data, and business logic (including serial communication).
    """
    # --- Signal (Event Emitter)
    input_text_commited = Signal() #Class Descriptor
    input_text_cleared = Signal()
    # NEW SIGNAL: Announces when the slow async task is complete
    async_task_completed = Signal(str)
    # REMOVED: ws_data_arrived signal is now replaced by direct state access

    # ------------------------- CONSTRUCTOR

    def __init__(self, parent=None):
        super().__init__(parent)
        # Standard instance attributes
        # --- Internal Application State ---
        self._dropdown_options = COMBO_OPTIONS
        self._live_input_text = ""
        self._committed_input_text = "N/A"
        
        # --- Serial Communication State ---
        self._ports = []
        self._serial_conn = None
        self._baudrate = SERIAL_BAUDRATE

        # --- ASYNCIO / WEBSOCKET STATE ---
        # Queue for raw audio frames (L, R tuples)
        self.ws_audio_queue = asyncio.Queue() 
        # State variable to hold the latest *normalized* value for the timer to read
        self._latest_ws_normalized_value = 0.0

        # ---- Audio debugging
        
    
    # --- QAbstractListModel required methods (for complex views, simple placeholder here) ---
    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and role == Qt.DisplayRole:
            return self._dropdown_options[index.row()]
        return None

    def rowCount(self, parent=None):
        return len(self._dropdown_options)
    
    # =====================================================================
    # =====================================================================
    # --- Custom Events --------------------
    # =====================================================================
    # =====================================================================
    def onCommitedInputTextChange():
        print("Something")

    # =====================================================================
    # =====================================================================
    # --- Data Accessors/Mutators ---
    # =====================================================================
    # =====================================================================

    def get_dropdown_options(self):
        """Returns the list of items for the ComboBox."""
        return self._dropdown_options

    def set_live_input_text(self, text):
        """Sets the state for text being actively typed."""
        self._live_input_text = text
        if(text == ""):
            self.input_text_cleared.emit()

    def get_live_input_text(self):
        """Returns the current live input text."""
        return self._live_input_text

    def set_committed_input_text(self, text):
        """Sets the state for text committed via ENTER key."""
        self._committed_input_text = text
        # Triggers the event (Sends/emits the signal)
        print("The signal is sent")
        self.input_text_commited.emit()

    def get_committed_input_text(self):
        """Returns the last committed input text."""
        return self._committed_input_text
    
    # ======== Load Audio File
    def load_audio_samples(self, file_path):
        """
        Loads the raw audio samples from a local WAV file path.
        Returns (sample_rate, samples) tuple, or a default set on failure.
        
        Architecture Rationale: This is data acquisition, so it belongs in the Model. 
        It isolates the file system logic and external library (scipy) dependency.
        """
        try:
            # 1. Build the absolute path relative to the current file (model.py)
            absolute_file_path = os.path.join(os.path.dirname(__file__), file_path)
            
            print(f"Model: Attempting to load audio from: {absolute_file_path}")
            
            # 2. Read the WAV file using scipy
            # fs = sample rate (int), samples = raw audio data (NumPy array)
            fs, samples = wavfile.read(absolute_file_path)
            
            # 3. Handle Stereo Data (If the audio has multiple channels)
            # Visualization usually works better with mono, so we select the first channel.
            if samples.ndim > 1:
                samples = samples[:, 0]
                print("Model: Converted stereo audio to mono (first channel).")
                
            print(f"Model: Audio loaded successfully. Sample rate: {fs} Hz. Total samples: {len(samples)}.")
            return fs, samples
            
        except FileNotFoundError:
            print(f"Model Error: Audio file '{file_path}' not found at {absolute_file_path}. Returning silent data.")
            return 44100, np.array([0], dtype=np.int16)
            
        except ImportError:
            # Handles the case where scipy is not installed
            print("Model Error: 'scipy' is required but not installed. Returning silent data.")
            return 44100, np.array([0], dtype=np.int16)
            
        except Exception as e:
            print(f"Model Error: Failed to read or parse WAV file: {e}. Returning silent data.")
            # Fallback to a safe, empty result
            return 44100, np.array([0], dtype=np.int16)
            
        except Exception as e:
            print(f"Model Error: Failed to read or parse WAV file: {e}. Returning silent data.")
            # Fallback to a safe, empty result
            return 44100, np.array([0], dtype=np.int16)

    # =====================================================================
    # =====================================================================
    # --- ASYNCIO IMPLEMENTATION ---
    # =====================================================================
    # =====================================================================
    
    def get_latest_ws_normalized_value(self):
        """Synchronous access for the Controller's QTimer slot."""
        return self._latest_ws_normalized_value
        

    async def _process_websocket_data_continuously(self):
        """
        Runs in the background, consuming data from the queue and updating 
        the single state variable for the main thread to read.
        """
        while True:
            # Safely get the next (left, right) audio sample tuple from the queue
            left, right = await self.ws_audio_queue.get() 
            
            # Calculate RMS/Intensity (Model's core logic)
            # Use the absolute value of the larger channel for intensity
            raw_value = max(abs(left), abs(right))
            MAX_16BIT = 32768.0
            
            # Normalize and clamp between 0.0 and 1.0
            normalized_value = min(raw_value / MAX_16BIT, 1.0)
            
            # Update the state variable (The Controller reads this on its timer)
            self._latest_ws_normalized_value = normalized_value
            self.ws_audio_queue.task_done()

    async def _listen_to_audio_form_websocket(self):
        """
        Asynchronous consumer: Reads data from the WebSocket and puts it 
        into the thread-safe asyncio Queue.
        """
        try:
            # Use a slightly longer timeout in case the server takes a moment
            async with connect("ws://127.0.0.1:8765", open_timeout=5) as websocket:
                print("Model Async: Connected to server.")

                while True:
                    # Await data arrival (non-blocking)
                    frame = await websocket.recv()
                    
                    # Ensure frame is the expected size before unpacking
                    if len(frame) == 4:
                        left, right = struct.unpack('<hh', frame)
                        # Put the raw data into the queue (non-blocking if queue is full)
                        await self.ws_audio_queue.put((left, right)) 
                    else:
                        print(f"Model Async: Warning, received unexpected frame size: {len(frame)}")

        except ConnectionRefusedError:
            print("Model Async Error: Connection refused. Is the server running on 127.0.0.1:8765?")
        except Exception as e:
            print(f"Model Async: Connection closed: {e}")
            
        # Ensure the Model state is reset if the connection drops
        self._latest_ws_normalized_value = 0.0 
        

    async def _slow_async_operation(self):
        """
        The actual asynchronous function that simulates a long-running I/O task.
        Runs entirely within the asyncio event loop.
        """
        print("Model Async: Task started, awaiting 2 seconds...")
        # AWAIT is the keyword that yields control back to the event loop, 
        # allowing the GUI to remain responsive.
        await asyncio.sleep(2) 
        print("Model Async: Wait finished. Emitting result signal.")
        
        # When emitting a signal from an async task, this is safe because 
        # QtAsyncio ensures the loop is running on the main thread.
        self.async_task_completed.emit("Async Task Completed!")

    def start_async_operation(self):
        """
        Synchronous public method to be called by the Controller.
        Schedules the async task to run on the event loop.
        """
        if self.is_serial_connected():
             return "Please disconnect the serial port first."
        
        # Schedule the slow task
        asyncio.create_task(self._slow_async_operation())
        
        # Schedule the WebSocket listener
        asyncio.create_task(self._listen_to_audio_form_websocket())
        
        # Schedule the continuous queue processor (NEW)
        asyncio.create_task(self._process_websocket_data_continuously())
        
        # This function returns *immediately* to the Controller.
        return "All Async Tasks Scheduled (Non-blocking)."


    # =====================================================================
    # =====================================================================
    # --- SERIAL COMMUNICATION METHODS ---
    # =====================================================================
    # =====================================================================

    def disconnect_serial(self):
        """Closes the active serial connection."""
        if self._serial_conn and self._serial_conn.is_open:
            self._serial_conn.close()
            self._serial_conn = None
            print("Model: Serial connection closed.")
        elif self._serial_conn:
            self._serial_conn = None
            
    def is_serial_connected(self):
        """Returns True if a serial connection is currently open."""
        return self._serial_conn is not None and self._serial_conn.is_open

    def get_available_ports(self):
        """Fetches a list of available serial port names."""
        try:
            # Use pyserial tool to list all available ports
            self._ports = serial.tools.list_ports.comports()
            # Return list of port device strings
            return [port.device for port in self._ports]
        except Exception as e:
            # Handle case where pyserial is not installed or permissions denied
            # In a real app, you might log this error or show it in the UI
            print(f"Error listing ports: {e}")
            return []

    def connect_serial(self, port_name):
        """
        Attempts to open a serial connection to the given port.
        Returns True on success, False on failure.
        """
        # 1. Close any existing connection first
        if self._serial_conn:
            self.disconnect_serial()
            
        try:
            # 2. Initialize and open the serial connection
            self._serial_conn = serial.Serial(
                port=port_name,             # The selected port name (e.g., '/dev/ttyACM0')
                baudrate=self._baudrate,    # The defined baud rate (9600)
                timeout=1                   # Timeout for read operations
            )
            
            print(f"Model: Serial connected to {port_name} @ {self._baudrate} baud.")
            # If you defined a signal for status updates, you'd emit it here:
            # self.connection_status_changed.emit(f"Connected to {port_name}")
            return True
            
        except serial.SerialException as e:
            # Catch common errors like port not found or permission denied
            print(f"Model Error: Failed to connect to {port_name}: {e}")
            self._serial_conn = None
            # self.connection_status_changed.emit(f"Error: Failed to connect to {port_name}")
            return False
        except Exception as e:
            # Catch any other unexpected errors
            print(f"Model Error: An unexpected error occurred: {e}")
            self._serial_conn = None
            return False
    
    def send_data(self, data):
        """
        Sends the provided data over the serial connection.
        Data is converted to bytes and terminated with a newline character.
        """
        # 1. Invariance Check: Is the connection open?
        if not self.is_serial_connected():
            print("Model: Cannot send data, serial connection is not active.")
            return False

        try:
            # 2. Prepare data: Convert to a string, append newline, and encode to bytes
            # The newline is often required for the receiving end (e.g., Arduino Serial.readStringUntil('\n'))
            data_to_send = f"{data}\n".encode('utf-8')
            
            # 3. Write data to the port
            self._serial_conn.write(data_to_send)
            print(f"Model: Data sent successfully: {data}") # Uncomment for debugging
            return True
            
        except serial.SerialTimeoutException:
            # This handles cases where the write buffer times out
            print("Model Error: Serial write timeout occurred.")
            return False
            
        except serial.SerialException as e:
            # This handles unexpected disconnections during transmission
            print(f"Model Error: Connection lost during write: {e}")
            self.disconnect_serial() # Clean up the broken connection
            return False
        
        except Exception as e:
            print(f"Model Error: Unexpected error during data send: {e}")
            return False
