#!/bin/bash
# tag-release.sh - Erstellt einen neuen Git-Tag mit aufsteigender Versionsnummer
# Verwendung: ./tag-release.sh

# Repo-Verzeichnis ermitteln (parent von shell-scripts/)
REPO_DIR="$(dirname "$(pwd)")"

# Git-Verzeichnis-Pruefung
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "FEHLER: Kein Git-Repository gefunden in: $REPO_DIR"
    echo "Bitte pruefen Sie die Verzeichnisstruktur."
    exit 1
fi

cd "$REPO_DIR"

git fetch --tags

# Letzten Tag ermitteln (nur Tags der Form v0.NN oder v0.NNx, x = Kleinbuchstabe)
LAST_TAG=$(git tag | grep -E '^v0\.[0-9]+[a-z]?$' | sort -V | tail -n 1)

if [ -z "$LAST_TAG" ]; then
    echo "Kein bisheriger Tag gefunden. Erster Tag wird erstellt."
    SUGGESTED="v0.80"
else
    echo "Letzter Tag: $LAST_TAG"
    # Naechste Version berechnen:
    #   v0.97  -> v0.98   (Zahl +1)
    #   v0.97a -> v0.97b  (Buchstabe +1)
    LAST_NUM=$(echo "$LAST_TAG" | sed -E 's/^v0\.([0-9]+)[a-z]?$/\1/')
    LAST_SUFFIX=$(echo "$LAST_TAG" | sed -E 's/^v0\.[0-9]+([a-z]?)$/\1/')
    if [ -z "$LAST_SUFFIX" ]; then
        SUGGESTED="v0.$((10#$LAST_NUM + 1))"
    elif [ "$LAST_SUFFIX" = "z" ]; then
        # Nach z geht es mit der naechsten Zahl weiter
        SUGGESTED="v0.$((10#$LAST_NUM + 1))"
    else
        NEXT_SUFFIX=$(echo "$LAST_SUFFIX" | tr 'a-y' 'b-z')
        SUGGESTED="v0.${LAST_NUM}${NEXT_SUFFIX}"
    fi
fi

echo "Vorgeschlagene Version: $SUGGESTED"
echo ""
read -p "Versionsnummer eingeben (Enter fuer $SUGGESTED): " USER_INPUT

# Wenn nichts eingegeben, Vorschlag verwenden
if [ -z "$USER_INPUT" ]; then
    VERSION="$SUGGESTED"
else
    VERSION="$USER_INPUT"
fi

# v vorne anfuegen falls nicht vorhanden
if [[ "$VERSION" != v* ]]; then
    VERSION="v$VERSION"
fi

echo ""
echo "=== TAG-RELEASE ==="
echo "Datum:   $(date '+%d.%m.%Y %H:%M:%S')"
echo "Version: $VERSION"
echo ""
read -p "Bestaetigen? (j/n): " CONFIRM

if [ "$CONFIRM" != "j" ]; then
    echo "Abgebrochen."
    exit 0
fi

git tag -a "$VERSION" -m "Version $VERSION - stable release"
if [ $? -ne 0 ]; then
    echo "FEHLER: Git-Tag konnte nicht erstellt werden!"
    exit 1
fi
echo "Tag erstellt: OK"

git push origin "$VERSION"
if [ $? -ne 0 ]; then
    echo "FEHLER: Git push fehlgeschlagen!"
    exit 1
fi
echo "Tag gepusht:  OK"

echo ""
echo "=== Tag-Release abgeschlossen ==="
