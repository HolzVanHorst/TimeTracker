"""App-Monitoring und Activity Tracking für TimeTracker."""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

import win32gui
import win32process
import psutil

from .exceptions import TrackerError
from .logger_config import setup_logger
from .database import Database

logger = setup_logger(__name__)


class AppTracker:
    """Überwacht Anwendungsnutzung und loggt Sessions."""
    
    def __init__(self, config_path: Path | str) -> None:
        """Initialisiere den AppTracker.
        
        Args:
            config_path: Pfad zur config.json
            
        Raises:
            TrackerError: Wenn Config nicht geladen werden kann
        """
        self.config_path = Path(config_path)
        
        try:
            self.config = self._load_config()
            self.target_apps = self.config["target_apps"]
            self.check_interval = self.config["check_interval"]
            self.db = Database(self.config["db_path"])
            
            # Tracking-State
            self.is_running = False
            self.start_time: Optional[datetime] = None
            self.app_name: Optional[str] = None
            self.app_path: Optional[str] = None
            
            logger.info(f"AppTracker initialisiert für Apps: {self.target_apps}")
        
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren von AppTracker: {e}")
            raise TrackerError(f"AppTracker-Initialisierung fehlgeschlagen: {e}")
    
    def _load_config(self) -> dict:
        """Lade die config.json Datei.
        
        Returns:
            dict: Die Konfiguration
            
        Raises:
            TrackerError: Wenn Config nicht lesbar ist
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise TrackerError(f"Config nicht gefunden: {self.config_path}")
        except json.JSONDecodeError:
            raise TrackerError(f"Config ungültig/beschädigt: {self.config_path}")
    
    def get_active_window_process(self) -> Tuple[Optional[str], Optional[str]]:
        """Hole Info über das aktive Fenster.
        
        Returns:
            Tuple: (process_name, process_exe) oder (None, None)
            
        Beispiel:
            ("chrome.exe", "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
        """
        try:
            # Hole das aktive Fenster
            hwnd = win32gui.GetForegroundWindow()
            
            # Hole die Process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            try:
                # Hole Process-Info
                process = psutil.Process(pid)
                return process.name(), process.exe()
            
            except psutil.NoSuchProcess:
                # Process existiert nicht mehr
                return None, None
        
        except Exception as e:
            logger.debug(f"Fehler beim Abrufen des aktiven Fensters: {e}")
            return None, None
    
    def is_target_app(self, process_name: Optional[str], 
                     process_exe: Optional[str]) -> bool:
        """Prüfe ob aktive App eine der zu trackenden Apps ist.
        
        Args:
            process_name: Name des Processes (z.B. "chrome.exe")
            process_exe: Voller Pfad zur .exe
            
        Returns:
            bool: True wenn App getracked werden soll
        """
        if not process_name or not process_exe:
            return False
        
        # Prüfe gegen ALLE Apps in der Liste
        process_name_lower = process_name.lower()
        
        for target_app in self.target_apps:
            if target_app.lower() in process_name_lower:
                return True
        
        return False
    
    def start_monitoring(self) -> None:
        """Starte die Hauptüberwachungsschleife.
        
        Diese Methode läuft kontinuierlich bis der User CTRL+C drückt.
        Sie prüft alle 500ms, welche App aktiv ist und loggt Sessions.
        
        Raises:
            KeyboardInterrupt: Wenn User CTRL+C drückt
        """
        logger.info(f"Monitoring gestartet für {len(self.target_apps)} App(s)")
        print(f"\n[START] Monitoring aktiv für: {', '.join(self.target_apps)}")
        print(f"[INFO] Drücke CTRL+C zum Beenden...\n")
        
        try:
            while True:
                # Hole aktives Fenster
                process_name, process_exe = self.get_active_window_process()
                is_active = self.is_target_app(process_name, process_exe)
                
                # ========== APP WURDE GERADE GESTARTET ==========
                if is_active and not self.is_running:
                    self.is_running = True
                    self.start_time = datetime.now()
                    self.app_name = process_name.lower()
                    self.app_path = process_exe
                    
                    time_str = self.start_time.strftime('%H:%M:%S')
                    print(f"[▶️  START] {self.app_name} um {time_str}")
                    logger.info(f"App gestartet: {self.app_name}")
                
                # ========== APP WURDE GERADE GESCHLOSSEN/MINIMIERT ==========
                elif not is_active and self.is_running:
                    self.is_running = False
                    end_time = datetime.now()
                    
                    # Speichere die Session in DB
                    duration = int((end_time - self.start_time).total_seconds())
                    minutes = duration // 60
                    seconds = duration % 60
                    
                    self.db.log_session(
                        self.app_name.lower(),
                        self.app_path,
                        self.start_time,
                        end_time
                    )
                    
                    time_str = end_time.strftime('%H:%M:%S')
                    print(f"[⏹️  STOP] {self.app_name} um {time_str} ({minutes}m {seconds}s)")
                    logger.info(f"App gestoppt: {self.app_name} ({duration}s)")
                
                # Warte ein bisschen bevor nächste Prüfung
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            # User hat CTRL+C gedrückt
            print("\n[STOP] Monitoring beendet durch User")
            
            # Falls noch eine App läuft, speichern wir sie ab
            if self.is_running and self.app_name and self.start_time:
                end_time = datetime.now()
                self.db.log_session(
                    self.app_name.lower(),
                    self.app_path,
                    self.start_time,
                    end_time
                )
                print(f"[SAVE] Letzte Session gespeichert")
                logger.info(f"Letzte Session gespeichert: {self.app_name}")
            
            logger.info("Monitoring beendet")
        
        except Exception as e:
            logger.error(f"Fehler im Monitoring: {e}", exc_info=True)
            raise TrackerError(f"Fehler während Monitoring: {e}")
