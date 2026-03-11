#!/bin/bash
# sync-back.sh - Kopiert Dateien von der Produktion zurueck ins source-Repo
# Verwendung: sudo /var/www/deepseek-chat/sync-back.sh <username>

# Root-Pruefung
if [ "$(id -u)" -ne 0 ]; then
    echo "FEHLER: Dieses Script muss als root ausgefuehrt werden!"
    echo "Verwendung: sudo /var/www/deepseek-chat/sync-back.sh <username>"
    exit 1
fi

# Parameter-Pruefung
if [ -z "$1" ]; then
    echo "FEHLER: Kein Benutzername angegeben!"
    echo "Verwendung: sudo /var/www/deepseek-chat/sync-back.sh <username>"
    exit 1
fi

SOURCE_DIR="/home/$1/multi-llm-chat/var/www/deepseek-chat"
PROD_DIR="/var/www/deepseek-chat"

# Zielverzeichnis-Pruefung
if [ ! -d "$SOURCE_DIR" ]; then
    echo "FEHLER: Zielverzeichnis nicht gefunden: $SOURCE_DIR"
    echo "Bitte pruefen Sie den Benutzernamen."
    exit 1
fi

echo "=== SYNC-BACK: Produktion -> source-Repo ==="
echo "Datum: $(date '+%d.%m.%Y %H:%M:%S')"

cp "$PROD_DIR/index.html"        "$SOURCE_DIR/index.html"
cp "$PROD_DIR/manifest"          "$SOURCE_DIR/manifest"
cp "$PROD_DIR/files-directorys"  "$SOURCE_DIR/files-directorys"
cp "$PROD_DIR/language.xml"      "$SOURCE_DIR/language.xml"
cp "$PROD_DIR/cgi-bin/"*.py      "$SOURCE_DIR/cgi-bin/"

chown "$1":"$1" "$SOURCE_DIR/index.html"
chown "$1":"$1" "$SOURCE_DIR/manifest"
chown "$1":"$1" "$SOURCE_DIR/files-directorys"
chown "$1":"$1" "$SOURCE_DIR/language.xml"
chown "$1":"$1" "$SOURCE_DIR/cgi-bin/"*.py
chmod 755 "$SOURCE_DIR/cgi-bin/"*.py

echo "=== Sync-Back abgeschlossen ==="
echo "Bitte danach manuell: git add, git commit, git push"

