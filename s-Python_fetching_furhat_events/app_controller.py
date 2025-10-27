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

    # --- Controller Event Handlers (Logic) ---

    def handle_combobox_change(self, index):
        """Updates the Model state and the View label based on the new ComboBox selection."""
        selected_text = self.view.combo_box.currentText()
        
        # 1. Update the Model (if necessary for the actual application logic)
        # Example: self.model.connect_serial(selected_text) 
        
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
        
        # 3. Print example data transmission to console (e.g., sending data to Arduino)
        print(f"CONTROLLER: Committing and Sending data: '{committed_text}'")
        self.model.send_data(committed_text)

    def handle_button_a_click(self):
        """Example handler for Button A."""
        print("CONTROLLER: Button A clicked. Executing application action.")

    def handle_button_b_click(self):
        """Example handler for Button B."""
        print("CONTROLLER: Button B clicked. Executing application action.")

    def show(self):
        """Displays the main window."""
        self.view.show()
