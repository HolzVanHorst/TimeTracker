"""Test ob alle Module importierbar sind."""

import sys
from pathlib import Path

# Füge src zum Path hinzu
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Teste ob alle Module ohne Fehler importierbar sind."""
    try:
        from timetracker.exceptions import TimeTrackerError, ConfigError
        from timetracker.config import CONFIG_PATH, DEFAULT_CONFIG
        from timetracker.logger_config import setup_logger
        from timetracker.strings import Messages
        from timetracker.database import Database
        from timetracker.tracker import AppTracker
        from timetracker.app import TimeTrackerApp
        
        print("✅ Alle Imports erfolgreich!")
        return True
    except Exception as e:
        print(f"❌ Import fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
