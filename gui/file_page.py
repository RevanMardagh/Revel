from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
from pathlib import Path

class FilePage(QWidget):
    def __init__(self, parent=None, on_file_selected=None):
        super().__init__(parent)
        self.parent = parent
        self.on_file_selected = on_file_selected

        # Layouts
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner_layout = QVBoxLayout()
        inner_layout.setSpacing(20)
        inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        self.title_label = QLabel("Select a log file to analyze")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        inner_layout.addWidget(self.title_label)

        # File input
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Path to log file...")
        self.file_input.setFixedWidth(400)
        self.file_input.setStyleSheet("font-size: 16px;")
        self.file_input.textChanged.connect(self.update_select_button)
        inner_layout.addWidget(self.file_input, alignment=Qt.AlignmentFlag.AlignCenter)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setFixedSize(140, 50)
        self.browse_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; font-weight: bold; font-size: 16px; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        self.browse_btn.clicked.connect(self.browse_file)
        button_layout.addWidget(self.browse_btn)

        self.select_btn = QPushButton("Select")
        self.select_btn.setFixedSize(140, 50)
        self.select_btn.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_btn)

        inner_layout.addLayout(button_layout)
        outer_layout.addLayout(inner_layout)
        outer_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(outer_layout)
        self.update_select_button()

    def browse_file(self):
        file_dialog, _ = QFileDialog.getOpenFileName(
            self, "Open Log File", "", "Log Files (*.log *.txt);;All Files (*)"
        )
        if file_dialog:
            self.file_input.setText(file_dialog)

    def update_select_button(self):
        file_path = self.file_input.text().strip()
        if file_path and Path(file_path).is_file():
            self.select_btn.setStyleSheet(
                "QPushButton { background-color: #2ecc71; color: white; font-weight: bold; font-size: 16px; }"
                "QPushButton:hover { background-color: #27ae60; }"
            )
            self.select_btn.setEnabled(True)
        else:
            self.select_btn.setStyleSheet(
                "QPushButton { background-color: #1e8449; color: white; font-weight: bold; font-size: 16px; }"
            )
            self.select_btn.setEnabled(False)

    def select_file(self):
        log_file = self.file_input.text().strip()
        if log_file and Path(log_file).is_file():
            if self.on_file_selected:
                self.on_file_selected(log_file)
            if self.parent:
                self.parent.selected_file = log_file
                self.parent.sidebar.setCurrentRow(1)
