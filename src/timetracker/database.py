"""SQLite Datenbank-Operationen für TimeTracker."""

import sqlite3
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

from .exceptions import DatabaseError
from .logger_config import setup_logger

logger = setup_logger(__name__)


class Database:
    """Verwaltet SQLite-Datenbankoperationen."""
    
    def __init__(self, db_path: str | Path) -> None:
        """Initialisiere Datenbank.
        
        Args:
            db_path: Pfad zur SQLite-Datenbankdatei
            
        Raises:
            DatabaseError: Wenn DB nicht initialisiert werden kann
        """
        self.db_path = Path(db_path)
        try:
            self.init_db()
            logger.info(f"Database initialisiert: {self.db_path}")
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der DB: {e}")
            raise DatabaseError(f"DB-Initialisierung fehlgeschlagen: {e}")
    
    def init_db(self) -> None:
        """Erstelle Tabelle falls sie nicht existiert."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT NOT NULL,
                app_path TEXT,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                duration_seconds INTEGER,
                date DATE DEFAULT CURRENT_DATE
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_session(self, app_name: str, app_path: str, 
                   start_time: datetime, end_time: datetime) -> None:
        """Speichere eine App-Session in der DB.
        
        Args:
            app_name: Name der App (z.B. "notepad.exe")
            app_path: Voller Pfad zur App
            start_time: Startzeitpunkt
            end_time: Stoppzeitpunkt
            
        Raises:
            DatabaseError: Wenn Speichern fehlschlägt
        """
        try:
            duration = int((end_time - start_time).total_seconds())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO app_sessions 
                (app_name, app_path, start_time, end_time, duration_seconds, date)
                VALUES (?, ?, ?, ?, ?, DATE('now'))
            """, (app_name, app_path, start_time, end_time, duration))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Session geloggt: {app_name} ({duration}s)")
        
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Session: {e}")
            raise DatabaseError(f"Session konnte nicht geloggt werden: {e}")
    
    def get_stats_today(self, app_name: str) -> Optional[Tuple[int, int, float]]:
        """Hole Statistiken für heute.
        
        Args:
            app_name: Name der App
            
        Returns:
            Tuple: (opens, total_seconds, avg_seconds) oder None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as opens,
                    SUM(duration_seconds) as total_seconds,
                    AVG(duration_seconds) as avg_seconds
                FROM app_sessions
                WHERE app_name = ? AND date = DATE('now')
            """, (app_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result
        
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Heute-Stats: {e}")
            return None
    
    def get_stats_all_time(self, app_name: str) -> Optional[Tuple[int, int, str]]:
        """Hole Gesamtstatistiken.
        
        Args:
            app_name: Name der App
            
        Returns:
            Tuple: (opens, total_seconds, first_use_date) oder None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as opens,
                    SUM(duration_seconds) as total_seconds,
                    MIN(start_time) as first_use
                FROM app_sessions
                WHERE app_name = ?
            """, (app_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result
        
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Gesamt-Stats: {e}")
            return None
