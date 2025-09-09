from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QStackedWidget, QHBoxLayout, QWidget
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtCore import Qt
from gui.file_page import FilePage
from gui.list_page import NextPage
from gui.stats_page import StatsPage
from gui.ai_page import AIPage
from gui.exports_page import ExportsPage
from mylibs.settings import load_settings
import os

class LogAnalyzerApp(QMainWindow):
    def __init__(self, on_file_selected=None):
        super().__init__()
        self.setWindowTitle("Revel Log Analyzer")

        # --- Set the window icon ---
        icon_path = os.path.join("assets", "icon.png")  # path to your icon file
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"⚠️ Icon file not found: {icon_path}")

        # Set default size
        self.resize(1600, 1200)

        # Center the window on the screen
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        # Load settings
        self.settings = load_settings()
        self.selected_file = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItem("📂 File")
        self.sidebar.addItem("📄 Overview")
        self.sidebar.addItem("📊 Statistics")
        self.sidebar.addItem("🤖 AI Overview")
        self.sidebar.addItem("💾 Export")


        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 0px;
                font-size: 18px;
            }
            QListWidget::item {
                height: 50px;
                padding-left: 10px;
            }
            QListWidget::item:hover {
                background-color: #34495e;
            }
            QListWidget::item:selected {
                background-color: #1abc9c;
                color: black;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(self.sidebar)

        # Pages
        self.stack = QStackedWidget()
        self.next_page = NextPage()
        self.stats_page = StatsPage()
        self.ai_page = AIPage()
        self.exports_page = ExportsPage() # start with empty data

        def wrapped_file_selected(file_path):

            # self.sidebar.setCurrentRow(1)

            if on_file_selected:
                results = on_file_selected(
                    file_path,
                    ai_page=self.ai_page,
                    exports_page=self.exports_page  # pass the exports page
                )
                self.next_page.set_data(results["parsed_data"], results["ip_stats"])
                self.stats_page.set_stats(results["log_stats"], results["ip_stats"])


        self.file_page = FilePage(parent=self, on_file_selected=wrapped_file_selected)

        self.stack.addWidget(self.file_page)   # index 0
        self.stack.addWidget(self.next_page)   # index 1
        self.stack.addWidget(self.stats_page)  # index 2
        self.stack.addWidget(self.ai_page)     # index 3
        self.stack.addWidget(self.exports_page)  # index 4
        main_layout.addWidget(self.stack)


        # Sidebar navigation
        self.sidebar.currentRowChanged.connect(self.display_page)
        self.sidebar.setCurrentRow(0)


    def display_page(self, index):
        self.stack.setCurrentIndex(index)



def run_gui(on_file_selected=None):
    app = QApplication([])
    window = LogAnalyzerApp(on_file_selected=on_file_selected)
    window.show()
    app.exec()
