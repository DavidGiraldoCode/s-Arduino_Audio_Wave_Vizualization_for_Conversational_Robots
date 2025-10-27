import sys
from PySide6.QtWidgets import QApplication
from app_controller import AppController 


def main():
    """
    Application entry point. Initializes the Qt environment and the AppController.
    """
    # 1. Initialize the Qt Application instance
    app = QApplication(sys.argv)
    
    # 2. Initialize the Controller (which handles Model and View creation)
    controller = AppController()
    
    # 3. Show the main window (View)
    controller.show()
    
    # 4. Start the Qt event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
