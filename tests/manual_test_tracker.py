"""Manueller Test des Trackers."""

import sys
from pathlib import Path

# Füge src zum Path hinzu
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from timetracker.tracker import AppTracker
from timetracker.config import CONFIG_PATH, DEFAULT_CONFIG
import json

# Erstelle Test-Config
test_config = DEFAULT_CONFIG.copy()
test_config["target_apps"] = ["notepad.exe"]

# Speichere Test-Config
with open(CONFIG_PATH, 'w') as f:
    json.dump(test_config, f, indent=2)

print("Test-Config erstellt.")
print("Starte Tracking für notepad.exe")
print("1. Öffne notepad.exe")
print("2. Schreibe etwas")
print("3. Schließe notepad")
print("4. Drücke CTRL+C")
print()

try:
    tracker = AppTracker(CONFIG_PATH)
    tracker.start_monitoring()
except Exception as e:
    print(f"Fehler: {e}")
