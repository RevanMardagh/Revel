from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Title
        self.title = QLabel("Statistics & General Info")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(self.title)

        # Labels for overall statistics
        self.info_label = QLabel("Load a log file to see statistics here.")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.info_label)

        # Table for per-IP statistics
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "IP Address",
                "Total Requests",
                "4xx Ratio",
                "Status Counts",
                "User Agents",
                "VirusTotal Flags",
                "AbuseIPDB Score",
                "Conclusion"
            ]
        )
        layout.addWidget(self.table)
        self.setLayout(layout)

        # Color mapping for Conclusion column
        self.colors = {
            "Safe": QColor("#82E0AA"),
            "Low Risk": QColor("#A9DFBF"),
            "Medium Risk": QColor("#F7DC6F"),
            "High Risk": QColor("#F1948A"),
            "Malicious": QColor("#5A1111"),
            "Unknown": QColor()  # default transparent
        }

        # --- Column resizing ---
        header = self.table.horizontalHeader()
        # Stretch URI and User Agents for readability
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Status Counts
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # User Agents
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Conclusion

        # Other columns resize to contents
        for col in [0, 1, 2, 5, 6]:
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

    def set_stats(self, log_stats: dict, ip_stats: dict = None):
        # --- Global stats ---
        text = (
            f"Total Requests: {log_stats.get('total_requests', 0)}\n"
            f"Unique IPs: {log_stats.get('unique_ips', 0)}\n"
            # f"Most Common IP: {log_stats.get('most_common_ip', 'N/A')}\n"
            f"4xx Error Ratio: {log_stats.get('error_rate', 'N/A')}\n"
        )
        self.info_label.setText(text)

        # --- Per-IP stats ---
        if ip_stats:
            self.table.setRowCount(len(ip_stats))

            for row, (ip, stats) in enumerate(ip_stats.items()):
                self.table.setItem(row, 0, QTableWidgetItem(ip))
                self.table.setItem(row, 1, QTableWidgetItem(str(stats["total_requests"])))
                self.table.setItem(row, 2, QTableWidgetItem(stats["4xx_ratio"]))

                # Status counts as HTML badges
                status_html = ""
                for status, count in stats["status_counts"].items():
                    if 100 <= status < 200:
                        color = "#85C1E9"
                    elif 200 <= status < 300:
                        color = "#82E0AA"
                    elif 300 <= status < 400:
                        color = "#F7DC6F"
                    elif 400 <= status < 500:
                        color = "#F1948A"
                    elif 500 <= status < 600:
                        color = "#E59866"
                    else:
                        color = "#D5D8DC"
                    status_html += f'<span style="background-color:{color}; padding:2px; margin:1px; border-radius:3px;">{status}:</span> {count}; '

                status_label = QLabel(status_html)
                status_label.setTextFormat(Qt.TextFormat.RichText)
                status_label.setWordWrap(True)
                self.table.setCellWidget(row, 3, status_label)

                # User agents as multi-line QLabel
                ua_text = "\n\r".join(f"{ua}: {count}" for ua, count in stats["user_agents"].items())
                ua_label = QLabel(ua_text)
                ua_label.setWordWrap(True)
                self.table.setCellWidget(row, 4, ua_label)

                # VirusTotal Report
                vt_score = stats.get("virustotal", "N/A")
                self.table.setItem(row, 5, QTableWidgetItem(str(vt_score)))

                # AbuseIPDB Score
                abuse_score = stats.get("abuseipdb", "N/A")
                self.table.setItem(row, 6, QTableWidgetItem(str(abuse_score)))

                # --- Conclusion column ---
                conclusion = stats.get("reputation", "Unknown")
                conclusion_item = QTableWidgetItem(conclusion)
                conclusion_item.setBackground(self.colors.get(conclusion, QColor()))
                self.table.setItem(row, 7, conclusion_item)
        else:
            self.table.setRowCount(0)
