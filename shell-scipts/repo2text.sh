#!/bin/bash

# === Konfiguration ===
OUTPUT_FILE_PREFIX="repo_export"

# === Funktion: Zeige Hilfe an ===
show_help() {
    echo "Verwendung: $0 [GitHub-Repository-URL]"
    echo ""
    echo "Beschreibung:"
    echo "  Klont ein GitHub-Repository, extrahiert den Text aller Textdateien"
    echo "  und schreibt sie mit deutlichen Trennern in eine einzige Textdatei."
    echo "  Das Repository wird nach der Extraktion automatisch gelöscht."
    echo ""
    echo "Argumente:"
    echo "  [GitHub-Repository-URL]  Optional: Die HTTPS- oder SSH-URL des Repos."
    echo "                            Wenn keine URL angegeben wird, erfolgt eine interaktive Eingabe."
    echo ""
    echo "Beispiele:"
    echo "  $0 https://github.com/kubernetes/kubernetes.git"
    echo "  $0   # dann URL eingeben"
}

# === Funktion: Prüfe, ob das Skript in einem sauberen Git-Repo gestartet wurde ===
check_git_clean() {
    # Prüfen, ob wir in einem Git-Repo sind
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "Hinweis: Das Skript wird nicht innerhalb eines Git-Repos ausgeführt – überspringe Sauberkeitsprüfung."
        return
    fi

    # Prüfen auf uncommittete Änderungen (working directory + staged)
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "FEHLER: Es gibt uncommittete Änderungen im Repository."
        echo "Bitte committen Sie alle Änderungen oder machen Sie sie rückgängig."
        exit 1
    fi

    # Prüfen auf nicht gepushte Commits
    local branch=$(git symbolic-ref --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        local remote=$(git config "branch.$branch.remote" 2>/dev/null)
        local merge=$(git config "branch.$branch.merge" 2>/dev/null)
        if [ -n "$remote" ] && [ -n "$merge" ]; then
            local upstream="${remote}/${merge#refs/heads/}"
            local unpushed=$(git rev-list --count "$upstream..$branch" 2>/dev/null)
            if [ "$unpushed" -gt 0 ]; then
                echo "FEHLER: Es gibt $unpushed nicht gepushte Commits auf dem Branch '$branch'."
                echo "Bitte führen Sie 'git push' aus, bevor Sie fortfahren."
                exit 1
            fi
        else
            echo "WARNUNG: Branch '$branch' hat keinen Upstream. Kann nicht auf gepushte Commits prüfen."
            # Hier brechen wir nicht ab, nur Warnung.
        fi
    fi
}

# === Hauptprogramm ===

# Prüfen, ob eine URL als Argument übergeben wurde
if [ $# -ge 1 ]; then
    REPO_URL="$1"
else
    # Interaktiv nach der URL fragen
    read -p "Bitte gib die GitHub-Repository-URL ein: " REPO_URL
    if [ -z "$REPO_URL" ]; then
        echo "Fehler: Keine URL eingegeben."
        show_help
        exit 1
    fi
fi

# Prüfen, ob git installiert ist
if ! command -v git &> /dev/null; then
    echo "Fehler: 'git' ist nicht installiert. Bitte installiere es mit:"
    echo "  sudo apt update && sudo apt install git -y"
    exit 1
fi

# Repository-Namen aus der URL extrahieren
REPO_NAME=$(basename "$REPO_URL" .git)

# Prüfen, ob das aktuelle Verzeichnis ein sauberes Git-Repo ist (optional)
check_git_clean

# Temporäres Verzeichnis zum Klonen erstellen
TEMP_DIR=$(mktemp -d -t "${REPO_NAME}-XXXXX")

if [ ! -d "$TEMP_DIR" ]; then
    echo "Fehler: Konnte kein temporäres Verzeichnis erstellen."
    exit 1
fi

echo "=== Klone Repository '$REPO_URL' nach '$TEMP_DIR' ==="

# Repository klonen (nur Standard-Branch, ohne Historie)
if ! git clone --depth 1 "$REPO_URL" "$TEMP_DIR"; then
    echo "Fehler beim Klonen des Repositories. Löschen des Temp-Verzeichnisses."
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "=== Klonen erfolgreich. Extrahiere Textdateien... ==="

# Zeitstempel für Dateinamen
TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')
OUTPUT_FILE="${OUTPUT_FILE_PREFIX}_${REPO_NAME}_${TIMESTAMP}.txt"

# Temporäre Datei für den Inhalt (ohne Header)
CONTENT_FILE="${OUTPUT_FILE}.content"
> "$CONTENT_FILE"

file_count=0

# Ins geklonte Repo wechseln und versionierte Dateien via git ls-files auflisten
cd "$TEMP_DIR"

while IFS= read -r -d '' file; do
    full_path="$TEMP_DIR/$file"

    # Prüfen, ob die Datei eine Textdatei ist
    mime_type=$(file -b --mime-type "$full_path")

    if [[ "$mime_type" == text/* ]]; then
        {
            echo "========================================================================="
            echo "Datei: $file"
            echo "========================================================================="
            cat "$full_path"
            echo
            echo
        } >> "$CONTENT_FILE"

        ((file_count++))
        echo "  + Hinzugefügt: $file"
    else
        echo "  - Überspringe (keine Textdatei): $file"
    fi
done < <(git ls-files -z)

echo "=== Aufräumen: Lösche temporäres Repository ==="
cd /tmp  # aus dem Verzeichnis wechseln, damit löschen funktioniert
rm -rf "$TEMP_DIR"

# Jetzt Header mit Metadaten erstellen und mit Inhalt kombinieren
{
    echo "========================================================================="
    echo "Repository Export"
    echo "========================================================================="
    echo "Export-Datum: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Repository-URL: $REPO_URL"
    echo "Anzahl extrahierter Textdateien: $file_count"
    echo "========================================================================="
    echo
    cat "$CONTENT_FILE"
} > "$OUTPUT_FILE"

# Temporäre Inhaltsdatei löschen
rm -f "$CONTENT_FILE"

echo "==============================================="
echo "Fertig! Es wurden $file_count Textdateien extrahiert."
echo "Die Ausgabedatei wurde erstellt: $(pwd)/$OUTPUT_FILE"
echo "==============================================="

