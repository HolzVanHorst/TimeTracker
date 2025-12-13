"""TimeTracker - Einstiegspunkt beim Ausführen als Modul.

Erlaubt: python -m timetracker
"""

from timetracker.app import TimeTrackerApp
from timetracker.logger_config import setup_logger

logger = setup_logger(__name__)


def main() -> None:
    """Starte die TimeTrackerApp."""
    try:
        app = TimeTrackerApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Auf Wiedersehen")
        logger.info("Programm durch User beendet")
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        logger.critical(f"Kritischer Fehler: {e}", exc_info=True)


if __name__ == "__main__":
    main()
