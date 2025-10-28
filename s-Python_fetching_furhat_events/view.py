# NOTE: This should be defined as a standalone class, e.g., AudioIntensityCanvas, 
# likely residing in its own file or at the top of view.py

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QPushButton, QComboBox, QLineEdit
)
from PySide6.QtCore import Qt, QSize

# Global constans related to View (not the model)
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Modular PySide6 For Research Projects"
MARGINGS_T = MARGINGS_B = MARGINGS_L = MARGINGS_R = 20
FIXED_HEIGHT = 40
# SPACINGS 
S_SMALL = 8
S_MEDIUM = 16
S_LARGE = 24


#TODO Move this to another file
# Background color for the plot (dark theme) - Assuming this constant is available
PLOT_BG_COLOR = "#323232" 

class AudioIntensityCanvas(QWidget):
    """A custom widget using Matplotlib to show two real-time intensity bars."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize the Figure and Canvas with the dark background
        self.figure = Figure(figsize=(4, 3), facecolor=PLOT_BG_COLOR)
        self.canvas = FigureCanvas(self.figure)
        
        # Expose the layout for the figure
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialize the single subplot
        self.ax = self.figure.add_subplot(111)
        
        # Initialize the bar containers
        self.bar_raw = None
        self.bar_norm = None
        
        self.init_plot_style()

    # --- Function Definition (Plotting Interface) ---
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
        Public interface: Updates the two intensity bars with new values.
        """
        if not self.bar_raw or not self.bar_norm:
            return

        # 1. Raw Bar Update: Scale raw RMS value for display
        raw_display_value = min(raw_value / 32768.0, 1.1)
        self.bar_raw[0].set_height(raw_display_value)
        
        # 2. Normalized Bar Update: Clamped between 0.0 and 1.0
        self.bar_norm[0].set_height(normalized_value)
        
        # Optional: Change color for visual feedback
        # if normalized_value >= 0.95:
        #      self.bar_norm[0].set_color('red')
        # else:
        #      self.bar_norm[0].set_color('lime')

        # Redraw the canvas for a real-time effect
        self.canvas.draw()


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
        self.layout = QVBoxLayout(central_widget)
        #self.layout = QVBoxLayout(central_widget)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.setContentsMargins(10, 10, 10, 10)
        # Align all widgets to the top and left, and let them fill the row width
        #layout.setAlignment(Qt.AlignTop | Qt.AlignLeft) 
        #layout.setContentsMargins(MARGINGS_T, MARGINGS_B, MARGINGS_L, MARGINGS_R )

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

        # Mutable Text: Async Echo
        self.async_status_label = QLabel("Waiting for an async call...⏳")
        self.async_status_label.setWordWrap(True)
        self.async_status_label.setObjectName("AsyncCallEchoLabel")
        
        # Button A
        self.button_a = QPushButton("Button A: Print to Console")
        self.button_a.setFixedHeight(FIXED_HEIGHT)

        # Button B
        self.button_b = QPushButton("Button B: Print to Console")
        self.button_b.setFixedHeight(FIXED_HEIGHT)

        self.button_c = QPushButton("Async call")
        self.button_c.setFixedHeight(FIXED_HEIGHT)

        # --- Widget Stacking (View Layout) ---
        self.layout.addWidget(self.title_label)
        self.layout.addSpacing(S_SMALL)
        self.layout.addWidget(self.description_label)
        self.layout.addSpacing(S_MEDIUM)
        
        self.layout.addWidget(self.combo_box)
        self.layout.addWidget(self.combo_result_label)
        self.layout.addSpacing(S_SMALL)

        self.layout.addWidget(self.text_input)
        self.layout.addWidget(self.live_echo_label)
        self.layout.addWidget(self.committed_echo_label)
        self.layout.addSpacing(S_SMALL)

        self.layout.addWidget(self.button_a)
        self.layout.addWidget(self.button_b)
        self.layout.addWidget(self.async_status_label)
        self.layout.addWidget(self.button_c)
        
        # Add a stretch at the bottom to push everything to the top
        self.layout.addStretch()

        # Controlling the Audio canvas
        # Placeholder for Canvas (Controller will insert it at index 0 later)
        self.intensity_plot = None 
