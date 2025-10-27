from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QPushButton, QComboBox, QLineEdit
)
from PySide6.QtCore import Qt, QSize

# Global constans related to View (not the model)
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Modular PySide6 For Research Projects"
MARGINGS_T = MARGINGS_B = MARGINGS_L = MARGINGS_R = 20
FIXED_HEIGHT = 40
# SPACINGS 
S_SMALL = 8
S_MEDIUM = 16
S_LARGE = 24

class View(QMainWindow):
    """
    Defines the main application window and lays out all GUI widgets.
    """
    def __init__(self, model):
        super().__init__()
        self.model = model # Retain a reference to the model for data access
        
        # --- Window Setup ---
        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(QSize(WINDOW_WIDTH, WINDOW_HEIGHT))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- Layout Setup ---
        layout = QVBoxLayout(central_widget)
        # Align all widgets to the top and left, and let them fill the row width
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft) 
        layout.setContentsMargins(MARGINGS_T, MARGINGS_B, MARGINGS_L, MARGINGS_R )

        # --- Widget Creation ---
        
        # Static Title
        self.title_label = QLabel("Example Modular Architecture")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")

        # Static Text Description
        self.description_label = QLabel("Simple GUI to test MV-C structure and user interactions.")
        self.description_label.setWordWrap(True)
        
        # ComboBox Input
        self.combo_box = QComboBox()
        self.combo_box.setFixedHeight(40)
        self.combo_box.addItems([])
        #self.combo_box.addItems(self.model.get_dropdown_options())
        
        # Mutable Text based on ComboBox
        self.combo_result_label = QLabel("ComboBox Selection: None")
        self.combo_result_label.setObjectName("ComboResultLabel")

        # Text Input Field
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type here...")
        self.text_input.setFixedHeight(FIXED_HEIGHT)

        # Mutable Text: Live Echo
        self.live_echo_label = QLabel("Live Echo: Start typing...")
        self.live_echo_label.setWordWrap(True)
        self.live_echo_label.setObjectName("LiveEchoLabel")

        # Mutable Text: Committed Echo
        self.committed_echo_label = QLabel(f"Committed Text (ENTER): {self.model.get_committed_input_text()}")
        self.committed_echo_label.setWordWrap(True)
        self.committed_echo_label.setObjectName("CommittedEchoLabel")
        
        # Button A
        self.button_a = QPushButton("Button A: Print to Console")
        self.button_a.setFixedHeight(FIXED_HEIGHT)

        # Button B
        self.button_b = QPushButton("Button B: Print to Console")
        self.button_b.setFixedHeight(FIXED_HEIGHT)

        # --- Widget Stacking (View Layout) ---
        layout.addWidget(self.title_label)
        layout.addSpacing(S_SMALL)
        layout.addWidget(self.description_label)
        layout.addSpacing(S_MEDIUM)
        
        layout.addWidget(self.combo_box)
        layout.addWidget(self.combo_result_label)
        layout.addSpacing(S_SMALL)

        layout.addWidget(self.text_input)
        layout.addWidget(self.live_echo_label)
        layout.addWidget(self.committed_echo_label)
        layout.addSpacing(S_SMALL)

        layout.addWidget(self.button_a)
        layout.addWidget(self.button_b)
        
        # Add a stretch at the bottom to push everything to the top
        layout.addStretch()
