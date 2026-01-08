"""
Main Window Module for OptiSend
"""

import os
import csv
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QFileDialog, QProgressBar,
    QMessageBox, QSpinBox, QFrame, QScrollArea, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QDialogButtonBox, QTabWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QIcon
from whatsapp_bot import WhatsAppBot


class AddContactDialog(QDialog):
    """Dialog for adding a single contact"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Contact")
        self.setFixedSize(400, 200)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setFixedWidth(80)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter contact name")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Phone input
        phone_layout = QHBoxLayout()
        phone_label = QLabel("Phone:")
        phone_label.setFixedWidth(80)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("e.g., 0241234567")
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)

        # Info label
        info = QLabel("💡 Phone format: 0241234567 or 233241234567")
        info.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(info)

        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def validate_and_accept(self):
        """Validate inputs before accepting"""
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a name.")
            return

        if not phone:
            QMessageBox.warning(self, "Invalid Input", "Please enter a phone number.")
            return

        # Basic phone validation
        phone_digits = ''.join(filter(str.isdigit, phone))
        if len(phone_digits) < 9:
            QMessageBox.warning(self, "Invalid Phone", "Phone number is too short.")
            return

        self.accept()

    def get_contact(self):
        """Return the contact data"""
        return {
            'name': self.name_input.text().strip(),
            'phone': self.phone_input.text().strip()
        }


class MainWindow(QMainWindow):
    """Main application window with modern UI"""

    def __init__(self):
        super().__init__()
        self.csv_file = None
        self.manual_contacts = []  # Store manually added contacts
        self.bot = None

        self.setWindowTitle("OptiSend - WhatsApp Bulk Messaging Platform")
        self.setMinimumSize(1100, 800)

        # Apply modern stylesheet
        self.apply_stylesheet()

        # Setup UI
        self.init_ui()

    def apply_stylesheet(self):
        """Apply modern dark-theme stylesheet"""
        stylesheet = """
        QMainWindow {
            background-color: #f5f5f5;
        }

        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }

        QLabel {
            color: #333333;
        }

        QPushButton {
            background-color: #60a5fa;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
        }

        QPushButton:hover {
            background-color: #3b82f6;
        }

        QPushButton:pressed {
            background-color: #2563eb;
        }

        QPushButton:disabled {
            background-color: #d1d5db;
            color: #9ca3af;
        }

        QTextEdit, QLineEdit {
            background-color: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 12px;
            color: #333333;
        }

        QTextEdit:focus, QLineEdit:focus {
            border: 2px solid #60a5fa;
        }

        QProgressBar {
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            text-align: center;
            background-color: #f3f4f6;
            height: 24px;
        }

        QProgressBar::chunk {
            background-color: #10b981;
            border-radius: 5px;
        }

        QSpinBox {
            background-color: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 8px;
            color: #333333;
        }

        QSpinBox:focus {
            border: 2px solid #60a5fa;
        }

        QTableWidget {
            background-color: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            gridline-color: #e5e7eb;
        }

        QTableWidget::item {
            padding: 8px;
        }

        QTableWidget::item:selected {
            background-color: #dbeafe;
            color: #1e40af;
        }

        QHeaderView::section {
            background-color: #f8fafc;
            padding: 10px;
            border: none;
            border-bottom: 2px solid #e5e7eb;
            font-weight: bold;
            color: #475569;
        }

        QTabWidget::pane {
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            background-color: white;
        }

        QTabBar::tab {
            background-color: #f1f5f9;
            color: #64748b;
            padding: 12px 24px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 4px;
        }

        QTabBar::tab:selected {
            background-color: white;
            color: #1e293b;
            font-weight: bold;
        }

        QTabBar::tab:hover {
            background-color: #e2e8f0;
        }

        .card {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
        }

        .header {
            background-color: #1e293b;
            padding: 20px;
        }
        """
        self.setStyleSheet(stylesheet)

    def init_ui(self):
        """Initialize the user interface"""
        # Main container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header section
        header = self.create_header()
        main_layout.addWidget(header)

        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Contacts Card (with tabs for CSV and Manual)
        contacts_card = self.create_contacts_card()
        content_layout.addWidget(contacts_card)

        # Message Template Card
        message_card = self.create_message_card()
        content_layout.addWidget(message_card)

        # Settings Card
        settings_card = self.create_settings_card()
        content_layout.addWidget(settings_card)

        # Action Card
        action_card = self.create_action_card()
        content_layout.addWidget(action_card)

        # Log Card
        log_card = self.create_log_card()
        content_layout.addWidget(log_card)

        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)

    def create_header(self):
        """Create application header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e293b,
                    stop:1 #334155
                );
                padding: 20px;
            }
        """)

        header_layout = QHBoxLayout(header_frame)

        # Logo
        logo_label = QLabel()
        if os.path.exists("optimus.png"):
            pixmap = QPixmap("optimus.png")
            scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("📨")
            logo_label.setStyleSheet("font-size: 40px;")

        header_layout.addWidget(logo_label)

        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title_label = QLabel("OptiSend")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")

        subtitle_label = QLabel("WhatsApp Bulk Messaging Platform")
        subtitle_label.setStyleSheet("color: #94a3b8; font-size: 13px;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Status indicator
        status_label = QLabel("● Ready")
        status_label.setStyleSheet("color: #10b981; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(status_label)

        return header_frame

    def create_card(self, title):
        """Create a styled card container"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Card title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        layout.addWidget(title_label)

        return card, layout

    def create_contacts_card(self):
        """Create contacts management card with tabs"""
        card, layout = self.create_card("👥 Contact Management")

        # Tab widget
        tab_widget = QTabWidget()

        # Tab 1: CSV Import
        csv_tab = QWidget()
        csv_layout = QVBoxLayout(csv_tab)
        csv_layout.setContentsMargins(15, 15, 15, 15)

        info_label = QLabel("Import contacts from a CSV file (columns: name, number)")
        info_label.setStyleSheet("color: #64748b; font-size: 12px;")
        csv_layout.addWidget(info_label)

        file_layout = QHBoxLayout()
        self.csv_label = QLabel("No file selected")
        self.csv_label.setStyleSheet("color: #94a3b8; font-style: italic;")
        file_layout.addWidget(self.csv_label)
        file_layout.addStretch()

        select_btn = QPushButton("📂 Browse Files")
        select_btn.setFixedWidth(150)
        select_btn.clicked.connect(self.select_csv)
        file_layout.addWidget(select_btn)
        csv_layout.addLayout(file_layout)

        # Tab 2: Manual Entry
        manual_tab = QWidget()
        manual_layout = QVBoxLayout(manual_tab)
        manual_layout.setContentsMargins(15, 15, 15, 15)

        info_label2 = QLabel("Add contacts manually one by one")
        info_label2.setStyleSheet("color: #64748b; font-size: 12px;")
        manual_layout.addWidget(info_label2)

        # Contacts table
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(2)
        self.contacts_table.setHorizontalHeaderLabels(["Name", "Phone Number"])
        self.contacts_table.horizontalHeader().setStretchLastSection(True)
        self.contacts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.contacts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.contacts_table.setMinimumHeight(200)
        manual_layout.addWidget(self.contacts_table)

        # Buttons for manual entry
        button_layout = QHBoxLayout()

        add_contact_btn = QPushButton("➕ Add Contact")
        add_contact_btn.clicked.connect(self.add_contact_dialog)
        button_layout.addWidget(add_contact_btn)

        remove_contact_btn = QPushButton("➖ Remove Selected")
        remove_contact_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        remove_contact_btn.clicked.connect(self.remove_selected_contact)
        button_layout.addWidget(remove_contact_btn)

        clear_all_btn = QPushButton("🗑Clear All")
        clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        clear_all_btn.clicked.connect(self.clear_all_contacts)
        button_layout.addWidget(clear_all_btn)

        button_layout.addStretch()

        # Export button
        export_btn = QPushButton("Export to CSV")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        export_btn.clicked.connect(self.export_contacts_to_csv)
        button_layout.addWidget(export_btn)

        manual_layout.addLayout(button_layout)

        # Contact count
        self.contact_count_label = QLabel("Total Contacts: 0")
        self.contact_count_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold;")
        manual_layout.addWidget(self.contact_count_label)

        # Add tabs
        tab_widget.addTab(csv_tab, "CSV Import")
        tab_widget.addTab(manual_tab, "Manual Entry")

        layout.addWidget(tab_widget)

        return card

    def create_message_card(self):
        """Create message template card"""
        card, layout = self.create_card("Message Template")

        # Info text
        info_label = QLabel("Compose your message. Use {name} for personalization.")
        info_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(info_label)

        # Message editor
        self.message_box = QTextEdit()
        self.message_box.setPlaceholderText("Write your message here...")
        self.message_box.setMinimumHeight(200)
        self.message_box.setText(
            "Hi {name} 👋\n\n"
            "📢 Meet *HomeBoss*\n\n"
            "HomeBoss is a smart home automation solution that lets you control "
            "lights, doors, and security from your phone.\n\n"
            "Built for modern African homes 🇬🇭\n\n"
            "👉 Please follow our WhatsApp channel:\n"
            "https://whatsapp.com/channel/0029VbCBWya0AgWB2ixLAK17\n\n"
            "Thank you 🙏"
        )
        layout.addWidget(self.message_box)

        # Character count
        self.char_label = QLabel("Characters: 0")
        self.char_label.setStyleSheet("color: #64748b; font-size: 11px;")
        self.message_box.textChanged.connect(self.update_char_count)
        layout.addWidget(self.char_label)
        self.update_char_count()

        return card

    def create_settings_card(self):
        """Create settings card"""
        card, layout = self.create_card("Settings")

        # Delay setting
        delay_layout = QHBoxLayout()

        delay_label = QLabel("Delay between messages:")
        delay_label.setStyleSheet("color: #475569;")
        delay_layout.addWidget(delay_label)

        self.delay_spin = QSpinBox()
        self.delay_spin.setMinimum(3)
        self.delay_spin.setMaximum(60)
        self.delay_spin.setValue(5)
        self.delay_spin.setSuffix(" seconds")
        self.delay_spin.setFixedWidth(150)
        delay_layout.addWidget(self.delay_spin)

        delay_layout.addStretch()

        layout.addLayout(delay_layout)

        return card

    def create_action_card(self):
        """Create action buttons card"""
        card, layout = self.create_card("Actions")

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        # Buttons
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Campaign")
        self.start_btn.clicked.connect(self.start_sending)
        self.start_btn.setMinimumHeight(45)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(45)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)

        return card

    def create_log_card(self):
        """Create activity log card"""
        card, layout = self.create_card("Activity Log")

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(200)
        self.log_box.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.log_box)

        return card

    def create_footer(self):
        """Create application footer"""
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-top: 1px solid #e5e7eb;
                padding: 15px;
            }
        """)

        footer_layout = QHBoxLayout(footer_frame)

        brand_label = QLabel("Developed by Optimus Tech")
        brand_label.setStyleSheet("color: #64748b; font-size: 12px;")
        footer_layout.addWidget(brand_label)

        footer_layout.addStretch()

        version_label = QLabel("Version 2.0")
        version_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        footer_layout.addWidget(version_label)

        return footer_frame

    # Contact Management Methods

    def add_contact_dialog(self):
        """Show dialog to add a contact"""
        dialog = AddContactDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            contact = dialog.get_contact()
            self.add_contact_to_table(contact['name'], contact['phone'])
            self.log(f"➕ Added contact: {contact['name']} ({contact['phone']})")

    def add_contact_to_table(self, name, phone):
        """Add a contact to the table"""
        row = self.contacts_table.rowCount()
        self.contacts_table.insertRow(row)

        self.contacts_table.setItem(row, 0, QTableWidgetItem(name))
        self.contacts_table.setItem(row, 1, QTableWidgetItem(phone))

        # Update manual contacts list
        self.manual_contacts.append({'name': name, 'phone': phone})
        self.update_contact_count()

    def remove_selected_contact(self):
        """Remove selected contact from table"""
        selected_rows = self.contacts_table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a contact to remove.")
            return

        # Remove from bottom to top to avoid index issues
        for index in sorted(selected_rows, reverse=True):
            row = index.row()
            self.contacts_table.removeRow(row)
            del self.manual_contacts[row]

        self.update_contact_count()
        self.log(f"➖ Removed {len(selected_rows)} contact(s)")

    def clear_all_contacts(self):
        """Clear all contacts from table"""
        if self.contacts_table.rowCount() == 0:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to remove all contacts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.contacts_table.setRowCount(0)
            self.manual_contacts.clear()
            self.update_contact_count()
            self.log("🗑️ All contacts cleared")

    def export_contacts_to_csv(self):
        """Export manual contacts to CSV file"""
        if not self.manual_contacts:
            QMessageBox.information(self, "No Contacts", "No contacts to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Contacts",
            "contacts.csv",
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['name', 'number'])
                    writer.writeheader()
                    for contact in self.manual_contacts:
                        writer.writerow({'name': contact['name'], 'number': contact['phone']})

                self.log(f"💾 Exported {len(self.manual_contacts)} contacts to {os.path.basename(file_path)}")
                QMessageBox.information(self, "Export Successful", f"Contacts exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export contacts:\n{str(e)}")

    def update_contact_count(self):
        """Update contact count label"""
        count = len(self.manual_contacts)
        self.contact_count_label.setText(f"Total Contacts: {count}")

    def log(self, message):
        """Add message to activity log"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.append(f"[{timestamp}] {message}")
        self.log_box.ensureCursorVisible()

    def update_char_count(self):
        """Update character count"""
        text = self.message_box.toPlainText()
        count = len(text)
        self.char_label.setText(f"Characters: {count}")

    def select_csv(self):
        """Handle CSV file selection"""
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Contacts CSV", "", "CSV Files (*.csv)"
        )
        if file:
            self.csv_file = file
            filename = os.path.basename(file)
            self.csv_label.setText(f"✓ {filename}")
            self.csv_label.setStyleSheet("color: #10b981; font-weight: bold;")
            self.log(f"CSV file loaded: {filename}")

    def start_sending(self):
        """Start the messaging campaign"""
        # Determine contact source
        has_csv = self.csv_file is not None
        has_manual = len(self.manual_contacts) > 0

        if not has_csv and not has_manual:
            QMessageBox.warning(
                self,
                "No Contacts",
                "Please either:\n• Import a CSV file, or\n• Add contacts manually"
            )
            return

        message = self.message_box.toPlainText().strip()
        if not message:
            QMessageBox.warning(
                self,
                "No Message",
                "Please enter a message template."
            )
            return

        # Determine which contacts to use
        if has_csv and has_manual:
            reply = QMessageBox.question(
                self,
                "Contact Source",
                "You have both CSV and manual contacts.\n\nWhich contacts would you like to use?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            )
            # Custom button text would be ideal, but using Yes=Manual, No=CSV, Cancel=Both
            msg = QMessageBox(self)
            msg.setWindowTitle("Contact Source")
            msg.setText("You have both CSV and manual contacts.\n\nWhich would you like to use?")
            msg.addButton("Manual Contacts", QMessageBox.ButtonRole.YesRole)
            msg.addButton("CSV File", QMessageBox.ButtonRole.NoRole)
            msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            result = msg.exec()

            if result == 2:  # Cancel
                return
            use_manual = (result == 0)  # Manual
        elif has_manual:
            use_manual = True
        else:
            use_manual = False

        # Confirm
        contact_source = "manual contacts" if use_manual else "CSV file"
        contact_count = len(self.manual_contacts) if use_manual else "all contacts in"

        reply = QMessageBox.question(
            self,
            "Confirm Campaign",
            f"Start sending messages to {contact_count} {contact_source}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Disable controls
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Prepare contacts
        if use_manual:
            # Create temporary CSV for manual contacts
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='')
            writer = csv.DictWriter(temp_file, fieldnames=['name', 'number'])
            writer.writeheader()
            for contact in self.manual_contacts:
                writer.writerow({'name': contact['name'], 'number': contact['phone']})
            temp_file.close()
            csv_to_use = temp_file.name
        else:
            csv_to_use = self.csv_file

        # Create and start bot
        self.bot = WhatsAppBot(
            csv_file=csv_to_use,
            message_template=message,
            delay=self.delay_spin.value(),
            log_callback=self.log,
            progress_callback=self.update_progress,
            finished_callback=self.sending_finished
        )

        self.bot.start()
        self.log("Campaign started!")

    def update_progress(self, current, total):
        """Update progress bar"""
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.progress.setFormat(f"{current}/{total} messages sent")

    def sending_finished(self):
        """Handle campaign completion"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log("Campaign completed!")

        QMessageBox.information(
            self,
            "Campaign Complete",
            "All messages have been processed successfully!"
        )


import time