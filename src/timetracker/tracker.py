"""App-Monitoring und Activity Tracking für TimeTracker."""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

import win32gui
import win32process
import psutil

from .exceptions import TrackerError
from .logger_config import setup_logger
from .database import Database

logger = setup_logger(__name__)


class AppTracker:
    """Überwacht Anwendungsnutzung und loggt Sessions (Fokus + Gesamtzeit pro App)."""

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

            # Pro-App Session State (app_name → state dict)
            self.sessions: Dict[str, Dict[str, Any]] = {}
            # Jede App hat: {
            #   "is_running": bool,              # App aktuell im Fokus
            #   "total_start_time": datetime,    # Wann die Session anfing
            #   "current_focus_start": datetime, # Anfang der Fokusphase
            #   "focus_accumulated": int,        # Summierte Fokuszeit
            #   "app_path": str,                 # Voller Pfad zur App
            # }

            logger.info(f"AppTracker initialisiert für Apps: {self.target_apps}")

        except Exception as e:
            logger.error(f"Fehler beim Initialisieren von AppTracker: {e}")
            raise TrackerError(f"AppTracker-Initialisierung fehlgeschlagen: {e}")

    def _load_config(self) -> dict:
        """Lade die config.json Datei."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise TrackerError(f"Config nicht gefunden: {self.config_path}")
        except json.JSONDecodeError:
            raise TrackerError(f"Config ungültig/beschädigt: {self.config_path}")

    def get_active_window_process(self) -> Tuple[Optional[str], Optional[str]]:
        """Hole Info über das aktive Fenster."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            try:
                process = psutil.Process(pid)
                return process.name(), process.exe()
            except psutil.NoSuchProcess:
                return None, None

        except Exception as e:
            logger.debug(f"Fehler beim Abrufen des aktiven Fensters: {e}")
            return None, None

    def is_target_app(self, process_name: Optional[str]) -> bool:
        """Prüfe ob Prozessname einer zu trackenden App entspricht."""
        if not process_name:
            return False

        process_name_lower = process_name.lower()

        for target_app in self.target_apps:
            if target_app.lower() in process_name_lower:
                return True

        return False

    def is_process_running(self, app_name: str) -> bool:
        """Prüfe ob Prozess mit gegebenem Namen noch läuft."""
        if not app_name:
            return False

        try:
            for proc in psutil.process_iter(["name"]):
                try:
                    if proc.info["name"] and proc.info["name"].lower() == app_name:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.debug(f"Fehler beim Prüfen von laufenden Prozessen: {e}")

        return False

    def _init_session(self, app_name: str, app_path: str) -> None:
        """Initialisiere eine neue Session für eine App."""
        now = datetime.now()
        self.sessions[app_name] = {
            "is_running": True,
            "total_start_time": now,
            "current_focus_start": now,
            "focus_accumulated": 0,
            "app_path": app_path,
        }

    def _end_session(self, app_name: str) -> None:
        """Beende die Session für eine App und speichere sie."""
        if app_name not in self.sessions:
            return

        state = self.sessions[app_name]
        end_time = datetime.now()

        # Falls noch Fokusphase offen, einsammeln
        if state["current_focus_start"]:
            focus_delta = int((end_time - state["current_focus_start"]).total_seconds())
            state["focus_accumulated"] += focus_delta

        total_duration = int((end_time - state["total_start_time"]).total_seconds())
        focus_duration = state["focus_accumulated"]

        # In DB speichern
        self.db.log_session(
            app_name,
            state["app_path"],
            state["total_start_time"],
            end_time,
            focus_duration,
            total_duration,
        )

        print(
            f"[⏹️  STOP] {app_name} um {end_time.strftime('%H:%M:%S')} "
            f"(focus={focus_duration}s, total={total_duration}s)"
        )
        logger.info(
            f"Session beendet: {app_name} "
            f"(focus={focus_duration}s, total={total_duration}s)"
        )

        # Session löschen
        del self.sessions[app_name]

    def start_monitoring(self) -> None:
        """Starte die Hauptüberwachungsschleife."""
        logger.info(f"Monitoring gestartet für {len(self.target_apps)} App(s)")
        print(f"\n[START] Monitoring aktiv für: {', '.join(self.target_apps)}")
        print("[INFO] Drücke CTRL+C zum Beenden...\n")

        try:
            while True:
                process_name, process_exe = self.get_active_window_process()
                is_active = self.is_target_app(process_name)

                # Bestimme aktuell fokussierte App
                active_app = process_name.lower() if is_active else None

                # ========== FÜR JEDE GETRACKTE APP ==========
                for app_name in self.sessions.copy().keys():
                    state = self.sessions[app_name]

                    # === App ist gerade im Fokus ===
                    if app_name == active_app and not state["is_running"]:
                        state["is_running"] = True
                        state["current_focus_start"] = datetime.now()

                        time_str = datetime.now().strftime("%H:%M:%S")
                        print(f"[▶️  START] {app_name} im Fokus um {time_str}")
                        logger.info(f"App im Fokus: {app_name}")

                    # === App verliert Fokus (aber läuft noch) ===
                    elif app_name != active_app and state["is_running"]:
                        state["is_running"] = False
                        now = datetime.now()

                        if state["current_focus_start"]:
                            focus_delta = int(
                                (now - state["current_focus_start"]).total_seconds()
                            )
                            state["focus_accumulated"] += focus_delta
                            state["current_focus_start"] = None

                        time_str = now.strftime("%H:%M:%S")
                        print(f"[⏸️  FOCUS LOST] {app_name} um {time_str}")
                        logger.info(
                            f"App Fokus verloren: {app_name}, "
                            f"fokus_accum={state['focus_accumulated']}s"
                        )

                    # === App läuft nicht mehr ===
                    if not self.is_process_running(app_name) and app_name in self.sessions:
                        self._end_session(app_name)

                # ========== NEUE APP KOMMT IN DEN FOKUS ==========
                if is_active and active_app not in self.sessions:
                    self._init_session(active_app, process_exe)

                    time_str = datetime.now().strftime("%H:%M:%S")
                    print(f"[▶️  START] {active_app} im Fokus um {time_str}")
                    logger.info(f"App im Fokus: {active_app}")

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n[STOP] Monitoring beendet durch User")

            # Speichere alle offenen Sessions
            for app_name in list(self.sessions.keys()):
                self._end_session(app_name)
                print(f"[SAVE] Session gespeichert: {app_name}")

            logger.info("Monitoring beendet")

        except Exception as e:
            logger.error(f"Fehler im Monitoring: {e}", exc_info=True)
            raise TrackerError(f"Fehler während Monitoring: {e}")
