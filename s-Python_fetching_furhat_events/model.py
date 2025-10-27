import serial
import serial.tools.list_ports
from PySide6.QtCore import Qt, QAbstractListModel

# --- GLOBAL CONSTANTS ---
SERIAL_BAUDRATE = 9600
# Example options list for the QComboBox
COMBO_OPTIONS = [f"Item {i}" for i in range(1, 11)] 


class AppModel(QAbstractListModel):
    """
    Manages application state, data, and business logic (including serial communication).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- Internal Application State ---
        self._dropdown_options = COMBO_OPTIONS
        self._live_input_text = ""
        self._committed_input_text = "N/A"
        
        # --- Serial Communication State ---
        self._serial_conn = None
        self._baudrate = SERIAL_BAUDRATE
    
    # --- QAbstractListModel required methods (for complex views, simple placeholder here) ---
    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and role == Qt.DisplayRole:
            return self._dropdown_options[index.row()]
        return None

    def rowCount(self, parent=None):
        return len(self._dropdown_options)

    # --- Data Accessors/Mutators ---

    def get_dropdown_options(self):
        """Returns the list of items for the ComboBox."""
        return self._dropdown_options

    def set_live_input_text(self, text):
        """Sets the state for text being actively typed."""
        self._live_input_text = text

    def get_live_input_text(self):
        """Returns the current live input text."""
        return self._live_input_text

    def set_committed_input_text(self, text):
        """Sets the state for text committed via ENTER key."""
        self._committed_input_text = text

    def get_committed_input_text(self):
        """Returns the last committed input text."""
        return self._committed_input_text

    # --- SERIAL PORT METHODS (Skeleton) ---

    def get_available_ports(self):
        """Fetches a list of available serial port names."""
        try:
            # Placeholder for real serial logic, returns a dummy list for demonstration
            # In a real app, you'd use: return [port.device for port in serial.tools.list_ports.comports()]
            return ["/dev/ttyUSB0 (Demo)", "COM3 (Demo)"]
        except Exception:
            # Handle case where pyserial is not installed or permissions denied
            return []

    def connect_serial(self, port_name):
        """Attempts to open a serial connection (Placeholder)."""
        print(f"MODEL: Attempting to connect to {port_name} @ {self._baudrate} baud...")
        # Placeholder for connection logic
        return True # Assume success for demo

    def send_data(self, data):
        """Sends data over the serial connection (Placeholder)."""
        if self._serial_conn:
            print(f"MODEL: Sending data: {data}")
        else:
            print("MODEL: Error - Cannot send data, serial connection is not active.")
