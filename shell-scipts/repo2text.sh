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

# === Funktion: Lese Remote-URL des aktuellen Git-Repos (falls vorhanden) ===
get_git_remote_url() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo ""
        return
    fi

    local remote=$(git remote | head -n1)
    if [ -z "$remote" ]; then
        echo ""
        return
    fi

    local url=$(git config --get "remote.$remote.url")
    echo "$url"
}

# === Funktion: Prüfe, ob das aktuelle Git-Repo "sauber" ist ===
check_git_cleanliness() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        return 0
    fi

    local dirty=0
    local unpushed=0
    local branch=$(git symbolic-ref --short HEAD 2>/dev/null)

    if ! git diff --quiet || ! git diff --cached --quiet; then
        dirty=1
    fi

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

# === Funktion: SSH-URL in HTTPS-URL umwandeln ===
convert_ssh_to_https() {
    local url="$1"
    if [[ "$url" =~ ^git@([^:]+):(.+)$ ]]; then
        local host="${BASH_REMATCH[1]}"
        local path="${BASH_REMATCH[2]}"
        echo "https://${host}/${path}"
    else
        echo "$url"
    fi
}

# === Funktion: Prüft, ob eine Datei eine reine Textdatei ist ===
is_text_file() {
    local file="$1"

    # 1. MIME-Typ muss mit text/ beginnen
    if ! file -b --mime-type "$file" | grep -q "^text/"; then
        return 1
    fi

    # 2. Datei darf keine Binärzeichen enthalten
    if ! grep -Iq . "$file" 2>/dev/null; then
        return 1
    fi

    return 0
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

if [ $# -ge 1 ]; then
    REPO_URL="$1"
else
    git_remote_url=$(get_git_remote_url)
    if [ -n "$git_remote_url" ]; then
        echo "Gefundene Remote-URL des aktuellen Git-Repos: $git_remote_url"
        read -p "Diese URL verwenden? (j/n): " use_remote
        if [[ "$use_remote" =~ ^[jJ]$ ]]; then
            REPO_URL="$git_remote_url"
        fi
    fi

    if [ -z "$REPO_URL" ]; then
        read -p "Bitte gib die GitHub-Repository-URL ein: " REPO_URL
        if [ -z "$REPO_URL" ]; then
            echo "Fehler: Keine URL eingegeben."
            show_help
            exit 1
        fi
    fi
fi

check_git_cleanliness

if [[ "$REPO_URL" == git@* ]]; then
    echo "Die URL ist eine SSH-URL: $REPO_URL"
    echo "SSH-Zugriff erfordert einen hinterlegten SSH-Key."
    read -p "Möchten Sie SSH verwenden? (j/n): " use_ssh
    if [[ ! "$use_ssh" =~ ^[jJ]$ ]]; then
        REPO_URL=$(convert_ssh_to_https "$REPO_URL")
        echo "Verwende stattdessen HTTPS: $REPO_URL"
    fi
fi

REPO_NAME=$(basename "$REPO_URL" .git)

TEMP_DIR=$(mktemp -d -t "${REPO_NAME}-XXXXX")
if [ ! -d "$TEMP_DIR" ]; then
    echo "Fehler: Konnte kein temporäres Verzeichnis erstellen."
    exit 1
fi

echo "=== Klone Repository '$REPO_URL' nach '$TEMP_DIR' ==="

if ! git clone --depth 1 "$REPO_URL" "$TEMP_DIR"; then
    echo "Fehler beim Klonen des Repositories. Löschen des Temp-Verzeichnisses."
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "=== Klonen erfolgreich. Extrahiere Textdateien... ==="

# Metadaten aus dem geklonten Repo auslesen
cd "$TEMP_DIR"
COMMIT_HASH=$(git rev-parse HEAD)
BRANCH_NAME=$(git symbolic-ref --short HEAD 2>/dev/null || echo "detached")

TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')
OUTPUT_FILE="$(pwd -P)/${OUTPUT_FILE_PREFIX}_${REPO_NAME}_${TIMESTAMP}.txt"
CONTENT_FILE="${OUTPUT_FILE}.content"
> "$CONTENT_FILE"

file_count=0

while IFS= read -r -d '' file; do
    full_path="$TEMP_DIR/$file"

    if is_text_file "$full_path"; then
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
        echo "  - Überspringe (keine reine Textdatei): $file"
    fi
done < <(git ls-files -z)

echo "=== Extraktion abgeschlossen. Erstelle Export-Datei... ==="

cd - > /dev/null

# Header mit Metadaten erstellen und mit Inhalt kombinieren
{
    echo "========================================================================="
    echo "Repository Export"
    echo "========================================================================="
    echo "Export-Datum: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Repository-URL: $REPO_URL"
    echo "Commit-Hash: $COMMIT_HASH"
    echo "Branch: $BRANCH_NAME"
    echo "Anzahl extrahierter Textdateien: $file_count"
    echo "========================================================================="
    echo
    cat "$CONTENT_FILE"
} > "$OUTPUT_FILE"

rm -f "$CONTENT_FILE"

echo "=== Aufräumen: Lösche temporäres Repository ==="
rm -rf "$TEMP_DIR"

echo "==============================================="
echo "Fertig! Es wurden $file_count Textdateien extrahiert."
echo "Die Ausgabedatei wurde erstellt: $(pwd)/$(basename "$OUTPUT_FILE")"
echo "==============================================="

