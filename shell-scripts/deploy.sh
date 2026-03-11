#!/bin/bash
# deploy.sh - Kopiert Dateien vom source-Repo in die Produktion
# Verwendung: sudo /var/www/deepseek-chat/deploy.sh <username>

# Root-Pruefung
if [ "$(id -u)" -ne 0 ]; then
    echo "FEHLER: Dieses Script muss als root ausgefuehrt werden!"
    echo "Verwendung: sudo /var/www/deepseek-chat/deploy.sh <username>"
    exit 1
fi

# Parameter-Pruefung
if [ -z "$1" ]; then
    echo "FEHLER: Kein Benutzername angegeben!"
    echo "Verwendung: sudo /var/www/deepseek-chat/deploy.sh <username>"
    exit 1
fi

SOURCE_DIR="/home/$1/private-chatboot/"
PROD_DIR="/var/www/deepseek-chat"

# Git-Verzeichnis-Pruefung
if [ ! -d "$SOURCE_DIR/.git" ]; then
    echo "FEHLER: Kein Git-Repository gefunden in: $SOURCE_DIR/.git"
    echo "Bitte pruefen Sie den Benutzernamen und das Repository."
    exit 1
fi

echo "=== DEPLOY: source-Repo -> Produktion ==="
echo "Datum: $(date '+%d.%m.%Y %H:%M:%S')"

cp "$SOURCE_DIR/var/www/deepseek-chat/index.html"        "$PROD_DIR/index.html"
cp "$SOURCE_DIR/var/www/deepseek-chat/manifest"          "$PROD_DIR/manifest"
cp "$SOURCE_DIR/var/www/deepseek-chat/files-directorys"  "$PROD_DIR/files-directorys"
cp "$SOURCE_DIR/var/www/deepseek-chat/cgi-bin/"*.py      "$PROD_DIR/cgi-bin/"
cp "$SOURCE_DIR/var/www/deepseek-chat/language.xml"      "$PROD_DIR/language.xml"

chown www-data:www-data "$PROD_DIR/index.html"
chown www-data:www-data "$PROD_DIR/manifest"
chown www-data:www-data "$PROD_DIR/files-directorys"
chown www-data:www-data "$PROD_DIR/cgi-bin/"*.py
chown www-data:www-data "$PROD_DIR/language.xml"
chmod 755 "$PROD_DIR/cgi-bin/"*.py

systemctl reload apache2 > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "FEHLER: Apache reload fehlgeschlagen! (RC: $?)"
    echo "Bitte pruefen Sie: systemctl status apache2"
    exit 1
fi
echo "Apache reload: OK"

systemctl status apache2 > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "WARNUNG: Apache laeuft moeglicherweise nicht korrekt! (RC: $?)"
    echo "Bitte pruefen Sie: systemctl status apache2"
    exit 1
fi
echo "Apache status: OK"

echo "=== Deploy abgeschlossen ==="

