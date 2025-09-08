from gui.gui import run_gui
from mylibs.parser import parser
from mylibs.statistics import log_statistics
from api.gemini import generate_ai_overview
import threading
from mylibs.settings import load_settings
import os
# --- AI callback ---
def handle_ai_text(ai_text, log_stats, ip_stats, exports_page):
    from PyQt6.QtCore import QTimer

    # Thread-safe update to ExportsPage
    def update_export():
        exports_page.update_data(
            log_stats=log_stats,
            ip_stats=ip_stats,
            ai_text=ai_text
        )

    QTimer.singleShot(0, update_export)



# --- File selected callback ---
def on_file_selected(file_path, ai_page=None, ai_callback=None, exports_page=None):
    """
    Called when a log file is selected in the GUI.
    Parses logs, calculates stats, and optionally generates AI overview.
    """
    settings = load_settings()
    gemini_api_key = settings.get("gemini_key", "")

    parsed_data = parser(file_path)
    log_stats, ip_stats = log_statistics(parsed_data)
    ip_list = [entry["remote_addr"] for entry in parsed_data]

    # Send stats immediately to ExportsPage (AI may arrive later)
    if exports_page:
        exports_page.update_data(log_stats=log_stats, ip_stats=ip_stats)

    # Run AI in background if enabled
    if settings.get("ai_enabled", True) and ai_page:
        ai_page.show_loading()

        def run_ai():
            ai_text = generate_ai_overview(ip_stats, gemini_api_key)
            ai_page.update_text_signal.emit(ai_text)  # update GUI

            if ai_callback:
                ai_callback(ai_text, log_stats, ip_stats, exports_page=exports_page)

                # Write AI text to file
                with open(os.path.join("exports", "temp.txt"), "w", encoding="utf-8") as f:
                    f.write(ai_text)

        threading.Thread(target=run_ai, daemon=True).start()
    else:
        if ai_page:
            ai_page.show_unchecked()

    return {
        "file_path": file_path,
        "parsed_data": parsed_data,
        "log_stats": log_stats,
        "ip_stats": ip_stats,
        "ip_list": ip_list
    }



run_gui(
    on_file_selected=lambda fp, ai_page=None, exports_page=None:
        on_file_selected(
            fp,
            ai_page=ai_page,
            ai_callback=handle_ai_text,
            exports_page=exports_page
        )
)
