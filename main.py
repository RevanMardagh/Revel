# main.py
from gui.gui import run_gui
from mylibs.parser import parser
from mylibs.statistics import log_statistics   # import your stats
import api.query_apis as api
from api.gemini import generate_ai_overview
import asyncio


vt_api_key = "6959c5e658d3ec7fea72475347b4b8025c4a8de00767317f2e0e8c1978f0bab4"
abuse_api_key = "ffc53215145b0aaddec3be4138ec4468e4fd57c20ee6f66d583bb00f45030ea81aef5d1b34c95530"
gemini_api_key = "AIzaSyBfIbqkLpHsxZdubj-_IVk-t2OOPKw47r4"


async def async_generate_ai_overview(ip_stats, api_key):
    """
    Run the AI overview in a non-blocking way.
    Uses asyncio.to_thread to run the blocking AI call in a thread.
    """
    result = await asyncio.to_thread(generate_ai_overview, ip_stats, api_key)
    return result




def on_file_selected(file_path):
    print("File selected:", file_path)
    # Parse log file
    parsed_data = parser(file_path)
    # Get stats
    log_stats, ip_stats = log_statistics(parsed_data)
    # IP list
    ip_list = [entry["remote_addr"] for entry in parsed_data]

    # AI BLET
    # Fire-and-forget AI call
    def run_ai_thread():
        ai_text = generate_ai_overview(ip_stats, gemini_api_key)
        print("AI Overview:\n", ai_text)
        # If you want, update your AIPage:
        # window.ai_page.set_text(ai_text)
        return ai_text

    ai_text = asyncio.get_event_loop().run_in_executor(None, run_ai_thread)






    # Return everything in a dict for GUI pages
    return {
        "file_path": file_path,
        "parsed_data": parsed_data,
        "log_stats": log_stats,
        "ip_stats": ip_stats,
        "ip_list": ip_list,
        "ai_text": ai_text
    }


# Run GUI and pass callback
run_gui(on_file_selected=on_file_selected)

