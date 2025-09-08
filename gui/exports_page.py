import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QCheckBox, QGroupBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from mylibs.export import export_logs_and_ai  # your exporter

class ExportsPage(QWidget):
    def __init__(self, log_stats=None, ip_stats=None, ai_text=None):
        super().__init__()
        self.log_stats = log_stats
        self.ip_stats = ip_stats
        self.ai_text = ai_text

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Export folder selection ---
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Export Folder:"))
        self.folder_input = QLineEdit(os.path.join(os.getcwd(), "exports", "logs"))
        folder_layout.addWidget(self.folder_input)
        folder_btn = QPushButton("Browse")
        folder_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(folder_btn)
        layout.addLayout(folder_layout)

        # --- Filename input ---
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("File Base Name:"))
        self.name_input = QLineEdit("log_report")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # --- File type checkboxes ---
        self.md_cb = QCheckBox("Markdown (.md)")
        self.txt_cb = QCheckBox("Text (.txt)")
        self.html_cb = QCheckBox("HTML (.html)")
        self.docx_cb = QCheckBox("DOCX (.docx)")
        self.pdf_cb = QCheckBox("PDF (.pdf)")

        font = QFont()
        font.setPointSize(11)
        for cb in [self.md_cb, self.txt_cb, self.html_cb, self.docx_cb, self.pdf_cb]:
            cb.setFont(font)
            cb.setStyleSheet("margin: 2px;")
            cb.setChecked(True)

        types_group = QGroupBox("File Types to Export")
        types_layout = QVBoxLayout()
        for cb in [self.md_cb, self.txt_cb, self.html_cb, self.docx_cb, self.pdf_cb]:
            types_layout.addWidget(cb)
        types_layout.addStretch()
        types_group.setLayout(types_layout)
        layout.addWidget(types_group)

        # --- Export & Refresh buttons ---
        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export")
        self.export_btn.setFixedHeight(35)
        self.export_btn.clicked.connect(self.export_files)
        btn_layout.addWidget(self.export_btn)

        self.refresh_btn = QPushButton("Refresh Data from AI")
        self.refresh_btn.setFixedHeight(35)
        self.refresh_btn.clicked.connect(self.refresh_data)
        btn_layout.addWidget(self.refresh_btn)

        layout.addLayout(btn_layout)

        # --- Status label ---
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    # ---------------- Helper Methods ----------------
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Export Folder", os.path.join(os.getcwd(), "exports", "logs")
        )
        if folder:
            self.folder_input.setText(folder)

    def refresh_data(self):
        """
        Pull the latest AI text from disk and update internal state.
        """
        ai_file = os.path.join(os.getcwd(), "exports", "temp.txt")
        if os.path.exists(ai_file):
            with open(ai_file, "r", encoding="utf-8") as f:
                self.ai_text = f.read()
            self.status_label.setText("✅ Data refreshed from AI overview file")
        else:
            self.status_label.setText("⚠️ AI overview file not found")

    def update_data(self, log_stats=None, ip_stats=None, ai_text=None):
        """
        Called from main.py / AI callback to update internal data.
        """
        if log_stats:
            self.log_stats = log_stats
        if ip_stats:
            self.ip_stats = ip_stats
        if ai_text:
            self.ai_text = ai_text

    def export_files(self):
        folder = self.folder_input.text()
        base_name = self.name_input.text()
        selected_types = []
        if self.md_cb.isChecked(): selected_types.append("md")
        if self.txt_cb.isChecked(): selected_types.append("txt")
        if self.html_cb.isChecked(): selected_types.append("html")
        if self.docx_cb.isChecked(): selected_types.append("docx")
        if self.pdf_cb.isChecked(): selected_types.append("pdf")

        if not selected_types:
            self.status_label.setText("⚠️ Please select at least one file type")
            return

        try:
            export_logs_and_ai(
                log_stats=self.log_stats,
                ip_stats=self.ip_stats,
                ai_text=self.ai_text,
                output_dir=folder,
                base_name=base_name,
                formats=selected_types
            )
            self.status_label.setText(f"✅ Exported successfully to {folder}")
        except Exception as e:
            self.status_label.setText(f"❌ Export failed: {str(e)}")
