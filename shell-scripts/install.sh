#!/bin/bash
# install.sh - Kopiert die shell-scripts source-Repo in die Produktion
# Verwendung: sudo /var/www/deepseek-chat/install.sh

# Root-Pruefung
if [ "$(id -u)" -ne 0 ]; then
    echo "FEHLER: Dieses Script muss als root ausgefuehrt werden!"
    echo "Verwendung: sudo /var/www/deepseek-chat/instal.sh"
    exit 1
fi

PROD_DIR="/var/www/deepseek-chat"

echo "Datum: $(date '+%d.%m.%Y %H:%M:%S')"

cp deploy.sh    "$PROD_DIR/deploy.sh"
cp sync-back.sh "$PROD_DIR/sync-back.sh"

chown www-data:www-data "$PROD_DIR/deploy.sh"
chown www-data:www-data "$PROD_DIR/sync-back.sh"

echo "shell-scripts installed"

