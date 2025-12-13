# REQUIREMENTS

## MVP (Minimum Viable Product)

### Funktional
- [ ] Mehrere Apps tracken
- [ ] Start/Stop erkennen
- [ ] In SQLite speichern
- [ ] Statistiken anzeigen
- [ ] Im Autostart laufen

### Technisch
- [ ] Klassenbasiert
- [ ] Type Hints
- [ ] Logging
- [ ] Exception Handling
- [ ] Zentrale Strings (i18n-ready)

## 🏗️ Technische Anforderungen (Wie soll es tun?)

- Python 3.9+
- Windows-only (pywin32, WMI)
- SQLite für Persistierung
- CLI-basiert
- Klassenbasiert
- Logging für Debugging
- Zentrale Texte (i18n-ready)

## 🗂️ Architektur-Entscheidungen

- Separation of Concerns (jede Klasse = eine Aufgabe)
- Type Hints überall
- Custom Exceptions
- Main.py = nur Entry Point

## 📊 Datenmodell

config.json:
{
"target_apps": ["chrome.exe", "vscode.exe"],
"db_path": "data/tracker.db",
"check_interval": 0.5
}

SQLite:
CREATE TABLE app_sessions (
id INTEGER PRIMARY KEY,
app_name TEXT NOT NULL,
app_path TEXT,
start_time DATETIME NOT NULL,
end_time DATETIME,
duration_seconds INTEGER,
date DATE
);

app_sessions (id, app_name, start_time, end_time, duration_seconds, date)


## 🔄 User Workflows

1. **Setup**: python main.py → Init → Apps eingeben
2. **Tracking**: python main.py → Run → Still im Hintergrund
3. **Stats**: python main.py → Stats → Anzeigen
4. **Settings**: python main.py → Settings → Apps ändern
5. **Autostart**: TimeTracker.exe --autostart → Still
