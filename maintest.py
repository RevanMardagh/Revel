# main.py
from gui.gui import run_gui
from mylibs.parser import parser
from mylibs.statistics import log_statistics   # import your stats
import api.query_apis as api


vt_api_key = "6959c5e658d3ec7fea72475347b4b8025c4a8de00767317f2e0e8c1978f0bab4"
abuse_api_key = "ffc53215145b0aaddec3be4138ec4468e4fd57c20ee6f66d583bb00f45030ea81aef5d1b34c95530"

def on_file_selected(file_path):
    print("File selected:", file_path)

    # Parse log file
    parsed_data = parser(file_path)

    # Get stats
    log_stats, ip_stats = log_statistics(parsed_data)

    # IP list
    ip_list = [entry["remote_addr"] for entry in parsed_data]

    # Return everything in a dict for GUI pages
    return {
        "file_path": file_path,
        "parsed_data": parsed_data,
        "log_stats": log_stats,
        "ip_stats": ip_stats,
        "ip_list": ip_list
    }


# Run GUI and pass callback
run_gui(on_file_selected=on_file_selected)

