# main.py
from gui.gui import run_gui
from mylibs.parser import parser  # your parse function


def on_file_selected(file_path):
    print("File selected:", file_path)
    # Call your parser function
    data = parser(file_path)
    # For now, just print data; later you can send it to the next page
    # print("Parsed data:", data[0].items())
    return data


# Run the GUI and pass the callback
run_gui(on_file_selected=on_file_selected)
