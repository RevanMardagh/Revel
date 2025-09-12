# gui/loading_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

class LoadingDialog(QDialog):
    def __init__(self, message="Loading, please wait...", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        progress = QProgressBar()
        progress.setRange(0, 0)  # infinite spinner
        layout.addWidget(progress)

        self.setFixedSize(300, 120)
