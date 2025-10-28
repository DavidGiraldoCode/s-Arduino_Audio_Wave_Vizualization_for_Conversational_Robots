import sys

import numpy as np

from PySide6.QtCore import QTimer, QSize, Qt, QUrl, QModelIndex
from PySide6.QtWidgets import QApplication

# Import Model and View classes from their respective files
from model import AppModel 
from view import AudioIntensityCanvas, View

# --- GLOBAL CONSTANTS ---
PLOT_UPDATE_INTERVAL = 50 # 50ms = 20 FPS
ASSET_AUDIO_URL = "audio_test.wav" 

class AppController:
    """
    The main controller for the application. 
    Manages initialization, signal connections, and event handling logic.
    """
    def __init__(self):
        # 1. Initialize Model and View -----------------------------------------------
        self.model = AppModel()
        self.view = View(self.model)

        #----------------------------------------------- Audio debugging
        # 2. Instantiate and attach the Matplotlib Canvas
        self.view.intensity_plot = AudioIntensityCanvas()
        # Insert the canvas at the top of the layout (index 0)
        self.view.layout.insertWidget(0, self.view.intensity_plot) 

        # 3. Load Audio Data and Set Frame Pointers (CORRECTED DATA ASSIGNMENT)
        self.sample_rate, self.full_audio_samples = self.model.load_audio_samples(ASSET_AUDIO_URL)
        
        if self.full_audio_samples.size > 0:
            # Calculate frame size based on update interval
            self.samples_per_frame = int(self.sample_rate * (PLOT_UPDATE_INTERVAL / 1000.0))
        else:
            self.samples_per_frame = 1 # Safe fallback if no data loaded

        self.current_sample_index = 0
        # 4. Initialize QTimer
        self.plot_timer = QTimer()
        self.plot_timer.setInterval(PLOT_UPDATE_INTERVAL)
        # The CONNECTION: Established in __init__
        self.plot_timer.timeout.connect(self.update_live_bar)
        #-----------------------------------------------
        
        # 2. Connect all signals from the View to the Controller's handler methods
        self._connect_signals()

        # 3. Initialize Serial Communicatiom
        self.assign_numbered_serial_ports_to_combo_box()



    def _connect_signals(self):
        """
        Connects signals from the View widgets to the appropriate controller methods (slots).
        This is where event handlers are defined.
        """
        
        # ComboBox: Whenever the selected item changes
        self.view.combo_box.currentIndexChanged.connect(self.handle_combobox_change)

        # QLineEdit: 
        # 1. Text changes (live typing)
        self.view.text_input.textChanged.connect(self.handle_live_input_change)
        # 2. Editing finished (User presses ENTER or focus leaves)
        self.view.text_input.returnPressed.connect(self.handle_input_commit)
        
        # Buttons: Click events
        self.view.button_a.clicked.connect(self.handle_button_a_click)
        self.view.button_b.clicked.connect(self.handle_button_b_click)

        # Application specific events Slot (Event Handler)
        self.model.input_text_commited.connect(self.on_commited_value_change)
        self.model.input_text_cleared.connect(self.on_cleared_input_text)

    # =====================================================================
    # =====================================================================
    # --- Controller Event Handlers (Logic) ---
    # =====================================================================
    # =====================================================================

    def handle_combobox_change(self, index):
        """Updates the Model state and the View label based on the new ComboBox selection."""
        selected_text = self.view.combo_box.currentText()
        
        # 1. Update the Model (if necessary for the actual application logic)
        # Example: self.model.connect_serial(selected_text)
        if selected_text == "":
            self.model.disconnect_serial()
            return
        
        print(f"Its going to connect to {selected_text}")
        self.model.connect_serial(selected_text)

        # 2. Update the View's mutable label
        self.view.combo_result_label.setText(f"ComboBox Selection: {selected_text}")

    def handle_live_input_change(self, new_text):
        """Updates the Model state and the live echo label as the user types."""
        # 1. Update the Model (Live state)
        self.model.set_live_input_text(new_text)
        
        # 2. Update the View's live echo label
        self.view.live_echo_label.setText(f"Live Echo: *{self.model.get_live_input_text()}*")

    def handle_input_commit(self):
        """Updates the Model state and the committed text label when ENTER is pressed."""
        committed_text = self.view.text_input.text()
        
        # 1. Update the Model (Committed state)
        self.model.set_committed_input_text(committed_text)
        
        # 2. Update the View's committed echo label
        self.view.committed_echo_label.setText(f"Committed Text (ENTER): {self.model.get_committed_input_text()}")
        #self.view.text_input.setEnabled(False)
        
        # 3. Print example data transmission to console (e.g., sending data to Arduino)
        print(f"CONTROLLER: Committing and Sending data: '{committed_text}'")
        self.model.send_data(committed_text)
        

    def handle_button_a_click(self):
        """
        Toggles the QTimer loop (starting and stopping the audio visualization).
        (FIXED: This now correctly manages the QTimer)
        """
        if self.plot_timer.isActive():
            self.plot_timer.stop()
            self.view.button_a.setText("▶️ Start Audio Plot")
            print("CONTROLLER: Audio visualization paused.")
        else:
            # Reset the index to start from the beginning of the file
            self.current_sample_index = 0
            self.plot_timer.start()
            self.view.button_a.setText("⏸️ Pause Audio Plot")
            print("CONTROLLER: Audio visualization started.")
            
        """Example handler for Button A.
        print("CONTROLLER: Button A clicked. Executing application action.")
        self.view.text_input.setEnabled(True)
        self.view.text_input.setPlaceholderText("Type here...")
        self.view.text_input.value = ""
        self.model.set_committed_input_text("")"""
        ##TODO: Make the text input reset


    def handle_button_b_click(self):
        """Example handler for Button B."""
        print("CONTROLLER: Button B clicked. Executing application action.")
        self.model.send_data(180)

    # =====================================================================
    # =====================================================================
    # ----- Application Specific Event Handlers (not OS related)
    # =====================================================================
    # =====================================================================

    def on_commited_value_change(self):
        print("The slot is reacting to the change!")

    def on_cleared_input_text(self):
        print("The input field has been cleared!")

    # ======== 
    # --- Audio Visualization

    def update_live_bar(self):
        """
        Processes the next frame of audio data, updates the visualization,
        and sends the normalized intensity over serial.
        (This method is connected to the QTimer's timeout signal).
        """
        
        # Ensure we have data
        total_samples = len(self.full_audio_samples)
        if total_samples == 0 or self.full_audio_samples.size == 0:
            self.view.intensity_plot.plot_frame_intensity(0, 0)
            return

        # 1. Retrieve Raw Audio Frame (Simulation of Input Stream)
        start_index = self.current_sample_index
        end_index = start_index + self.samples_per_frame
        
        # Handle circular wrapping
        if end_index >= total_samples:
            # Logic to wrap the frame back to the start of the audio array
            frame = np.concatenate((self.full_audio_samples[start_index:], 
                                    self.full_audio_samples[:end_index - total_samples]))
            self.current_sample_index = end_index - total_samples
        else:
            frame = self.full_audio_samples[start_index:end_index]
            self.current_sample_index += self.samples_per_frame

        # 2. Process Data (RMS Calculation & Normalization)
        # Note: Must handle potential conversion to float/int types
        raw_rms = np.sqrt(np.mean(frame.astype(float)**2))
        MAX_16BIT = 32768.0 
        normalized_value = min(raw_rms / MAX_16BIT, 1.0) # Normalized from 0.0 to 1.0
        
        # 3. Update View and Send Data to Model
        
        # A. Update View: Pass raw and normalized values to the plotter
        self.view.intensity_plot.plot_frame_intensity(raw_rms, normalized_value)

        # 4. Send to Arduino through the Serial port
        rgd_bounded_val = int(normalized_value * 255)
        self.model.send_data(rgd_bounded_val)

    # =====================================================================
    # =====================================================================
    # ------ Serial Communication
    # =====================================================================
    # =====================================================================

    def assign_numbered_serial_ports_to_combo_box(self):
        """
        Retrieves ports from the Model and formats/prints them to the console.

        Architecture Rationale: The Controller orchestrates the process:
        1. It requests data from the Model (Model's job).
        2. It performs presentation formatting (Controller/View's job).
        3. It directs the output (e.g., print to console, or update a QLabel).
        """
        # 1. Get raw port list from the Model
        port_list = self.model.get_available_ports()

        print("\n--- Available Serial Ports ---")
        
        if not port_list:
            print("No serial ports found.")
            return

        # 2. Format the output with indexing (Controller's responsibility)
        for index, port_name in enumerate(port_list):
            print(f"{index} {port_name}")
        
        self.view.combo_box.addItems([""] + port_list)
        print("------------------------------\n")

    # ------

    def show(self):
        """Displays the main window."""
        self.view.show()
