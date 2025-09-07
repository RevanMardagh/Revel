from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal

class AIPage(QWidget):
    # Signal to update AI text safely from another thread
    update_text_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title at the top
        self.title = QLabel("🤖 AI Overview")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title)

        # Markdown-capable text area
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            font-size: 16px;
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #555555;
        """)
        layout.addWidget(self.info_text)

        self.setLayout(layout)

        # Connect the signal to update function
        self.update_text_signal.connect(self.set_ai_data)

    def set_ai_data(self, ai_data: str):
        """Set AI text with Markdown rendering."""
        self.info_text.setMarkdown(ai_data)

    def show_loading(self):
        """Show loading message."""
        self.info_text.setPlainText("Generating AI overview… Please wait…")

    def show_unchecked(self):
        """Show unchecked message."""
        self.info_text.setPlainText("You've disabled AI overview. Run the program again if you want AI to review the log file")
