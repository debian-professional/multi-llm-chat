#!/bin/bash

# === Konfiguration ===
OUTPUT_FILE_PREFIX="repo_export"

# === Funktion: Zeige Hilfe an ===
show_help() {
    echo "Verwendung: $0 [OPTIONEN] [GitHub-Repository-URL]"
    echo ""
    echo "Beschreibung:"
    echo "  Klont ein GitHub-Repository, extrahiert den Text aller Textdateien"
    echo "  und schreibt sie mit deutlichen Trennern in eine Ausgabedatei."
    echo "  Unterstützte Formate: txt (Standard), json, md (Markdown)."
    echo "  Anschließend wird zusätzlich ein ZIP-Archiv dieser Datei erstellt."
    echo "  Das Repository wird nach der Extraktion automatisch gelöscht."
    echo ""
    echo "Optionen:"
    echo "  -f, --format FORMAT   Ausgabeformat: txt, json, md (oder markdown)"
    echo "  -h, --help            Diese Hilfe anzeigen"
    echo ""
    echo "Argumente:"
    echo "  [GitHub-Repository-URL]  Optional: Die HTTPS- oder SSH-URL des Repos."
    echo "                            Wenn keine URL angegeben wird, erfolgt eine interaktive Eingabe."
    echo "                            Wird das Skript innerhalb eines Git-Repos ausgeführt,"
    echo "                            wird automatisch die Remote-URL als Vorschlag verwendet."
    echo ""
    echo "Beispiele:"
    echo "  $0 https://github.com/kubernetes/kubernetes.git"
    echo "  $0 -f json https://github.com/kubernetes/kubernetes.git"
    echo "  $0 --format md   # dann URL eingeben (oder Vorschlag aus Git-Remote)"
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

# ============================================
# Ausgabefunktionen für die verschiedenen Formate
# ============================================

# --- Text (Standard) ---
write_txt_header() {
    local outfile="$1"
    local count="$2"
    cat > "$outfile" <<EOF
=========================================================================
Repository Export
=========================================================================
Export-Datum: $(date '+%Y-%m-%d %H:%M:%S')
Repository-URL: $REPO_URL
Commit-Hash: $COMMIT_HASH
Branch: $BRANCH_NAME
Anzahl extrahierter Textdateien: $count
=========================================================================

EOF
}

write_txt_file() {
    local outfile="$1"
    local file="$2"
    local full_path="$3"
    {
        echo "========================================================================="
        echo "Datei: $file"
        echo "========================================================================="
        cat "$full_path"
        echo
        echo
    } >> "$outfile"
}

# --- Markdown ---
write_md_header() {
    local outfile="$1"
    local count="$2"
    {
        echo "# Repository Export"
        echo
        echo "**Export-Datum:** $(date '+%Y-%m-%d %H:%M:%S')"
        echo
        echo "**Repository-URL:** $REPO_URL"
        echo
        echo "**Commit-Hash:** $COMMIT_HASH"
        echo
        echo "**Branch:** $BRANCH_NAME"
        echo
        echo "**Anzahl extrahierter Textdateien:** $count"
        echo
        echo "---"
        echo
    } >> "$outfile"
}

write_md_file() {
    local outfile="$1"
    local file="$2"
    local full_path="$3"

    # Sprache für Code-Block aus Endung ermitteln
    local lang=""
    case "$file" in
        *.sh) lang="bash" ;;
        *.py) lang="python" ;;
        *.js) lang="javascript" ;;
        *.json) lang="json" ;;
        *.md) lang="markdown" ;;
        *.c) lang="c" ;;
        *.cpp) lang="cpp" ;;
        *.java) lang="java" ;;
        *.go) lang="go" ;;
        *.rs) lang="rust" ;;
        *.php) lang="php" ;;
        *.rb) lang="ruby" ;;
        *.pl) lang="perl" ;;
        *.sql) lang="sql" ;;
        *.xml) lang="xml" ;;
        *.yaml|*.yml) lang="yaml" ;;
        *.html) lang="html" ;;
        *.css) lang="css" ;;
        *) lang="" ;;
    esac

    {
        echo "## Datei: \`$file\`"
        echo
        echo "\`\`\`$lang"
        cat "$full_path"
        echo "\`\`\`"
        echo
    } >> "$outfile"
}

# --- JSON ---
write_json_final() {
    local objects_file="$1"
    local final_file="$2"
    local count="$3"

    # Metadaten als separates Objekt, dann die Dateiliste als Array
    jq -n \
        --arg date "$(date '+%Y-%m-%d %H:%M:%S')" \
        --arg url "$REPO_URL" \
        --arg commit "$COMMIT_HASH" \
        --arg branch "$BRANCH_NAME" \
        --argjson count "$count" \
        --slurpfile files "$objects_file" \
        '{metadata: {date: $date, url: $url, commit: $commit, branch: $branch, file_count: $count}, files: $files}' > "$final_file"
}

# ============================================
# Hauptprogramm
# ============================================

# --- Abhängigkeiten prüfen ---
if ! command -v git &> /dev/null; then
    echo "Fehler: 'git' ist nicht installiert. Bitte installiere es."
    exit 1
fi
if ! command -v file &> /dev/null; then
    echo "Fehler: 'file' ist nicht installiert. Bitte installiere es."
    exit 1
fi

# --- Argumente parsen ---
OUTPUT_FORMAT="txt"
REPO_URL=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            # Erstes nicht-Option-Argument wird als URL interpretiert
            if [[ -z "$REPO_URL" ]]; then
                REPO_URL="$1"
            else
                echo "Unbekanntes Argument: $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Format normalisieren
if [[ "$OUTPUT_FORMAT" == "markdown" ]]; then
    OUTPUT_FORMAT="md"
fi
if [[ ! "$OUTPUT_FORMAT" =~ ^(txt|json|md)$ ]]; then
    echo "Fehler: Unbekanntes Format '$OUTPUT_FORMAT'. Erlaubt: txt, json, md (oder markdown)"
    exit 1
fi

# Für JSON muss jq installiert sein
if [[ "$OUTPUT_FORMAT" == "json" ]] && ! command -v jq &> /dev/null; then
    echo "Fehler: Für JSON-Ausgabe wird 'jq' benötigt. Bitte installiere es."
    exit 1
fi

# Startverzeichnis merken
START_DIR="$(pwd)"

# --- URL bestimmen ---
if [ -z "$REPO_URL" ]; then
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

# Sauberkeitsprüfung (nur wenn das aktuelle Repo verwendet wird? Wir führen sie immer durch,
# aber die Warnung bezieht sich auf das aktuelle Repo, nicht auf das zu klonende.
# Das ist akzeptabel, da der Benutzer gewarnt wird, falls sein aktuelles Repo unsauber ist.
check_git_cleanliness

# SSH-URL? Benutzer fragen, ob er SSH verwenden will
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

# Zurück zum Startverzeichnis für die Ausgabedatei
cd "$START_DIR"

TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')
OUTPUT_FILE="${OUTPUT_FILE_PREFIX}_${REPO_NAME}_${TIMESTAMP}.${OUTPUT_FORMAT}"
file_count=0

# Je nach Format temporäre Dateien anlegen
case "$OUTPUT_FORMAT" in
    txt|md)
        CONTENT_FILE="${OUTPUT_FILE}.content"
        > "$CONTENT_FILE"
        ;;
    json)
        OBJECTS_FILE="${OUTPUT_FILE}.objects"
        > "$OBJECTS_FILE"
        ;;
esac

# Wieder ins temporäre Repo wechseln für die Dateiextraktion
cd "$TEMP_DIR"

while IFS= read -r -d '' file; do
    full_path="$TEMP_DIR/$file"

    if is_text_file "$full_path"; then
        case "$OUTPUT_FORMAT" in
            txt)
                write_txt_file "$START_DIR/$CONTENT_FILE" "$file" "$full_path"
                ;;
            md)
                write_md_file "$START_DIR/$CONTENT_FILE" "$file" "$full_path"
                ;;
            json)
                # Ein JSON-Objekt pro Zeile in die Objects-Datei schreiben
                jq -n \
                    --arg path "$file" \
                    --arg content "$(cat "$full_path")" \
                    '{path: $path, content: $content}' >> "$START_DIR/$OBJECTS_FILE"
                ;;
        esac
        ((file_count++))
        echo "  + Hinzugefügt: $file"
    else
        echo "  - Überspringe (keine reine Textdatei): $file"
    fi
done < <(git ls-files -z)

echo "=== Extraktion abgeschlossen. Erstelle Export-Datei... ==="

cd "$START_DIR"

case "$OUTPUT_FORMAT" in
    txt)
        {
            write_txt_header /dev/stdout "$file_count"
            cat "$CONTENT_FILE"
        } > "$OUTPUT_FILE"
        rm -f "$CONTENT_FILE"
        ;;
    md)
        {
            write_md_header /dev/stdout "$file_count"
            cat "$CONTENT_FILE"
        } > "$OUTPUT_FILE"
        rm -f "$CONTENT_FILE"
        ;;
    json)
        write_json_final "$OBJECTS_FILE" "$OUTPUT_FILE" "$file_count"
        rm -f "$OBJECTS_FILE"
        ;;
esac

# === ZIP-Archiv erstellen ===
if command -v zip &> /dev/null; then
    echo "=== Erstelle ZIP-Archiv ==="
    zip -j "$OUTPUT_FILE.zip" "$OUTPUT_FILE"
    echo "ZIP-Archiv erstellt: $OUTPUT_FILE.zip"
else
    echo "WARNUNG: 'zip' nicht gefunden. Überspringe ZIP-Erstellung."
fi

echo "=== Aufräumen: Lösche temporäres Repository ==="
rm -rf -- "$TEMP_DIR"

echo "==============================================="
echo "Fertig! Es wurden $file_count Textdateien extrahiert."
echo "Die Ausgabedatei wurde erstellt: $START_DIR/$OUTPUT_FILE"
if [ -f "$OUTPUT_FILE.zip" ]; then
    echo "ZIP-Archiv erstellt:        $START_DIR/$OUTPUT_FILE.zip"
fi
echo "==============================================="

