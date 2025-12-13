"""Konfiguration und Konstanten für TimeTracker."""

from pathlib import Path

# ========== PFADE ==========
BASE_DIR = Path(__file__).parent.parent.parent  # → TimeTracker/
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"

# Stelle sicher, dass data/ existiert
DATA_DIR.mkdir(exist_ok=True)

CONFIG_PATH = DATA_DIR / "config.json"
DB_PATH = DATA_DIR / "tracker.db"
LOG_PATH = DATA_DIR / "tracker.log"

# ========== STANDARD-KONFIGURATION ==========
DEFAULT_CONFIG = {
    "target_apps": ["notepad.exe"],
    "db_path": str(DB_PATH),
    "check_interval": 0.5,
}

# ========== AUTOSTART ==========
AUTOSTART_PARAM = "--autostart"

# ========== LOGGING ==========
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# ========== VALIDIERUNG ==========
MIN_CHECK_INTERVAL = 0.1
MAX_CHECK_INTERVAL = 5.0
