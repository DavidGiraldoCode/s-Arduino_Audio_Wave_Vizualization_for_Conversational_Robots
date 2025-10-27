import sys
# Import Model and View classes from their respective files
from model import AppModel 
from view import View
from PySide6.QtWidgets import QApplication


class AppController:
    """
    The main controller for the application. 
    Manages initialization, signal connections, and event handling logic.
    """
    def __init__(self):
        # 1. Initialize Model and View
        self.model = AppModel()
        self.view = View(self.model)
        
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
        self.view.text_input.setEnabled(False)
        
        # 3. Print example data transmission to console (e.g., sending data to Arduino)
        print(f"CONTROLLER: Committing and Sending data: '{committed_text}'")
        self.model.send_data(committed_text)

    def handle_button_a_click(self):
        """Example handler for Button A."""
        print("CONTROLLER: Button A clicked. Executing application action.")
        self.view.text_input.setEnabled(True)
        self.view.text_input.setPlaceholderText("Type here...")
        self.view.text_input.value = ""
        self.model.set_committed_input_text("")
        ##TODO: Make the text input reset


    def handle_button_b_click(self):
        """Example handler for Button B."""
        print("CONTROLLER: Button B clicked. Executing application action.")
        self.model.send_data(0)

    # =====================================================================
    # =====================================================================
    # ----- Application Specific Event Handlers (not OS related)
    # =====================================================================
    # =====================================================================

    def on_commited_value_change(self):
        print("The slot is reacting to the change!")

    def on_cleared_input_text(self):
        print("The input field has been cleared!")

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
