"""Windows Autostart-Verwaltung für TimeTracker."""

import winreg
from pathlib import Path
from .logger_config import setup_logger

logger = setup_logger(__name__)


class AutostartManager:
    """Verwaltet Autostart-Einträge in der Windows Registry."""
    
    REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    ENTRY_NAME = "TimeTracker"
    
    @staticmethod
    def get_exe_path() -> str:
        """Hole den Pfad zur TimeTracker.exe.
        
        Returns:
            str: Voller Pfad zur .exe
        """
        # Wenn als .exe ausgeführt: sys.executable zeigt auf TimeTracker.exe
        # Wenn als Python-Script: zeigt auf python.exe
        
        import sys
        
        # Check ob wir als .exe laufen
        if sys.executable.endswith("TimeTracker.exe"):
            return sys.executable
        
        # Sonst: .exe sollte neben diesem Script sein
        exe_path = Path(__file__).parent.parent.parent / "dist" / "TimeTracker.exe"
        
        if exe_path.exists():
            return str(exe_path)
        
        # Fallback: error
        raise FileNotFoundError(f"TimeTracker.exe nicht gefunden: {exe_path}")
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Prüfe ob Autostart aktiviert ist.
        
        Returns:
            bool: True wenn aktiv
        """
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REGISTRY_PATH,
                0,
                winreg.KEY_READ
            ) as key:
                value, _ = winreg.QueryValueEx(key, cls.ENTRY_NAME)
                return bool(value)
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Fehler beim Prüfen von Autostart: {e}")
            return False
    
    @classmethod
    def enable(cls) -> bool:
        """Aktiviere Autostart.
        
        Returns:
            bool: True wenn erfolgreich
        """
        try:
            exe_path = cls.get_exe_path()
            
            # Schreibe in Registry: "exe_path --autostart"
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REGISTRY_PATH,
                0,
                winreg.KEY_WRITE
            ) as key:
                winreg.SetValueEx(
                    key,
                    cls.ENTRY_NAME,
                    0,
                    winreg.REG_SZ,
                    f'"{exe_path}" --autostart'
                )
            
            logger.info(f"Autostart aktiviert: {exe_path}")
            return True
        
        except Exception as e:
            logger.error(f"Fehler beim Aktivieren von Autostart: {e}")
            return False
    
    @classmethod
    def disable(cls) -> bool:
        """Deaktiviere Autostart.
        
        Returns:
            bool: True wenn erfolgreich
        """
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REGISTRY_PATH,
                0,
                winreg.KEY_WRITE
            ) as key:
                winreg.DeleteValue(key, cls.ENTRY_NAME)
            
            logger.info("Autostart deaktiviert")
            return True
        
        except FileNotFoundError:
            # Entry existiert nicht → schon deaktiviert
            return True
        except Exception as e:
            logger.error(f"Fehler beim Deaktivieren von Autostart: {e}")
            return False
