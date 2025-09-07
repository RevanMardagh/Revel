from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class AIPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Title
        self.title = QLabel("AI Overview")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(self.title)

        # Placeholder content
        self.info_label = QLabel(
            "AI insights and summaries will appear here.\n"
            "You can feed log statistics or other analysis here."
        )
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def set_ai_data(self, ai_data: str):
        """Set the AI overview text."""
        self.info_label.setText(ai_data)
