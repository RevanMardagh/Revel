import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class FileBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Browser")
        self.resize(500, 180)
        self.selected_file = None  # store result

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Heading
        label = QLabel("Select the log file you want to analyze", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(label)

        # File input row
        file_layout = QHBoxLayout()
        file_layout.setSpacing(5)
        self.file_path = QLineEdit(self)
        self.file_path.setPlaceholderText("No file selected")
        file_layout.addWidget(self.file_path)

        browse_button = QPushButton("Browse", self)
        browse_button.setFixedHeight(35)
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_button)
        main_layout.addLayout(file_layout)

        # Connect Enter key to submit
        self.file_path.returnPressed.connect(self.submit_file)

        # Centered Submit button
        submit_layout = QHBoxLayout()
        submit_layout.addStretch(1)
        submit_button = QPushButton("Submit", self)
        submit_button.setFixedHeight(35)
        submit_button.setFixedWidth(120)
        submit_button.clicked.connect(self.submit_file)
        submit_layout.addWidget(submit_button)
        submit_layout.addStretch(1)
        main_layout.addLayout(submit_layout)

        self.setLayout(main_layout)

    def browse_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.file_path.setText(selected_files[0])

    def submit_file(self):
        filename = self.file_path.text().strip()
        if not filename:
            QMessageBox.warning(self, "No file selected", "Please select a file before submitting.")
            return
        if not os.path.isfile(filename):
            QMessageBox.critical(self, "Invalid file", "The selected file does not exist.")
            return
        self.selected_file = filename
        self.close()  # close the window


def get_file():
    """Show the GUI and return the selected file"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = FileBrowser()
    window.show()
    app.exec()
    return window.selected_file
