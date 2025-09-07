from gui.gui import run_gui
from mylibs.parser import parser
from mylibs.statistics import log_statistics
from api.gemini import generate_ai_overview
import threading
from mylibs.settings import load_settings



def on_file_selected(file_path, ai_page=None):
    """
    Called when a file is selected in the GUI.
    Parses the logs, computes stats, and starts AI overview in background if enabled.
    """
    print("File selected:", file_path)

    # Load settings
    settings = load_settings()
    gemini_api_key = settings.get("gemini_key", "")

    # Parse log file
    parsed_data = parser(file_path)

    # Compute statistics
    log_stats, ip_stats = log_statistics(parsed_data)

    # IP list
    ip_list = [entry["remote_addr"] for entry in parsed_data]


    # Only run AI if the setting is enabled
    if settings.get("ai_enabled", True) and ai_page:
        print("Starting AI overview...")
        # Show loading immediately
        ai_page.show_loading()

        def run_ai():
            ai_text = generate_ai_overview(ip_stats, gemini_api_key)
            print("AI overview:\n", ai_text)
            ai_page.update_text_signal.emit(ai_text)  # Safe update from thread

        threading.Thread(target=run_ai, daemon=True).start()
    else:
        ai_page.show_unchecked()
        print("Won't show AI overview...")

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
