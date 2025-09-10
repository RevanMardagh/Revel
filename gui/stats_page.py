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
                "Conclusion",
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
            "Unknown": QColor(),  # default transparent
        }

        # --- Column resizing ---
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # all columns resizable
        header.setStretchLastSection(False)

        # Special resize rules
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Conclusion fits content
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # User Agents stretches
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Status Counts stretches

    def set_stats(self, log_stats: dict, ip_stats: dict = None):

        # --- Global stats ---
        text = (
            f"Total Requests: {log_stats.get('total_requests', 0)}\n"
            f"Unique IPs: {log_stats.get('unique_ips', 0)}\n"
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

                # --- Status counts: centered, bold bubbles ---
                status_html = '<div style="text-align:center;">'
                for status, count in sorted(stats["status_counts"].items()):
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
                    status_html += (
                        f'<span style="background:{color}; '
                        f'padding:8px; margin:10px; '
                        f'border-radius:12px; font-weight:bold; '
                        f'display:inline-block;">'
                        f'{status}: {count}</span> '
                    )
                status_html += '</div>'

                status_label = QLabel(status_html)
                status_label.setTextFormat(Qt.TextFormat.RichText)
                status_label.setWordWrap(True)
                status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setCellWidget(row, 3, status_label)

                # --- User agents: shortest first ---
                sorted_uas = sorted(stats["user_agents"].items(), key=lambda x: len(x[0]))
                ua_text = "\n".join(f"{ua}: {count}" for ua, count in sorted_uas)
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

            # Auto-resize rows to fit content (important for status counts & UAs)
            self.table.resizeRowsToContents()

            # Make Status Counts column as narrow as possible
            self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        else:
            self.table.setRowCount(0)
