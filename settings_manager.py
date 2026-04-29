import json
import os
from pathlib import Path

SETTINGS_FILE = "app_settings.json"

# Base dir for resources
_BASE_DIR = os.path.dirname(__file__)

def save_settings(dark_mode, sound_paths):
    """Save settings to file"""
    settings = {
        "dark_mode": dark_mode,
        "sound_paths": sound_paths
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def load_settings():
    """Load settings from file"""
    if not os.path.exists(SETTINGS_FILE):
        return {
            "dark_mode": True,
            "sound_paths": {
                36: os.path.join(_BASE_DIR, "sounds", "kick.wav"),   # NOTE_KICK
                38: os.path.join(_BASE_DIR, "sounds", "snare.wav"),  # NOTE_SNARE
                42: os.path.join(_BASE_DIR, "sounds", "hihat.wav")   # NOTE_HH
            }
        }
    
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        return settings
    except:
        return {
            "dark_mode": True,
            "sound_paths": {
                36: os.path.join(_BASE_DIR, "sounds", "kick.wav"),
                38: os.path.join(_BASE_DIR, "sounds", "snare.wav"),
                42: os.path.join(_BASE_DIR, "sounds", "hihat.wav")
            }
        }
