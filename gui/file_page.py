from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QSpacerItem, QSizePolicy, QCheckBox,
    QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer
from pathlib import Path
from mylibs.settings import load_settings, save_settings


class FilePage(QWidget):
    def __init__(self, parent=None, on_file_selected=None):
        super().__init__(parent)
        self.parent = parent
        self.on_file_selected = on_file_selected

        # Load settings
        self.settings = load_settings()

        # # Top-right reload button
        # reload_btn = QPushButton("🔄 Reload App")
        # reload_btn.setFixedSize(140, 35)
        # reload_btn.setStyleSheet(self.button_style("#e74c3c", "#c0392b"))
        # reload_btn.clicked.connect(self.reload_app)
        #
        # # Add to a horizontal layout to push it to the right
        # top_row = QHBoxLayout()
        # top_row.addStretch()
        # top_row.addWidget(reload_btn)
        # self.setLayout(QVBoxLayout())  # wrap outer layout with new top_row
        # self.layout().addLayout(top_row)
        # self.layout().addLayout(outer_layout)

        # Outer layout
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        outer_layout.setSpacing(30)

        # --- File selection section ---
        file_section = QVBoxLayout()
        file_section.setSpacing(15)
        file_section.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        file_title = QLabel("📂 Select a Log File to Analyze")
        file_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_title.setStyleSheet("font-size: 26px; font-weight: bold;")
        file_section.addWidget(file_title)


        last_file = self.settings.get("last_file", "")

        # File path input
        self.file_input = QLineEdit()

        if last_file and Path(last_file).is_file():
            self.file_input.setText(last_file)
        self.file_input.setPlaceholderText("Path to log file...")

        self.file_input.setFixedWidth(600)
        self.file_input.setStyleSheet("font-size: 16px; padding: 6px;")
        self.file_input.textChanged.connect(self.update_select_button)
        file_section.addWidget(self.file_input, alignment=Qt.AlignmentFlag.AlignCenter)


        # Buttons row
        button_row = QHBoxLayout()
        button_row.setSpacing(20)
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setFixedSize(160, 45)
        self.browse_btn.setStyleSheet(self.button_style("#3498db", "#2980b9"))
        self.browse_btn.clicked.connect(self.browse_file)
        button_row.addWidget(self.browse_btn)

        self.select_btn = QPushButton("Select")
        self.select_btn.setFixedSize(160, 45)
        self.select_btn.clicked.connect(self.select_file)
        button_row.addWidget(self.select_btn)

        file_section.addLayout(button_row)
        outer_layout.addLayout(file_section)

        # --- Application Settings section ---
        settings_group = QGroupBox("⚙️ Application Settings")
        settings_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        form_layout = QFormLayout()

        # API Key fields (stretchable, hidden by default)
        self.abuseipdb_input = self.create_api_input("abuseipdb_key", "AbuseIPDB API Key", form_layout)
        self.vt_input = self.create_api_input("virustotal_key", "VirusTotal API Key", form_layout)
        self.gemini_input = self.create_api_input("gemini_key", "Gemini API Key", form_layout)

        # AI Toggle
        self.ai_toggle = QCheckBox("Enable AI Overview")
        self.ai_toggle.setChecked(self.settings.get("ai_enabled", True))
        form_layout.addRow(self.ai_toggle)

        # Save button at bottom right + saved indicator
        save_layout = QHBoxLayout()
        save_layout.addStretch()

        self.saved_label = QLabel("✔ Settings saved")
        self.saved_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.saved_label.setVisible(False)
        save_layout.addWidget(self.saved_label)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setFixedSize(180, 45)
        self.save_btn.setStyleSheet(self.button_style("#27ae60", "#1e8449"))
        self.save_btn.clicked.connect(self.save_settings)
        save_layout.addWidget(self.save_btn)


        # # Inside __init__ after self.save_btn
        # self.apply_btn = QPushButton("Apply Settings")
        # self.apply_btn.setFixedSize(180, 45)
        # self.apply_btn.setStyleSheet(self.button_style("#f39c12", "#d35400"))
        # self.apply_btn.clicked.connect(self.apply_settings)
        # save_layout.addWidget(self.apply_btn)



        form_layout.addRow(save_layout)

        settings_group.setLayout(form_layout)
        outer_layout.addWidget(settings_group)

        # Spacer
        outer_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.setLayout(outer_layout)

        # Initialize select button state
        self.update_select_button()

    # === Helpers ===
    def create_api_input(self, key_name, label_text, layout):
        """Creates a masked API input with a toggle show/hide button and stretchable"""
        hbox = QHBoxLayout()
        line_edit = QLineEdit(self.settings.get(key_name, ""))
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        line_edit.setReadOnly(True)  # cannot edit when hidden
        line_edit.setMinimumWidth(400)
        line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hbox.addWidget(line_edit)

        show_btn = QPushButton("Show")
        show_btn.setFixedSize(60, 28)
        show_btn.setStyleSheet(self.button_style("#95a5a6", "#7f8c8d"))
        show_btn.setCheckable(True)

        def toggle_visibility(checked):
            if checked:
                line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
                line_edit.setReadOnly(False)
                show_btn.setText("Hide")
            else:
                line_edit.setEchoMode(QLineEdit.EchoMode.Password)
                line_edit.setReadOnly(True)
                show_btn.setText("Show")

        show_btn.toggled.connect(toggle_visibility)
        hbox.addWidget(show_btn)

        layout.addRow(label_text + ":", hbox)
        return line_edit

    def button_style(self, color, hover_color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """

    # def reload_app(self):
    #     """
    #     Fully restart the application.
    #     """
    #     python = sys.executable
    #     script = sys.argv[0]
    #     print("Reloading app...")
    #     # Launch a new process running this same script
    #     subprocess.Popen([python, script] + sys.argv[1:])
    #     # Exit current process
    #     sys.exit(0)

    # === File Handlers ===
    def browse_file(self):
        file_dialog, _ = QFileDialog.getOpenFileName(
            self, "Open Log File", "", "Log Files (*.log *.txt);;All Files (*)"
        )
        if file_dialog:
            self.file_input.setText(file_dialog)

    def update_select_button(self):
        file_path = self.file_input.text().strip()
        if file_path and Path(file_path).is_file():
            self.select_btn.setEnabled(True)
            self.select_btn.setStyleSheet(
                self.button_style("#2ecc71", "#27ae60")
            )
        else:
            self.select_btn.setEnabled(False)
            self.select_btn.setStyleSheet(
                self.button_style("#566573", "#566573")
            )

    def select_file(self):
        log_file = self.file_input.text().strip()
        if log_file and Path(log_file).is_file():
            # Save last_file in settings
            self.settings["last_file"] = log_file
            save_settings(self.settings)
            self.settings = load_settings()  # reload to apply

            # Update parent selected_file
            if self.parent:
                self.parent.selected_file = log_file

                # Automatically go to the next page (e.g., stats page)
                if hasattr(self.parent, "sidebar"):
                    self.parent.sidebar.setCurrentRow(1)  # index of next page

            # Call the callback
            if self.on_file_selected:
                self.on_file_selected(log_file)

    # === Settings Handlers ===
    def save_settings(self):
        self.settings["abuseipdb_key"] = self.abuseipdb_input.text().strip()
        self.settings["virustotal_key"] = self.vt_input.text().strip()
        self.settings["gemini_key"] = self.gemini_input.text().strip()
        self.settings["ai_enabled"] = self.ai_toggle.isChecked()
        save_settings(self.settings)

        # Show saved indicator for 2 seconds
        self.saved_label.setVisible(True)
        QTimer.singleShot(2000, lambda: self.saved_label.setVisible(False))

    #
    # def apply_settings(self):
    #     """
    #     Reload settings, save changes, and re-run current log file to refresh stats & AI overview.
    #     """
    #     # First save current inputs
    #     self.save_settings()
    #
    #     # Reload settings from disk
    #     self.settings = load_settings()
    #
    #     # Re-run the last selected file if exists
    #     last_file = self.settings.get("last_file", "")
    #     if last_file and Path(last_file).is_file() and self.on_file_selected:
    #         print("Applying settings and reloading file:", last_file)
    #         # Pass the parent.ai_page if needed
    #         ai_page = getattr(self.parent, "ai_page", None)
    #         self.on_file_selected(last_file, ai_page=ai_page)