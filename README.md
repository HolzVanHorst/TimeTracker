# ⏱️ TimeTracker

Automatische App-Überwachung und Zeittracking für Windows. Trackt Fokuszeit und Gesamtlaufzeit mehrerer Anwendungen parallel, mit detaillierten Statistiken und Windows-Autostart-Integration.

---

## ✨ Features

- **Multi-App Tracking** – Tracke mehrere Apps gleichzeitig und unabhängig
- **Fokuszeit + Gesamtzeit** – Unterscheidung zwischen Fokuszeit (App aktiv) und Gesamtlaufzeit (App offen)
- **Echtzeit-Monitoring** – Kontinuierliche Überwachung mit konfigurierbarem Check-Intervall (Standard: 500ms)
- **Detaillierte Statistiken** – Heute und Gesamt mit Öffnungen, Zeiten, Durchschnitte
- **SQLite-Datenbank** – Lokale Speicherung aller Tracking-Daten
- **Windows Autostart** – Optionale automatische Registrierung im Windows-Autostart (Registry-basiert)
- **Konfigurierbar** – JSON-basierte Config für Apps und Einstellungen
- **Logging** – Umfassendes Debugging und Error-Logging
- **Exe-Verpackung** – Mit PyInstaller als standalone `.exe` lauffähig

---

## 📋 Anforderungen

- **Python 3.9+**
- **Windows 10/11** (benötigt Win32 APIs)

### Dependencies

pywin32==306
psutil==6.0.0
pyinstaller==6.10.0

---

## 🚀 Installation & Start

### 1. Repository klonen

git clone https://github.com/HolzVanHorst/TimeTracker.git
cd TimeTracker

### 2. Dependencies installieren

pip install -r requirements.txt

### 3. Ausführen

**Mit Python:**

cd src
python -m timetracker

**Mit `.exe` (nach PyInstaller Build):**

python build.py
dist/TimeTracker.exe

---

## 📖 Verwendung

### Hauptmenü

============================================================
⏱️ TIME TRACKER

1.Tracking starten

2.Statistiken

3.Settings

4.Beenden

### Workflow

#### 1. **Initialisierung** (erste Nutzung)

Wahl: 1

Welche Apps sollen getracked werden? (komma-getrennt)
Beispiel: chrome.exe,code.exe,notepad.exe

Die Apps werden in `data/config.json` gespeichert.

#### 2. **Tracking starten**

Wahl: 1

▶️ Starte Monitoring für 2 App(s)
📱 Apps: chrome.exe, code.exe
📁 Database: data/tracker.db
⏹️ CTRL+C zum Beenden

Das Programm läuft kontinuierlich und loggt alle Fokuswechsel und Sessions.

#### 3. **Statistiken ansehen**

Wahl: 2

📱 CHROME.EXE
───────────────────────────────────────────
📅 HEUTE (13.12.2025)

* Öffnungen: 2x

* Fokuszeit: 0h 1m 23s

* Gesamtzeit: 0h 2m 45s

* Ø Fokus/Öffnung: 0m 41s

📈 GESAMT

* Öffnungen: 5x

* Fokuszeit (gesamt): 0h 5m 10s

* Gesamtzeit (gesamt): 0h 8m 30s

* Erste Nutzung: 2025-12-13

#### 4. **Settings**

Wahl: 3

🔄 Autostart: ✅ Aktiviert

📱 Getrackte Apps:

    -chrome.exe

    -code.exe

1.App hinzufügen

2.App entfernen

3.Autostart aktivieren

4.Autostart deaktivieren

5.Zurück

---

## 🎯 Fokuszeit vs. Gesamtzeit

**Fokuszeit** = Zeit, in der die App im Vordergrund aktiv war.

**Gesamtzeit** = Zeit, in der die App geöffnet/gelaufen war (inklusive Hintergrund).

**Beispiel:**

- Chrome öffnen: 14:00
- Im Fokus: 14:00 – 14:05 (5 Min)
- Im Hintergrund: 14:05 – 14:12 (7 Min)
- Chrome schließen: 14:12
- Fokuszeit: **5 Minuten**
- Gesamtzeit: **12 Minuten**

---

## 🔄 Autostart (Windows Registry)

### Aktivieren

Settings → Autostart aktivieren

Das Programm wird beim nächsten Windows-Start automatisch gestartet und läuft im Hintergrund.

**Registry-Eintrag:** `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\TimeTracker`

### Deaktivieren

Settings → Autostart deaktivieren

---

## 🛠️ Build zu `.exe`

python build.py

Die `.exe` wird nach `dist/TimeTracker.exe` kompiliert und kann standalone ausgeführt werden.

---

## 📝 Logging

Alle Ausgaben werden in `data/tracker.log` protokolliert:

2025-12-13 22:25:07,413 - timetracker.tracker - INFO - App im Fokus: chrome.exe
2025-12-13 22:25:21,443 - timetracker.tracker - INFO - App Fokus verloren: chrome.exe, fokus_accum=10s
2025-12-13 22:25:22,963 - timetracker.database - INFO - Session geloggt: chrome.exe (focus=10s, total=15s)

---

## 🐛 Troubleshooting

### „No module named 'timetracker'"

cd src
python -m timetracker

### Config nicht gefunden

Starten Sie das Programm und wählen Sie Punkt 1 (Initialisierung).

### Tracking erkennt meine App nicht

Prüfen Sie den genauen Prozessnamen in der `config.json`:

In Windows Task Manager unter "Prozesse" nachschauen
z.B. "firefox.exe", "vlc.exe" statt "Firefox", "VLC"

---

## 📄 Lizenz

MIT License – Siehe LICENSE-Datei.

---

## 👨‍💻 Autor

**Mike** – Development & Debugging

---

## 🤝 Support

Bei Fragen oder Bugs: [GitHub Issues](https://github.com/HolzVanHorst/TimeTracker/issues)

---

**Viel Erfolg beim Tracken! ⏱️**