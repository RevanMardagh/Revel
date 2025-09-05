import os

folder = r"C:\Users\Ravan\Music\OnTheSpot\Tracks"

for filename in os.listdir(folder):
    if " - " in filename:
        name, ext = os.path.splitext(filename)
        parts = name.split(" - ")
        if len(parts) == 2:
            new_name = f"{parts[1]} - {parts[0]}{ext}"
            os.rename(os.path.join(folder, filename), os.path.join(folder, new_name))
