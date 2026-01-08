"""
Splash Screen Module for OptiSend
"""

import os
from PyQt6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont


class SplashScreen(QSplashScreen):
    """Custom splash screen with loading animation"""

    def __init__(self):
        # Create a custom pixmap for splash background
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(18, 18, 18))  # Dark background

        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # Setup UI
        self.setup_ui()

        # Start progress animation
        self.progress_value = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(40)

    def setup_ui(self):
        """Setup splash screen UI elements"""
        # Try to load logo
        logo_path = "optimus.png"

        # Create message with logo or text
        if os.path.exists(logo_path):
            message = f'<div align="center">'
            message += f'<img src="{logo_path}" width="200"><br><br>'
            message += '<span style="color: #ffffff; font-size: 24px; font-weight: bold;">OptiSend</span><br>'
            message += '<span style="color: #a0a0a0; font-size: 14px;">WhatsApp Bulk Messaging Platform</span><br><br>'
            message += '<span style="color: #60a5fa; font-size: 12px;">Developed by Optimus Tech</span>'
            message += '</div>'
        else:
            message = '<div align="center">'
            message += '<span style="color: #ffffff; font-size: 32px; font-weight: bold;">OptiSend</span><br><br>'
            message += '<span style="color: #a0a0a0; font-size: 16px;">WhatsApp Bulk Messaging Platform</span><br><br>'
            message += '<span style="color: #60a5fa; font-size: 14px;">Developed by Optimus Tech</span>'
            message += '</div>'

        self.showMessage(
            message,
            Qt.AlignmentFlag.AlignCenter,
            QColor(255, 255, 255)
        )

    def update_progress(self):
        """Animate loading progress"""
        self.progress_value += 2

        # Create progress indicator at bottom
        loading_text = "●" * (self.progress_value // 20)
        progress_message = f'<div align="center" style="margin-top: 300px;">'
        progress_message += f'<span style="color: #60a5fa; font-size: 16px;">{loading_text}</span>'
        progress_message += '</div>'

        if self.progress_value >= 100:
            self.timer.stop()

    def drawContents(self, painter):
        """Custom draw to add gradient effect"""
        super().drawContents(painter)

        # Draw subtle gradient overlay
        painter.setOpacity(0.1)
        gradient_rect = self.rect()
        painter.fillRect(gradient_rect, QColor(96, 165, 250))