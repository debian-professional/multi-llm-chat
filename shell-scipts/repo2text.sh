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
    echo "                            Wird das Skript innerhalb eines Git-Repos ausgeführt,"
    echo "                            wird automatisch die Remote-URL als Vorschlag verwendet."
    echo ""
    echo "Beispiele:"
    echo "  $0 https://github.com/kubernetes/kubernetes.git"
    echo "  $0   # dann URL eingeben (oder Vorschlag aus Git-Remote)"
}

# === Funktion: Prüfe, ob das aktuelle Verzeichnis in einem Git-Repo liegt und gib die Remote-URL zurück ===
get_git_remote_url() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo ""
        return
    fi

    # Erstes Remote ermitteln (sortiert, z.B. origin)
    local remote=$(git remote | head -n1)
    if [ -z "$remote" ]; then
        echo ""
        return
    fi

    local url=$(git config --get "remote.$remote.url")
    echo "$url"
}

# === Funktion: Prüfe, ob das Skript in einem sauberen Git-Repo gestartet wurde (nur Warnung) ===
check_git_cleanliness() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        return 0  # kein Git-Repo, also immer "sauber"
    fi

    local dirty=0
    local unpushed=0
    local branch=$(git symbolic-ref --short HEAD 2>/dev/null)

    # Uncommittete Änderungen?
    if ! git diff --quiet || ! git diff --cached --quiet; then
        dirty=1
    fi

    # Nicht gepushte Commits?
    if [ -n "$branch" ]; then
        local remote=$(git config "branch.$branch.remote" 2>/dev/null)
        local merge=$(git config "branch.$branch.merge" 2>/dev/null)
        if [ -n "$remote" ] && [ -n "$merge" ]; then
            local upstream="${remote}/${merge#refs/heads/}"
            local count=$(git rev-list --count "$upstream..$branch" 2>/dev/null)
            if [ "$count" -gt 0 ]; then
                unpushed=$count
            fi
        fi
    fi

    if [ $dirty -eq 1 ] || [ $unpushed -gt 0 ]; then
        echo ""
        echo "WARNUNG: Das aktuelle Git-Repository ist nicht sauber:"
        [ $dirty -eq 1 ] && echo "  - Es gibt uncommittete Änderungen."
        [ $unpushed -gt 0 ] && echo "  - Es gibt $unpushed nicht gepushte Commits."
        echo ""
        read -p "Trotzdem fortfahren? (j/N): " confirm
        if [[ ! "$confirm" =~ ^[jJ]$ ]]; then
            echo "Abbruch."
            exit 1
        fi
    fi
}

# === Hauptprogramm ===

# Prüfen, ob git installiert ist
if ! command -v git &> /dev/null; then
    echo "Fehler: 'git' ist nicht installiert. Bitte installiere es mit:"
    echo "  sudo apt update && sudo apt install git -y"
    exit 1
fi

# --- URL bestimmen ---
REPO_URL=""

# 1. Fall: URL als Parameter übergeben
if [ $# -ge 1 ]; then
    REPO_URL="$1"
else
    # 2. Fall: Skript läuft in einem Git-Repo? Dann Remote auslesen
    git_remote_url=$(get_git_remote_url)
    if [ -n "$git_remote_url" ]; then
        echo "Gefundene Remote-URL des aktuellen Git-Repos: $git_remote_url"
        read -p "Diese URL verwenden? (j/n): " use_remote
        if [[ "$use_remote" =~ ^[jJ]$ ]]; then
            REPO_URL="$git_remote_url"
        fi
    fi

    # 3. Fall: immer noch keine URL -> interaktiv abfragen
    if [ -z "$REPO_URL" ]; then
        read -p "Bitte gib die GitHub-Repository-URL ein: " REPO_URL
        if [ -z "$REPO_URL" ]; then
            echo "Fehler: Keine URL eingegeben."
            show_help
            exit 1
        fi
    fi
fi

# Prüfung auf Sauberkeit des aktuellen Repos (falls wir in einem sind)
check_git_cleanliness

# Repository-Namen aus der URL extrahieren
REPO_NAME=$(basename "$REPO_URL" .git)

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

TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')
OUTPUT_FILE="${OUTPUT_FILE_PREFIX}_${REPO_NAME}_${TIMESTAMP}.txt"
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
cd /tmp
rm -rf "$TEMP_DIR"

# Header mit Metadaten erstellen
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

rm -f "$CONTENT_FILE"

echo "==============================================="
echo "Fertig! Es wurden $file_count Textdateien extrahiert."
echo "Die Ausgabedatei wurde erstellt: $(pwd)/$OUTPUT_FILE"
echo "==============================================="

