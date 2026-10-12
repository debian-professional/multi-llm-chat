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

SOURCE_DIR="/home/$1/multi-llm-chat/"
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

echo ""
echo "=== MD5-Summen der kopierten Dateien (Produktion) ==="
md5sum \
    "$PROD_DIR/index.html" \
    "$PROD_DIR/manifest" \
    "$PROD_DIR/files-directorys" \
    "$PROD_DIR/cgi-bin/"*.py \
    "$PROD_DIR/language.xml"
echo ""

# Dateien, die deploy.sh nicht kopiert: MD5 anzeigen und gegen das source-Repo vergleichen
# (deploy.sh/sync-back.sh kommen ueber install.sh, die Apache-Konfiguration manuell,
#  der changelog wird nicht deployt und steht nur im source-Repo)
echo "=== MD5-Summen weiterer Projektdateien ==="
pruefe_datei() {
    # $1 = Anzeigename, $2 = Quelle im source-Repo, $3 = Zieldatei in der Produktion (leer = nicht deployt)
    if [ ! -f "$2" ]; then
        echo "FEHLT im source-Repo:  $1"
        return
    fi
    SRC_SUM=$(md5sum "$2" | cut -d' ' -f1)
    if [ -z "$3" ]; then
        echo "$SRC_SUM  $1  (nur source-Repo, wird nicht deployt)"
    elif [ ! -f "$3" ]; then
        echo "$SRC_SUM  $1  (in der Produktion nicht vorhanden: $3)"
    else
        PROD_SUM=$(md5sum "$3" | cut -d' ' -f1)
        if [ "$SRC_SUM" = "$PROD_SUM" ]; then
            echo "$PROD_SUM  $3  (identisch mit source-Repo)"
        else
            echo "$PROD_SUM  $3  ABWEICHUNG: source-Repo hat $SRC_SUM -> install.sh bzw. manuell kopieren!"
        fi
    fi
}
pruefe_datei "changelog"            "$SOURCE_DIR/var/www/deepseek-chat/changelog"  ""
pruefe_datei "deploy.sh"            "$SOURCE_DIR/shell-scripts/deploy.sh"          "$PROD_DIR/deploy.sh"
pruefe_datei "sync-back.sh"         "$SOURCE_DIR/shell-scripts/sync-back.sh"       "$PROD_DIR/sync-back.sh"
pruefe_datei "deepseek-chat.conf"     "$SOURCE_DIR/etc/apache2/sites-available/deepseek-chat.conf"     "/etc/apache2/sites-available/deepseek-chat.conf"
pruefe_datei "deepseek-chat-ssl.conf" "$SOURCE_DIR/etc/apache2/sites-available/deepseek-chat-ssl.conf" "/etc/apache2/sites-available/deepseek-chat-ssl.conf"
echo ""

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
