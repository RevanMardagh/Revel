from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTableView, QProgressBar, QApplication
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QThread, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor

from api.query_apis import check_ip_reputation_levels  # your fixed API code

class ReputationThread(QThread):
    update_ip = pyqtSignal(str, str)  # IP and its reputation level

    def __init__(self, ips):
        super().__init__()
        self.ips = ips

    def run(self):
        results = check_ip_reputation_levels(self.ips)
        for ip, level in results.items():
            self.update_ip.emit(ip, level)

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

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Table view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "Timestamp", "IP Address", "Method", "URI", "Status", "User Agent", "Reputation"
        ])

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setDefaultSectionSize(25)
        self.table.setColumnWidth(3, 200)
        layout.addWidget(self.table)

        # Filter proxy
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(-1)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.table.setModel(self.proxy_model)
        self.filter_input.textChanged.connect(self.proxy_model.setFilterFixedString)

        self.setLayout(layout)

        # Color mapping
        self.colors = {
            "Safe": QColor("green"),
            "Low Risk": QColor("lightgreen"),
            "Medium Risk": QColor("yellow"),
            "High Risk": QColor("orange"),
            "Malicious": QColor(119, 17, 17)
        }

        self.reputation_thread = None

    def set_data(self, raw_data):
        """
        raw_data: list of dicts with keys:
        timestamp, remote_addr, method, uri, status, user_agent
        """
        self.raw_data = raw_data
        self.model.setRowCount(0)

        # Add placeholder rows
        for entry in raw_data:
            row_items = [
                QStandardItem(str(entry.get("timestamp", ""))),
                QStandardItem(str(entry.get("remote_addr", ""))),
                QStandardItem(str(entry.get("method", ""))),
                QStandardItem(str(entry.get("uri", ""))),
                QStandardItem(str(entry.get("status", ""))),
                QStandardItem(str(entry.get("user_agent", ""))),
                QStandardItem("Checking...")  # placeholder
            ]
            for item in row_items:
                item.setEditable(False)
            self.model.appendRow(row_items)

        for col in [0, 1, 2, 4, 5, 6]:
            self.table.resizeColumnToContents(col)

        # Start reputation thread
        ips = [entry["remote_addr"] for entry in raw_data]
        self.progress_bar.setMaximum(len(ips))
        self.progress_bar.setValue(0)

        self.reputation_thread = ReputationThread(ips)
        self.reputation_thread.update_ip.connect(self.update_ip_row)
        self.reputation_thread.start()

    def update_ip_row(self, ip, level):
        """
        Update all rows for a single IP and apply color
        """
        rows_updated = 0
        for row in range(self.model.rowCount()):
            if self.model.item(row, 1).text() == ip:
                # Update reputation text
                self.model.item(row, 6).setText(level)
                # Update row color
                for col in range(self.model.columnCount()):
                    self.model.item(row, col).setBackground(self.colors.get(level, QColor("white")))
                rows_updated += 1

        # Update progress bar by the number of rows updated
        self.progress_bar.setValue(self.progress_bar.value() + rows_updated)
        QApplication.processEvents()  # refresh GUI


