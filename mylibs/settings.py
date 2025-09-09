# mylibs/settings.py
import json
from pathlib import Path

SETTINGS_FILE = Path("settings.json")
# print(SETTINGS_FILE)

DEFAULT_SETTINGS = {
    "abuseipdb_key": "",
    "virustotal_key": "",
    "gemini_key": "",
    "ai_enabled": True,
    "last_file": "",
    "theme": "dark"
}

def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r") as f:
            return {**DEFAULT_SETTINGS, **json.load(f)}
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
