from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableView,
    QProgressBar, QApplication, QHBoxLayout, QComboBox, QHeaderView
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QThread, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor

from api.query_apis import check_ip_reputation_levels


class ReputationThread(QThread):
    update_ip = pyqtSignal(str, str)  # IP and its reputation level

    def __init__(self, ips):
        super().__init__()
        self.ips = ips

    def run(self):
        results = check_ip_reputation_levels(self.ips)
        for ip, level in results.items():
            self.update_ip.emit(ip, level)


class MultiFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text = ""
        self.status_filter = "All Statuses"
        self.reputation_filter = "All Reputations"

    def set_search_text(self, text: str):
        self.search_text = text or ""
        self.invalidateFilter()

    def set_status_filter(self, text: str):
        self.status_filter = text or "All Statuses"
        self.invalidateFilter()

    def set_reputation_filter(self, text: str):
        self.reputation_filter = text or "All Reputations"
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        model = self.sourceModel()
        if model is None:
            return True

        # 1) Search text applied across all columns
        if self.search_text:
            found = False
            for col in range(model.columnCount()):
                item = model.item(source_row, col)
                if item and self.search_text.lower() in item.text().lower():
                    found = True
                    break
            if not found:
                return False

        # 2) Status filter (e.g. "2xx", "4xx")
        if self.status_filter and self.status_filter != "All Status":
            status_item = model.item(source_row, 4)  # Status column index
            if status_item is None:
                return False
            status_text = status_item.text().strip()
            # If status filter like "2xx", check first digit
            if self.status_filter.endswith("xx") and len(status_text) > 0:
                if not status_text.startswith(self.status_filter[0]):
                    return False
            else:
                if status_text != self.status_filter:
                    return False

        # 3) Reputation filter (exact match)
        if self.reputation_filter and self.reputation_filter != "All Reputation":
            rep_item = model.item(source_row, 6)  # Reputation column index
            if rep_item is None:
                return False
            if rep_item.text() != self.reputation_filter:
                return False

        return True


class NextPage(QWidget):
    def __init__(self):
        super().__init__()
        self.raw_data = []

        main_layout = QVBoxLayout()

        # Top bar: title left, options right
        top_bar = QHBoxLayout()
        self.title_label = QLabel("All Parsed Logs")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()

        # Dropdowns (filter options)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "2xx", "3xx", "4xx", "5xx"])
        top_bar.addWidget(self.status_filter)

        self.reputation_filter = QComboBox()
        self.reputation_filter.addItems(["All Reputation", "Safe", "Low Risk", "Medium Risk", "High Risk", "Malicious"])
        top_bar.addWidget(self.reputation_filter)

        main_layout.addLayout(top_bar)

        # Search bar below the top bar
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search logs...")
        self.filter_input.setStyleSheet("font-size: 16px; padding: 5px;")
        main_layout.addWidget(self.filter_input)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        # Table model + view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "Timestamp", "IP Address", "Method", "URI", "Status", "User Agent", "Reputation"
        ])

        self.table = QTableView()
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setDefaultSectionSize(25)
        self.table.setColumnWidth(3, 200)

        # Proxy model (multi-filter)
        self.proxy_model = MultiFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.table.setModel(self.proxy_model)

        main_layout.addWidget(self.table)

        # Row count label
        self.row_count_label = QLabel("Rows: 0")
        self.row_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.row_count_label.setStyleSheet("font-size: 14px; color: gray;")
        main_layout.addWidget(self.row_count_label)

        # Wire signals
        self.filter_input.textChanged.connect(self.on_filter_changed)
        self.status_filter.currentTextChanged.connect(self.on_filter_changed)
        self.reputation_filter.currentTextChanged.connect(self.on_filter_changed)

        self.setLayout(main_layout)

        # Color mapping
        self.colors = {
            "Safe": QColor("green"),
            "Low Risk": QColor("lightgreen"),
            "Medium Risk": QColor("yellow"),
            "High Risk": QColor("orange"),
            "Malicious": QColor(90, 17, 17),
            # "Unknown": QColor("gray")
        }

        self.reputation_thread = None

    def on_filter_changed(self, _=None):
        # Send current UI values into the proxy model
        self.proxy_model.set_search_text(self.filter_input.text())
        self.proxy_model.set_status_filter(self.status_filter.currentText())
        self.proxy_model.set_reputation_filter(self.reputation_filter.currentText())
        self.update_row_count()

    def update_row_count(self):
        # Show rows after filtering (proxy row count)
        self.row_count_label.setText(f"Rows: {self.proxy_model.rowCount()}")

    def set_data(self, raw_data):
        """
        raw_data: list of dicts with keys:
        timestamp, remote_addr, method, uri, status, user_agent
        """
        self.raw_data = raw_data
        self.model.setRowCount(0)

        for entry in raw_data:
            row_items = [
                QStandardItem(str(entry.get("timestamp", ""))),
                QStandardItem(str(entry.get("remote_addr", ""))),
                QStandardItem(str(entry.get("method", ""))),
                QStandardItem(str(entry.get("uri", ""))),
                QStandardItem(str(entry.get("status", ""))),
                QStandardItem(str(entry.get("user_agent", ""))),
                QStandardItem("Checking...")  # placeholder reputation
            ]
            for item in row_items:
                item.setEditable(False)
            self.model.appendRow(row_items)

        # Resize columns for readability
        for col in [0, 1, 2, 4, 5, 6]:
            self.table.resizeColumnToContents(col)

        # After creating the table and setting the model
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # URI
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # User Agent

        # Optional: keep other columns resize-to-contents
        for col in [0, 1, 2, 4, 6]:
            self.table.resizeColumnToContents(col)

        # Update progress bar and start reputation thread
        ips = [entry["remote_addr"] for entry in raw_data]
        self.progress_bar.setMaximum(len(ips))
        self.progress_bar.setValue(0)

        # Ensure filters applied to new data
        self.on_filter_changed()

        self.reputation_thread = ReputationThread(ips)
        self.reputation_thread.update_ip.connect(self.update_ip_row)
        self.reputation_thread.start()

    def update_ip_row(self, ip, level):
        """
        Update all rows matching an IP with the reputation level and color.
        Invalidate proxy so filtering updates, and refresh the row count.
        """
        rows_updated = 0
        for row in range(self.model.rowCount()):
            item_ip = self.model.item(row, 1)
            if item_ip and item_ip.text() == ip:
                self.model.item(row, 6).setText(level)  # reputation
                # color the row (source model)
                for col in range(self.model.columnCount()):
                    self.model.item(row, col).setBackground(self.colors.get(level, QColor()))
                rows_updated += 1

        # Invalidate proxy since source data changed and filters may depend on it
        self.proxy_model.invalidateFilter()
        # Update progress by number of rows updated
        self.progress_bar.setValue(min(self.progress_bar.maximum(), self.progress_bar.value() + rows_updated))

        # Refresh visible row count
        self.update_row_count()
        QApplication.processEvents()
