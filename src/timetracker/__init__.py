"""TimeTracker - Automatische App-Nutzungsüberwachung.

Ein einfaches Tool zum Tracken von Anwendungsnutzung unter Windows.

Beispiel:
    >>> from timetracker.app import TimeTrackerApp
    >>> app = TimeTrackerApp()
    >>> app.run()
"""

__version__ = "0.1.0"
__author__ = "Mike ©"
__all__ = ["TimeTrackerApp", "AppTracker", "Database"]

from timetracker.app import TimeTrackerApp
from timetracker.tracker import AppTracker
from timetracker.database import Database
