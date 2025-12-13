"""Hauptanwendungsklasse für TimeTracker mit CLI-Interface."""

import json
import sys
from pathlib import Path
from typing import Optional

from .config import CONFIG_PATH, DEFAULT_CONFIG, AUTOSTART_PARAM
from .exceptions import ConfigError
from .logger_config import setup_logger
from .strings import Messages
from .database import Database
from .tracker import AppTracker

logger = setup_logger(__name__)


class TimeTrackerApp:
    """Hauptanwendungsklasse für TimeTracker.
    
    Verwaltet:
    - Konfiguration (Laden/Speichern)
    - CLI-Menu
    - Tracking-Prozess
    - Statistiken
    """
    
    def __init__(self, config_path: Path | str = CONFIG_PATH) -> None:
        """Initialisiere TimeTrackerApp.
        
        Args:
            config_path: Pfad zur config.json
        """
        if not isinstance(config_path, Path):
            config_path = Path(config_path)
        
        self.config_path: Path = config_path
        self.autostart_mode: bool = AUTOSTART_PARAM in sys.argv
        self.config: Optional[dict] = None
        
        logger.info(f"TimeTrackerApp initialisiert (Autostart: {self.autostart_mode})")
    
    # ========== CONFIG MANAGEMENT ==========
    
    def config_exists(self) -> bool:
        """Prüfe ob config.json existiert.
        
        Returns:
            bool: True wenn Datei existiert
        """
        exists = self.config_path.exists()
        logger.debug(f"Config existiert: {exists}")
        return exists
    
    def load_config(self) -> Optional[dict]:
        """Lade die config.json Datei.
        
        Returns:
            dict: Geladene Konfiguration
            None: Wenn Datei nicht existiert oder ungültig ist
        """
        try:
            if not self.config_exists():
                logger.warning("Config-Datei nicht gefunden")
                return None
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validiere die Config
            self._validate_config(config)
            self.config = config
            logger.info("Config erfolgreich geladen")
            return config
        
        except json.JSONDecodeError as e:
            logger.error(f"Config-Datei beschädigt: {e}")
            return None
        except ConfigError as e:
            logger.error(f"Config ungültig: {e}")
            return None
        except Exception as e:
            logger.error(f"Fehler beim Laden der Config: {e}")
            return None
    
    def save_config(self, config: dict) -> bool:
        """Speichere die config.json Datei.
        
        Args:
            config: Zu speichernde Konfiguration
            
        Returns:
            bool: True wenn erfolgreich gespeichert
        """
        try:
            # Validiere zuerst
            self._validate_config(config)
            
            # Speichere
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.config = config
            logger.info(f"Config gespeichert: {self.config_path}")
            return True
        
        except ConfigError as e:
            logger.error(f"Config ungültig: {e}")
            return False
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Config: {e}")
            return False
    
    @staticmethod
    def _validate_config(config: dict) -> None:
        """Validiere die Config-Struktur.
        
        Args:
            config: Zu validierende Config
            
        Raises:
            ConfigError: Wenn Config ungültig ist
        """
        # Prüfe erforderliche Keys
        required_keys = ["target_apps", "db_path", "check_interval"]
        for key in required_keys:
            if key not in config:
                raise ConfigError(f"Erforderlicher Key fehlt: {key}")
        
        # target_apps muss Liste sein
        if not isinstance(config["target_apps"], list):
            raise ConfigError("target_apps muss eine Liste sein")
        
        # target_apps darf nicht leer sein
        if len(config["target_apps"]) == 0:
            raise ConfigError("target_apps darf nicht leer sein")
        
        # Alle Apps müssen Strings sein
        for app in config["target_apps"]:
            if not isinstance(app, str):
                raise ConfigError(f"App '{app}' ist kein String")
        
        # check_interval muss Zahl sein
        if not isinstance(config["check_interval"], (int, float)):
            raise ConfigError("check_interval muss eine Zahl sein")
    
    # ========== COMMANDS ==========
    
    def cmd_initialize(self) -> bool:
        """Initialisiere die App (erstelle Config + DB).
        
        Returns:
            bool: True wenn erfolgreich
        """
        print(f"\n{Messages.SEPARATOR}")
        print(f"  {Messages.HEADER_INIT}")
        print(f"{Messages.SEPARATOR}\n")
        
        # Hole App-Namen vom User
        apps_input = input(Messages.PROMPT_APPS).strip()
        
        if not apps_input:
            print(Messages.MSG_ERROR_INVALID)
            logger.warning("Ungültige App-Eingabe während Initialisierung")
            return False
        
        # Parse Komma-getrennte Apps
        apps = [app.strip().lower() for app in apps_input.split(',')]
        apps = [app for app in apps if app]  # Leere entfernen
        
        if not apps:
            print(Messages.MSG_ERROR_INVALID)
            return False
        
        # Erstelle neue Config
        config = DEFAULT_CONFIG.copy()
        config["target_apps"] = apps
        
        # Speichere Config
        if not self.save_config(config):
            return False
        
        # Initialisiere Datenbank
        try:
            db = Database(config["db_path"])
            print(f"\n{Messages.MSG_SUCCESS_CONFIG.format(len(apps))}")
            print(f"📱 Apps: {', '.join(apps)}\n")
            logger.info(f"App initialisiert mit {len(apps)} App(s): {apps}")
            return True
        
        except Exception as e:
            print(f"{Messages.MSG_ERROR_GENERIC.format(e)}")
            logger.error(f"Fehler beim Initialisieren: {e}")
            return False
    
    def cmd_run(self) -> None:
        """Starte das Monitoring."""
        config = self.load_config()
        if not config:
            print(Messages.MSG_ERROR_NO_CONFIG)
            return
        
        num_apps = len(config['target_apps'])
        print(f"\n{Messages.MSG_INFO_START.format(num_apps)}")
        print(f"📱 Apps: {', '.join(config['target_apps'])}")
        print(f"📁 Database: {config['db_path']}")
        print(f"{Messages.MSG_INFO_RUNNING}\n")
        
        try:
            tracker = AppTracker(self.config_path)
            tracker.start_monitoring()
        
        except KeyboardInterrupt:
            print(f"\n{Messages.MSG_SUCCESS_STOP}")
            logger.info("Monitoring durch User beendet")
        
        except Exception as e:
            print(f"{Messages.MSG_ERROR_GENERIC.format(e)}")
            logger.error(f"Fehler beim Monitoring: {e}")
    
    def cmd_stats(self) -> None:
        """Zeige Statistiken für alle Apps."""
        from datetime import datetime
        
        print(f"\n{Messages.SEPARATOR}")
        print(f"  {Messages.HEADER_STATS}")
        print(f"{Messages.SEPARATOR}\n")
        
        config = self.load_config()
        if not config:
            print(Messages.MSG_ERROR_NO_CONFIG)
            return
        
        try:
            db = Database(config['db_path'])
            
            # Zeige Stats für jede App
            for i, app in enumerate(config['target_apps']):
                if i > 0:
                    print(f"\n{'─'*60}")
                
                print(f"📱 {app.upper()}")
                print(f"{'─'*60}")
                
                # ========== HEUTE ==========
                today_stats = db.get_stats_today(app)
                print(f"\n{Messages.STATS_TODAY.format(datetime.now().strftime('%d.%m.%Y'))}")
                
                if today_stats and today_stats[0]:
                    opens, total_sec, avg_sec = today_stats
                    hours = total_sec // 3600
                    minutes = (total_sec % 3600) // 60
                    seconds = total_sec % 60
                    avg_min = int(avg_sec // 60) if avg_sec else 0
                    avg_sec_remainder = int(avg_sec % 60) if avg_sec else 0
                    
                    print(Messages.STATS_OPENS.format(opens))
                    print(Messages.STATS_TIME.format(hours, minutes, seconds))
                    print(Messages.STATS_AVG.format(avg_min, avg_sec_remainder))
                else:
                    print(Messages.STATS_NO_DATA)
                
                # ========== GESAMT ==========
                all_stats = db.get_stats_all_time(app)
                print(f"\n{Messages.STATS_ALL}")
                
                if all_stats and all_stats[0]:
                    opens, total_sec, first_use = all_stats
                    hours = total_sec // 3600
                    minutes = (total_sec % 3600) // 60
                    seconds = total_sec % 60
                    
                    print(Messages.STATS_OPENS.format(opens))
                    print(Messages.STATS_TIME.format(hours, minutes, seconds))
                    print(Messages.STATS_FIRST.format(first_use[:10]))
                else:
                    print(Messages.STATS_NO_DATA)
        
        except Exception as e:
            print(f"{Messages.MSG_ERROR_GENERIC.format(e)}")
            logger.error(f"Fehler beim Abrufen der Statistiken: {e}")
    
    def cmd_settings(self) -> None:
        """Bearbeite Settings (App-Management + Autostart)."""
        config = self.load_config()
        if not config:
            print(Messages.MSG_ERROR_NO_CONFIG)
            return
        
        from .autostart import AutostartManager
        
        while True:
            print(f"\n{Messages.SEPARATOR}")
            print(f"  {Messages.HEADER_SETTINGS}")
            print(f"{Messages.SEPARATOR}\n")
            
            # ========== AUTOSTART STATUS ==========
            autostart_status = "✅ Aktiviert" if AutostartManager.is_enabled() else "❌ Deaktiviert"
            print(f"🔄 Autostart: {autostart_status}\n")
            
            # ========== GETRACKTE APPS ==========
            print("📱 Getrackte Apps:")
            for i, app in enumerate(config['target_apps'], 1):
                print(f"   {i}. {app}")
            
            print(f"\n1. App hinzufügen")
            print(f"2. App entfernen")
            print(f"3. Autostart aktivieren")
            print(f"4. Autostart deaktivieren")
            print(f"5. Zurück")
            
            choice = input(f"\n{Messages.PROMPT_CHOICE}").strip()
            
            if choice == "1":
                self._add_app(config)
            elif choice == "2":
                self._remove_app(config)
            elif choice == "3":
                if AutostartManager.enable():
                    print("\n✅ Autostart aktiviert!")
                    print("⚠️  Programm wird beim nächsten Start automatisch ausgeführt.")
                else:
                    print("\n❌ Fehler beim Aktivieren von Autostart")
            elif choice == "4":
                if AutostartManager.disable():
                    print("\n✅ Autostart deaktiviert!")
                else:
                    print("\n❌ Fehler beim Deaktivieren von Autostart")
            elif choice == "5":
                break
            else:
                print(Messages.MSG_ERROR_INVALID)

    
    def _add_app(self, config: dict) -> None:
        """Füge eine App zur Liste hinzu.
        
        Args:
            config: Die aktuelle Config
        """
        new_app = input(f"\n{Messages.PROMPT_ADD_APP}").strip().lower()
        
        if not new_app:
            print(Messages.MSG_ERROR_INVALID)
            return
        
        # Prüfe ob App bereits existiert
        if new_app in config['target_apps']:
            print(f"❌ App existiert bereits: {new_app}")
            logger.warning(f"Versuch, doppelte App hinzuzufügen: {new_app}")
            return
        
        # Füge hinzu und speichere
        config['target_apps'].append(new_app)
        if self.save_config(config):
            print(f"\n{Messages.MSG_SUCCESS_APP_ADDED.format(new_app)}")
            logger.info(f"App hinzugefügt: {new_app}")
        else:
            config['target_apps'].remove(new_app)  # Rollback
    
    def _remove_app(self, config: dict) -> None:
        """Entferne eine App aus der Liste.
        
        Args:
            config: Die aktuelle Config
        """
        # Verhindere, dass die Liste leer wird
        if len(config['target_apps']) == 1:
            print("❌ Mindestens eine App muss getracked werden!")
            return
        
        remove_app = input(f"\n{Messages.PROMPT_REMOVE_APP}").strip().lower()
        
        # Prüfe ob App existiert
        if remove_app not in config['target_apps']:
            print(f"❌ App nicht gefunden: {remove_app}")
            logger.warning(f"Versuch, nicht existierende App zu entfernen: {remove_app}")
            return
        
        # Entferne und speichere
        config['target_apps'].remove(remove_app)
        if self.save_config(config):
            print(f"\n{Messages.MSG_SUCCESS_APP_REMOVED.format(remove_app)}")
            logger.info(f"App entfernt: {remove_app}")
        else:
            config['target_apps'].append(remove_app)  # Rollback
    
    # ========== MENU ==========
    
    def show_menu(self) -> None:
        """Zeige das interaktive Hauptmenü."""
        while True:
            print(f"\n{Messages.SEPARATOR}")
            print(f"  {Messages.HEADER_MAIN}")
            print(f"{Messages.SEPARATOR}\n")
            
            # ========== WENN KEINE CONFIG ==========
            if not self.config_exists():
                print(Messages.MSG_INFO_CONFIG_MISSING)
                print(f"{Messages.MENU_INIT}")
                print(f"{Messages.MENU_EXIT.replace('4.', '2.')}")
                
                choice = input(f"\n{Messages.PROMPT_CHOICE}").strip()
                
                if choice == "1":
                    self.cmd_initialize()
                elif choice == "2":
                    break
                else:
                    print(Messages.MSG_ERROR_INVALID)
            
            # ========== WENN CONFIG EXISTIERT ==========
            else:
                print(f"{Messages.MENU_RUN}")
                print(f"{Messages.MENU_STATS}")
                print(f"{Messages.MENU_SETTINGS}")
                print(f"{Messages.MENU_EXIT}")
                
                choice = input(f"\n{Messages.PROMPT_CHOICE}").strip()
                
                if choice == "1":
                    self.cmd_run()
                elif choice == "2":
                    self.cmd_stats()
                elif choice == "3":
                    self.cmd_settings()
                elif choice == "4":
                    break
                else:
                    print(Messages.MSG_ERROR_INVALID)
        
        print(f"\n{Messages.GOODBYE}\n")
    
    # ========== AUTOSTART MODE ==========
    
    def run_autostart(self) -> None:
        """Stille Variante für Autostart (kein Output).
        
        Läuft im Hintergrund ohne Console-Output.
        Nur Fehler werden in Log-Datei geschrieben.
        """
        config = self.load_config()
        if not config:
            logger.warning("Config nicht gefunden im Autostart-Mode")
            return
        
        try:
            tracker = AppTracker(self.config_path)
            tracker.start_monitoring()
        except Exception as e:
            logger.error(f"Fehler im Autostart-Mode: {e}", exc_info=True)
    
    # ========== MAIN ENTRY ==========
    
    def run(self) -> None:
        """Starte die Anwendung.
        
        Unterscheidet zwischen:
        - Autostart-Mode (silent)
        - Manueller Start (mit Menu)
        """
        if self.autostart_mode:
            # Autostart: Keine Ausgabe, nur tracken
            self.run_autostart()
        else:
            # Manuell: Interaktives Menu
            self.show_menu()
