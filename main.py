"""Business Card Generator - Main Entry Point.

This module provides the entry point for the Business Card Generator application.
It initializes the Qt application and displays the main window.
"""

import sys
from PySide6.QtWidgets import QApplication

from src.business_card_generator.ui.main_window import MainWindow


def main():
    """Run the Business Card Generator application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Business Card Generator")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
