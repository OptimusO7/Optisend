"""
OptiSend - Professional WhatsApp Bulk Messaging Platform
Developed by Optimus Tech
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from splash_screen import SplashScreen
from main_window import MainWindow


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("OptiSend")
    app.setOrganizationName("Optimus Tech")

    # Set application-wide style
    app.setStyle("Fusion")

    # Create and show splash screen
    splash = SplashScreen()
    splash.show()

    # Process events to ensure splash is displayed
    app.processEvents()

    # Initialize main window (but don't show yet)
    main_window = MainWindow()

    # Close splash and show main window after delay
    def show_main_window():
        splash.finish(main_window)
        main_window.show()

    # Show main window after 4 seconds
    QTimer.singleShot(4000, show_main_window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()