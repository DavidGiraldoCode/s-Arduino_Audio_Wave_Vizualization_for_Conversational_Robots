import sys
import os 
import numpy as np
import io
import serial # Required for serial communication
#import serial.tools.list_ports # Required to list available ports

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit
)
from PySide6.QtCore import (
    QAbstractListModel, Qt, QModelIndex,
    QSize, QUrl, QFile, QByteArray, QTimer
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

# Matplotlib Imports for plotting
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# --- GLOBAL CONSTANTS ---
ASSET_AUDIO_URL = "qrc:audio_test.wav" 
LOCAL_AUDIO_FILE_PATH = os.path.join(os.path.dirname(__file__), 'audio_test.wav')
# Timer interval for plot and data updates (50ms = 20 FPS)
PLOT_UPDATE_INTERVAL = 50 
# Background color for the plot (dark theme)
PLOT_BG_COLOR = "#323232"
# Baud rate for Arduino communication
SERIAL_BAUDRATE = 9600


# --- 1. MODEL: Handles data, audio parsing, and serial communication logic ---

class AppModel(QAbstractListModel):
    """Manages application data, including dropdown options and serial connection state."""
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self._options = ["Option A", "Option B", "Option C"]
        self._input_text = ""
        
        # Serial communication state
        self._serial_conn = None
        self._baudrate = SERIAL_BAUDRATE

    # Standard QAbstractListModel methods (data display)
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._options[index.row()]
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._options)

    # Application-specific Model accessors/mutators
    def get_dropdown_options(self):
        return self._options

    def set_input_text(self, text):
        self._input_text = text

    def get_input_text(self):
        return self._input_text

    # --- SERIAL PORT METHODS ---

    def get_available_ports(self):
        """Fetches a list of available serial port names."""
        try:
            # Use pyserial tool to list all available ports
            ports = serial.tools.list_ports.comports()
            # Return list of port names (e.g., ['COM3', '/dev/ttyACM0'])
            return [port.device for port in ports]
        except Exception as e:
            print(f"Error listing ports: {e}")
            return []

    def connect_serial(self, port_name):
        """Attempts to open a serial connection to the given port."""
        if self._serial_conn:
            self.disconnect_serial()
            
        try:
            # Initialize and open the serial connection
            self._serial_conn = serial.Serial(port_name, self._baudrate, timeout=1)
            print(f"Serial connected to {port_name} @ {self._baudrate} baud.")
            return True
        except Exception as e:
            print(f"Error connecting serial: {e}")
            self._serial_conn = None
            return False

    def disconnect_serial(self):
        """Closes the active serial connection."""
        if self._serial_conn and self._serial_conn.is_open:
            self._serial_conn.close()
            self._serial_conn = None
            print("Serial connection closed.")
        elif self._serial_conn:
            self._serial_conn = None
    
    def is_serial_connected(self):
        """Returns True if a serial connection is currently open."""
        return self._serial_conn is not None and self._serial_conn.is_open

    def send_data(self, data):
        """
        Sends the processed audio data over the serial connection.
        Data is sent as an ASCII string followed by a newline.
        """
        if self.is_serial_connected():
            try:
                # Format data string and encode to bytes, adding newline for Arduino's Serial.readStringUntil('\n')
                data_to_send = f"{data}\n".encode('utf-8')
                self._serial_conn.write(data_to_send)
            except Exception as e:
                print(f"Error sending data, connection lost: {e}")
                # If sending fails, assume connection is lost and disconnect
                self.disconnect_serial()


# --------------------------------------------------------------------------------------------------

# --- 2. CUSTOM PLOTTING WIDGET (Matplotlib Bar Integration) ---

class AudioIntensityCanvas(QWidget):
    """A custom widget using Matplotlib to show two real-time intensity bars."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize the Figure and Canvas with the dark background
        self.figure = Figure(figsize=(4, 3), facecolor=PLOT_BG_COLOR)
        self.canvas = FigureCanvas(self.figure)
        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialize the single subplot
        self.ax = self.figure.add_subplot(111)
        
        # Initialize the bar containers
        self.bar_raw = None
        self.bar_norm = None
        
        self.init_plot_style()
        
    def init_plot_style(self):
        """Sets up the initial appearance of the plot, including the dark background."""
        self.ax.clear()
        
        # Set the requested background color for the axes
        self.ax.set_facecolor(PLOT_BG_COLOR) 
        
        # Style grid lines, ticks, and labels for visibility on dark background
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        
        self.ax.set_title("Real-Time Audio Frame Intensity", color='white')
        self.ax.set_xticks([0.2, 0.7])
        self.ax.set_xticklabels(['Raw', 'Normalized'], color='white')
        self.ax.set_ylim(0, 1.1) # Max Y-limit for the bars
        self.ax.set_ylabel("Amplitude / Intensity", color='white')
        self.ax.grid(axis='y', alpha=0.3, color='gray')
        
        # Re-initialize the bar objects
        self.bar_raw = self.ax.bar(0.2, 0, width=0.35, color='cyan')
        self.bar_norm = self.ax.bar(0.65, 0, width=0.35, color='lime')
        
        self.figure.tight_layout(pad=1.5)

    def plot_frame_intensity(self, raw_value, normalized_value):
        """
        Updates the two intensity bars with new values.
        """
        if not self.bar_raw or not self.bar_norm:
            return

        # 1. Raw Bar Update: Scale raw RMS value for display
        raw_display_value = min(raw_value / 32768.0, 1.1)
        self.bar_raw[0].set_height(raw_display_value)
        
        # 2. Normalized Bar Update: Clamped between 0.0 and 1.0
        self.bar_norm[0].set_height(normalized_value)
        
        # Change color to red if normalized value is near clipping (feedback)
        if normalized_value >= 0.95:
             self.bar_norm[0].set_color('red')
        else:
             self.bar_norm[0].set_color('lime')

        # Redraw the canvas for a real-time effect
        self.canvas.draw()


# --------------------------------------------------------------------------------------------------

# --- 3. VIEW/CONTROLLER: The main window and all UI elements ---

class MainWindow(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model
        
        # --- AUDIO/VISUALIZATION DATA INITIALIZATION ---
        self.full_audio_samples = self.read_audio_file()
        self.sample_rate = 44100
        self.samples_per_frame = int(self.sample_rate * (PLOT_UPDATE_INTERVAL / 1000.0))
        self.current_sample_index = 0
        
        # Setup the QTimer for continuous plot updates
        self.plot_timer = QTimer(self)
        self.plot_timer.setInterval(PLOT_UPDATE_INTERVAL)
        self.plot_timer.timeout.connect(self.update_live_bar)
        
        # --- AUDIO PLAYBACK SETUP ---
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput() # Required for sound output to speakers
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setSource(QUrl(ASSET_AUDIO_URL))
        
        # Connect signals for UI updates and infinite looping
        self.media_player.playbackStateChanged.connect(self.update_play_button_text)
        self.media_player.positionChanged.connect(self._check_and_reset_loop) 
        # -------------------

        # Window setup and layout
        self.setWindowTitle("PySide6 Real-Time Audio Bar Visualizer (Serial Demo)")
        self.setFixedSize(QSize(400, 600))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- WIDGETS ---
        self.intensity_plot = AudioIntensityCanvas() 
        
        # Serial Status Label (new)
        self.serial_status_label = QLabel("Serial: Disconnected")
        self.serial_status_label.setWordWrap(True)
        
        # Port Selection Dropdown (new purpose)
        self.dropdown = QComboBox()
        self.dropdown.setFixedHeight(40)
        
        # Populate the dropdown with available serial ports
        port_options = ["--- Select COM Port ---"] + self.model.get_available_ports()
        self.dropdown.addItems(port_options)
        
        self.dropdown_label = QLabel("Serial Port:")
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter text here...")
        self.text_input.setFixedHeight(40)
        self.input_label = QLabel("Input Echo: ")
        self.input_label.setWordWrap(True)
        self.button_play = QPushButton("▶️ Play & Visualize Audio (Loop)")
        self.button_play.setFixedHeight(40)
        self.button_demo = QPushButton("Demo Button")
        self.button_demo.setFixedHeight(40)
        
        # --- DEFINING LAYOUT ---
        layout.addWidget(self.intensity_plot) 
        layout.addWidget(self.serial_status_label) # Status label below the plot
        layout.addWidget(self.dropdown_label)
        layout.addWidget(self.dropdown) # Port selection combo box
        layout.addWidget(self.input_label)
        layout.addWidget(self.text_input)
        layout.addWidget(self.button_play)
        layout.addWidget(self.button_demo)

        # --- CONNECTING EVENTS ---
        # Connect dropdown change to serial connection handler
        self.dropdown.currentIndexChanged.connect(self.handle_dropdown_change)
        self.text_input.textChanged.connect(self.handle_text_input_change)
        self.button_play.clicked.connect(self.handle_play_audio_and_plot)
        self.button_demo.clicked.connect(self.handle_demo_button_click)
        
        # Initial plot visualization
        self.intensity_plot.plot_frame_intensity(0, 0)
    
    # --- HELPER METHODS ---

    def _generate_dummy_samples(self):
        """Helper to generate a simple sine wave for visualization fallback."""
        fs = 44100
        duration = 1.0
        t = np.linspace(0., duration, int(fs * duration), endpoint=False)
        samples = (0.5 * np.sin(2. * np.pi * 440. * t) * (2**15 - 1)).astype(np.int16)
        return samples

    def read_audio_file(self):
        """Reads the entire WAV file from the Qt Resource System (qrc:/) once."""
        try:
            from scipy.io import wavfile
            
            qrc_path = QUrl(ASSET_AUDIO_URL).path() 
            q_file = QFile(qrc_path)
            
            if not q_file.open(QFile.ReadOnly):
                print(f"ERROR: Could not open resource file: {qrc_path}. Using dummy data.")
                return self._generate_dummy_samples()

            data_qbytearray = q_file.readAll()
            q_file.close()

            data_bytes = bytes(data_qbytearray.data())
            byte_stream = io.BytesIO(data_bytes)
            
            # Read the WAV file data using scipy
            fs, samples = wavfile.read(byte_stream)
            
            # Ensure we only have one channel (mono) for visualization
            if samples.ndim > 1:
                samples = samples[:, 0]
                
            return samples
            
        except ImportError:
            print("WARNING: scipy not installed. Cannot parse WAV file samples. Using dummy data.")
            return self._generate_dummy_samples()
        except Exception as e:
            print(f"Error reading or parsing WAV resource: {e}. Using dummy data.")
            return self._generate_dummy_samples()
        
    def _check_and_reset_loop(self, position):
        """Checks media player position to implement infinite loop."""
        # Check if the position is near the end (within 100ms) of the duration
        if self.media_player.duration() > 0 and position >= self.media_player.duration() - 100:
            print("Looping audio...")
            self.media_player.setPosition(0)
            self.current_sample_index = 0 # Reset visualization index
            self.media_player.play()


    # --- LIVE VISUALIZATION AND SERIAL DATA SENDING ---

    def update_live_bar(self):
        """
        Processes the next frame of audio data, updates the visualization,
        and sends the normalized intensity over serial.
        """
        total_samples = len(self.full_audio_samples)
        if total_samples == 0:
            self.intensity_plot.plot_frame_intensity(0, 0)
            return

        # --- 1. Get Audio Frame (Input Stream Simulation) ---
        start_index = self.current_sample_index
        end_index = start_index + self.samples_per_frame
        
        # Handle circular wrapping
        if end_index >= total_samples:
            frame = np.concatenate((self.full_audio_samples[start_index:], 
                                    self.full_audio_samples[:end_index - total_samples]))
            self.current_sample_index = end_index - total_samples
        else:
            frame = self.full_audio_samples[start_index:end_index]
            self.current_sample_index += self.samples_per_frame

        # --- 2. Process Data (RMS Calculation) ---
        raw_rms = np.sqrt(np.mean(frame.astype(float)**2))
        MAX_16BIT = 32768.0 
        normalized_value = min(raw_rms / MAX_16BIT, 1.0) # Normalized from 0.0 to 1.0
        
        # --- 3. Update View and Send Data ---
        
        # Update the plot visualization
        self.intensity_plot.plot_frame_intensity(raw_rms, normalized_value)
        
        # Send the normalized value to Arduino (Controller passes data to Model)
        self.model.send_data(f"{normalized_value:.4f}") 
        
        # Update status if connection was lost during transmission
        if not self.model.is_serial_connected():
            self.serial_status_label.setText("Serial: Disconnected (Error)")


    # --- GUI EVENT HANDLERS (Controller) ---

    def handle_dropdown_change(self, index):
        """Handles serial port selection and connection attempt."""
        port_name = self.dropdown.currentText()
        
        if port_name.startswith("---"):
            # If the placeholder is selected, disconnect
            self.model.disconnect_serial()
            self.serial_status_label.setText("Serial: Disconnected")
        else:
            # Attempt connection via the Model
            if self.model.connect_serial(port_name):
                self.serial_status_label.setText(f"Serial: Connected to {port_name} @ {SERIAL_BAUDRATE}")
            else:
                self.serial_status_label.setText(f"Serial: FAILED to connect to {port_name}!")
        
    def handle_play_audio_and_plot(self):
        """Toggles audio playback (Play/Pause/Stop) and starts/stops the visualization timer."""
        
        if not self.media_player.source().isValid():
            self.button_play.setText("Audio Error!")
            return

        current_state = self.media_player.playbackState()

        if current_state == QMediaPlayer.PlaybackState.PlayingState:
            # Pause both playback and visualization
            self.media_player.pause()
            self.plot_timer.stop()
        elif current_state == QMediaPlayer.PlaybackState.StoppedState:
            # Start fresh: reset and play both
            self.current_sample_index = 0
            self.media_player.setPosition(0)
            self.media_player.play()
            self.plot_timer.start()
        elif current_state == QMediaPlayer.PlaybackState.PausedState:
            # Resume both playback and visualization
            self.media_player.play()
            self.plot_timer.start()

    def update_play_button_text(self, state):
        """Updates the button text based on the media player's state."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.button_play.setText("⏸️ Pause Audio & Visualize")
        elif state == QMediaPlayer.PlaybackState.StoppedState:
            self.button_play.setText("▶️ Play & Visualize Audio (Loop)")
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.button_play.setText("▶️ Resume Audio & Visualize")
            self.plot_timer.stop() # Ensure timer is stopped when paused


    def handle_demo_button_click(self):
        """Dedicated event handler for the demo button."""
        print("Demo Button clicked!")
        self.button_demo.setText("Demo Clicked!")


    def handle_text_input_change(self, new_text):
        """Event handler for the QLineEdit text change."""
        self.model.set_input_text(new_text)
        self.input_label.setText(f"Input Echo: *{self.model.get_input_text()}*")


# --------------------------------------------------------------------------------------------------

# --- 4. APPLICATION ENTRY POINT ---

if __name__ == "__main__":
    
    if not os.path.exists(LOCAL_AUDIO_FILE_PATH):
        print("\n*** NOTE ON QRC ***")
        print(f"To run successfully, a WAV file must be accessible via the QRC system or named '{os.path.basename(LOCAL_AUDIO_FILE_PATH)}' in this directory (falling back to dummy data if not found).")
        print("*******************\n")

    app = QApplication(sys.argv)
    app_model = AppModel()
    main_window = MainWindow(app_model)
    main_window.show()
    sys.exit(app.exec())
