from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTableView
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class NextPage(QWidget):
    def __init__(self):
        super().__init__()
        self.raw_data = []
        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("All Parsed Logs")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Filter input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Type to filter logs...")
        self.filter_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.filter_input)

        # Table view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "Timestamp", "IP Address", "Method", "URI", "Status", "User Agent"
        ])

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(-1)  # filter all columns
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.table = QTableView()
        self.table.setModel(self.proxy_model)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setDefaultSectionSize(25)
        self.table.setColumnWidth(3, 200)  # fixed URI width
        layout.addWidget(self.table)

        # Connect filter input
        self.filter_input.textChanged.connect(self.proxy_model.setFilterFixedString)

        self.setLayout(layout)

    def set_data(self, raw_data):
        """
        raw_data: list of dicts with keys:
        timestamp, remote_addr, method, uri, status, user_agent
        """
        self.raw_data = raw_data
        self.model.setRowCount(0)  # clear old data

        for entry in raw_data:
            row_items = [
                QStandardItem(str(entry.get("timestamp", ""))),
                QStandardItem(str(entry.get("remote_addr", ""))),
                QStandardItem(str(entry.get("method", ""))),
                QStandardItem(str(entry.get("uri", ""))),
                QStandardItem(str(entry.get("status", ""))),
                QStandardItem(str(entry.get("user_agent", ""))),
            ]
            for item in row_items:
                item.setEditable(False)
            self.model.appendRow(row_items)

        # Optional: resize columns except URI to contents
        for col in [0, 1, 2, 4, 5]:
            self.table.resizeColumnToContents(col)
