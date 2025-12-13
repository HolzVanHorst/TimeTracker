"""Build-Script zum Erstellen der TimeTracker.exe mit PyInstaller."""

import os
import sys
from pathlib import Path

def build_exe():
    """Baue die .exe mit PyInstaller."""
    
    # Pfade
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    print("=" * 60)
    print("🔨 TimeTracker .exe Builder")
    print("=" * 60)
    
    # PyInstaller Command
    cmd = [
        "pyinstaller",
        "--name=TimeTracker",
        "--onefile",
        # "--windowed",
        "--hidden-import=sqlite3",           # ← HINZUGEFÜGT
        "--hidden-import=win32gui",          # ← HINZUGEFÜGT
        "--hidden-import=win32process",      # ← HINZUGEFÜGT
        "--hidden-import=psutil",            # ← HINZUGEFÜGT
        f"--add-data=src/timetracker:timetracker",
        str(src_dir / "timetracker" / "__main__.py"),
    ]
    
    print(f"\n📦 Starte Build mit:")
    print(f"   {' '.join(cmd)}\n")
    
    # Führe PyInstaller aus
    result = os.system(" ".join(cmd))
    
    if result == 0:
        print("\n" + "=" * 60)
        print("✅ Build erfolgreich!")
        print("=" * 60)
        print(f"\n📁 .exe Datei:")
        print(f"   {dist_dir / 'TimeTracker.exe'}")
        print(f"\n🚀 Start mit:")
        print(f"   {dist_dir / 'TimeTracker.exe'}")
    else:
        print("\n❌ Build fehlgeschlagen!")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
