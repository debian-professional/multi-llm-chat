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
    echo "  Das neu erzeugte Repository wird nach der Extraktion automatisch gelöscht."
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
    echo "  $0 https://github.com"
    echo "  $0 -f json https://github.com"
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
    if ! file -b --mime-type "$file" | grep -q "^text/"; then
        return 1
    fi
    if ! grep -Iq . "$file" 2>/dev/null; then
        return 1
    fi
    return 0
}

# ============================================
# Ausgabefunktionen
# ============================================

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

write_json_final() {
    local objects_file="$1"
    local final_file="$2"
    local count="$3"
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

# --- Erweiterte Abhängigkeitsprüfung am Anfang (inklusive pv) ---
MISSING_PKGS=()
for pkg in git file zip jq pv; do
    if ! command -v "$pkg" &> /dev/null; then
        MISSING_PKGS+=("$pkg")
    fi
done

if [ ${#MISSING_PKGS[@]} -ne 0 ]; then
    echo "Fehler: Folgende benötigte Programme fehlen: ${MISSING_PKGS[*]}"
    echo "Bitte installiere sie unter Debian mit:"
    echo "sudo apt update && sudo apt install ${MISSING_PKGS[*]} -y"
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
    echo "Fehler: Unbekanntes Format '$OUTPUT_FORMAT'. Erlaubt: txt, json, md"
    exit 1
fi

# URL ermitteln falls nicht übergeben
if [[ -z "$REPO_URL" ]]; then
    check_git_cleanliness
    DEFAULT_URL=$(get_git_remote_url)
    if [ -n "$DEFAULT_URL" ]; then
        read -p "GitHub-Repository-URL [$DEFAULT_URL]: " input_url
        REPO_URL=${input_url:-$DEFAULT_URL}
    else
        read -p "GitHub-Repository-URL: " REPO_URL
    fi
fi

if [[ -z "$REPO_URL" ]]; then
    echo "Fehler: Keine Repository-URL angegeben."
    exit 1
fi

REPO_URL=$(convert_ssh_to_https "$REPO_URL")
REPO_NAME=$(basename "$REPO_URL" .git)
TEMP_DIR="temp_repo_$(date +%s)"

echo "Klone Repository: $REPO_URL ..."
if ! git clone --depth 1 "$REPO_URL" "$TEMP_DIR" &> /dev/null; then
    echo "Fehler: Klonen fehlgeschlagen."
    exit 1
fi

cd "$TEMP_DIR" || exit 1
COMMIT_HASH=$(git rev-parse HEAD)
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
cd ..

OUTPUT_FILE="${OUTPUT_FILE_PREFIX}_${REPO_NAME}_$(date +%Y%m%d_%H%M%S).${OUTPUT_FORMAT}"
JSON_TEMP="json_files.tmp"
[ "$OUTPUT_FORMAT" == "json" ] && rm -f "$JSON_TEMP"

# --- Vorbereitung Profi-Fortschrittsanzeige ---
echo "Analysiere Repository..."
total_files=$(find "$TEMP_DIR" -type f -not -path '*/.*' | wc -l)
echo 0 > .count.tmp

echo "Extrahiere $total_files Dateien..."

# Die Schleife wird durch pv getaktet
find "$TEMP_DIR" -type f -not -path '*/.*' -print0 | pv -0 -p -t -e -r -s "$total_files" -l | while IFS= read -r -d '' full_path; do
    rel_path="${full_path#$TEMP_DIR/}"
    
    if is_text_file "$full_path"; then
        case "$OUTPUT_FORMAT" in
            txt)  write_txt_file "$OUTPUT_FILE" "$rel_path" "$full_path" ;;
            md)   write_md_file  "$OUTPUT_FILE" "$rel_path" "$full_path" ;;
            json)
                content=$(cat "$full_path")
                jq -n --arg path "$rel_path" --arg content "$content" '{path: $path, content: $content}' >> "$JSON_TEMP"
                ;;
        esac
        curr_c=$(cat .count.tmp)
        echo $((curr_c + 1)) > .count.tmp
    fi
done

file_count=$(cat .count.tmp)
rm .count.tmp

if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    write_json_final "$JSON_TEMP" "$OUTPUT_FILE" "$file_count"
    rm -f "$JSON_TEMP"
else
    TEMP_HEADER="header.tmp"
    if [[ "$OUTPUT_FORMAT" == "txt" ]]; then
        write_txt_header "$TEMP_HEADER" "$file_count"
    else
        write_md_header "$TEMP_HEADER" "$file_count"
    fi
    cat "$OUTPUT_FILE" >> "$TEMP_HEADER"
    mv "$TEMP_HEADER" "$OUTPUT_FILE"
fi

echo "Erstelle ZIP-Archiv..."
zip -q "${OUTPUT_FILE}.zip" "$OUTPUT_FILE"

echo "Aufräumen..."
rm -rf "$TEMP_DIR"

echo "==============================================="
echo "Fertig! Es wurden $file_count Textdateien extrahiert."
echo "Die Ausgabedatei wurde erstellt: $(pwd)/$OUTPUT_FILE"
if [ -f "$OUTPUT_FILE.zip" ]; then
    echo "ZIP-Archiv erstellt:        $(pwd)/$OUTPUT_FILE.zip"
fi
echo "==============================================="

