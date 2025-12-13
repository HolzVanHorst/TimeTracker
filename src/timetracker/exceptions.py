"""Custom Exceptions für TimeTracker."""


class TimeTrackerError(Exception):
    """Base Exception für alle TimeTracker Fehler."""
    pass


class ConfigError(TimeTrackerError):
    """Exception für Konfigurationsfehler."""
    pass


class DatabaseError(TimeTrackerError):
    """Exception für Datenbankfehler."""
    pass


class TrackerError(TimeTrackerError):
    """Exception für Tracker-Fehler."""
    pass
