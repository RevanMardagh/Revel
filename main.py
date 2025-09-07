# main.py
from gui.gui import run_gui
from mylibs.parser import parser
from mylibs.statistics import log_statistics   # import your stats
from api.gemini import generate_ai_overview
import threading
from PyQt6.QtCore import QTimer

gemini_api_key = "AIzaSyBfIbqkLpHsxZdubj-_IVk-t2OOPKw47r4"


def on_file_selected(file_path, ai_page=None):
    """
    Called when a file is selected in the GUI.
    Parses the logs, computes stats, and starts AI overview in background.
    """
    print("File selected:", file_path)

    # Parse log file
    parsed_data = parser(file_path)

    # Compute statistics
    log_stats, ip_stats = log_statistics(parsed_data)

    # IP list
    ip_list = [entry["remote_addr"] for entry in parsed_data]

    # Show loading immediately
    if ai_page:
        ai_page.show_loading()

    def run_ai():
        ai_text = generate_ai_overview(ip_stats, gemini_api_key)
        print("AI overview:\n", ai_text)
        if ai_page:
            ai_page.update_text_signal.emit(ai_text)  # Safe update from thread

    threading.Thread(target=run_ai, daemon=True).start()

    # Return everything for GUI pages (without ai_text, it will be set later)
    return {
        "file_path": file_path,
        "parsed_data": parsed_data,
        "log_stats": log_stats,
        "ip_stats": ip_stats,
        "ip_list": ip_list
    }


# Run GUI and pass callback
run_gui(on_file_selected=on_file_selected)
