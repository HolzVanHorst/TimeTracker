"""Alle UI-Texte für TimeTracker."""


class Messages:
    """Zentrale Text-Konstanten."""
    
    # ========== HEADERS ==========
    HEADER_MAIN = "⏱️  TIME TRACKER"
    HEADER_INIT = "⏱️  TIME TRACKER - INITIALISIERUNG"
    HEADER_SETTINGS = "⚙️  SETTINGS"
    HEADER_STATS = "📊 STATISTIKEN"
    
    # ========== PROMPTS ==========
    PROMPT_APPS = "Welche Apps sollen getracked werden? (Komma-getrennt, z.B. chrome.exe,vscode.exe): "
    PROMPT_ADD_APP = "App hinzufügen (z.B. vscode.exe): "
    PROMPT_REMOVE_APP = "App entfernen: "
    PROMPT_CHOICE = "Wahl: "
    
    # ========== MENU ==========
    MENU_INIT = "1. Initialisierung"
    MENU_RUN = "1. Tracking starten"
    MENU_STATS = "2. Statistiken"
    MENU_SETTINGS = "3. Settings"
    MENU_EXIT = "4. Beenden"
    
    # ========== SETTINGS MENU ==========
    MENU_SETTINGS_ADD = "1. App hinzufügen"
    MENU_SETTINGS_REMOVE = "2. App entfernen"
    MENU_SETTINGS_BACK = "3. Zurück"

    
    # ========== SUCCESS ==========
    MSG_SUCCESS_CONFIG = "✅ Config erstellt mit {} App(s)"
    MSG_SUCCESS_APP_ADDED = "✅ App hinzugefügt: {}"
    MSG_SUCCESS_APP_REMOVED = "✅ App entfernt: {}"
    MSG_SUCCESS_STOP = "✅ Monitoring beendet"
    
    # ========== ERROR ==========
    MSG_ERROR_INVALID = "❌ Ungültige Eingabe!"
    MSG_ERROR_NO_CONFIG = "❌ Config nicht gefunden!"
    MSG_ERROR_NO_DATA = "❌ Keine Daten vorhanden"
    MSG_ERROR_GENERIC = "❌ Fehler: {}"
    
    # ========== INFO ==========
    MSG_INFO_CONFIG_MISSING = "⚠️  Config nicht gefunden!\n"
    MSG_INFO_START = "▶️  Starte Monitoring für {} App(s)"
    MSG_INFO_RUNNING = "⏹️  CTRL+C zum Beenden"
    
    # ========== STATS ==========
    STATS_TODAY = "📅 HEUTE ({})"
    STATS_ALL = "📈 GESAMT"
    STATS_OPENS = "• Öffnungen: {}x"
    STATS_TIME = "• Gesamtzeit: {}h {}m"
    STATS_AVG = "• Ø pro Öffnung: {}m"
    STATS_FIRST = "• Erste Nutzung: {}"
    
    # ========== STATS MESSAGES (DIESE HIER HINZUFÜGEN) ==========
    STATS_TODAY = "📅 HEUTE ({})"
    STATS_ALL = "📈 GESAMT"
    STATS_OPENS = "• Öffnungen: {}x"
    STATS_TIME = "• Gesamtzeit: {}h {}m"
    STATS_AVG = "• Ø pro Öffnung: {}m"
    STATS_FIRST = "• Erste Nutzung: {}"
    STATS_NO_DATA = "Keine Daten"
    
    # ========== SEPARATOR ==========
    SEPARATOR = "=" * 60
    GOODBYE = "Auf Wiedersehen!"
