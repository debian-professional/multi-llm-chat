#!/bin/bash

# === Konfiguration ===
OUTPUT_FILE_PREFIX="repo_export"

# Liste der Dateiendungen, die ignoriert werden sollen (Regex-Format)
# Hier kannst du einfach weitere hinzufügen, z.B. |lock|tmp|bak
EXCLUDE_EXTENSIONS="lock|log|tmp|bak|swp|cache"

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
    echo "  --flat                Nur Dateinamen ohne Pfad verwenden (flat)"
    echo "  -h, --help            Diese Hilfe anzeigen"
    echo ""
    echo "Argumente:"
    echo "  [GitHub-Repository-URL]  Optional: Die HTTPS- oder SSH-URL des Repos."
    echo "                            Wenn keine URL angegeben wird, erfolgt eine interaktive Eingabe."
    echo "                            Wird das Skript innerhalb eines Git-Repos ausgeführt,"
    echo "                            wird automatisch die Remote-URL als Vorschlag verwendet."
}

# === Funktion: Lese Remote-URL des aktuellen Git-Repos ===
get_git_remote_url() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo ""
    fi
    local remote=$(git remote | head -n1)
    [ -z "$remote" ] && echo "" && return
    echo "$(git config --get "remote.$remote.url")"
}

# === Funktion: Prüfe Git-Status ===
check_git_cleanliness() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then return 0; fi
    local dirty=0
    local unpushed=0
    local branch=$(git symbolic-ref --short HEAD 2>/dev/null)
    if ! git diff --quiet || ! git diff --cached --quiet; then dirty=1; fi
    if [ -n "$branch" ]; then
        local remote=$(git config "branch.$branch.remote" 2>/dev/null)
        local merge=$(git config "branch.$branch.merge" 2>/dev/null)
        if [ -n "$remote" ] && [ -n "$merge" ]; then
            local upstream="${remote}/${merge#refs/heads/}"
            unpushed=$(git rev-list --count "$upstream..$branch" 2>/dev/null || echo 0)
        fi
    fi
    if [ $dirty -eq 1 ] || [ "$unpushed" -gt 0 ]; then
        echo -e "\nWARNUNG: Das aktuelle Git-Repository ist nicht sauber."
        read -p "Trotzdem fortfahren? (j/N): " confirm
        [[ ! "$confirm" =~ ^[jJ]$ ]] && echo "Abbruch." && exit 1
    fi
}

# === Funktion: SSH zu HTTPS ===
convert_ssh_to_https() {
    local url="$1"
    if [[ "$url" =~ ^git@([^:]+):(.+)$ ]]; then
        echo "https://${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    else
        echo "$url"
    fi
}

# === Funktion: Textdatei-Prüfung ===
is_text_file() {
    local file="$1"
    # 1. MIME-Check
    if ! file -b --mime-type "$file" | grep -q "^text/"; then return 1; fi
    # 2. Ausschluss über Endungen (Regex gegen Dateiname)
    if [[ "$file" =~ \.($EXCLUDE_EXTENSIONS)$ ]]; then return 1; fi
    # 3. Binär-Check
    if ! grep -Iq . "$file" 2>/dev/null; then return 1; fi
    return 0
}

# ============================================
# Ausgabefunktionen
# ============================================

write_txt_header() {
    cat > "$1" <<EOF
=========================================================================
Repository Export | Dateien: $2
Datum: $(date '+%Y-%m-%d %H:%M:%S') | URL: $REPO_URL
=========================================================================

EOF
}

write_txt_file() {
    { echo "FILE: $2"; echo "---------------------------------------------------------"; cat "$3"; echo -e "\n\n"; } >> "$1"
}

write_md_header() {
    { echo "# Repo Export"; echo -e "\n- **URL:** $REPO_URL\n- **Dateien:** $2\n\n---\n"; } >> "$1"
}

write_md_file() {
    local lang="${2##*.}"
    { echo "## \`$2\`"; echo -e "\n\`\`\`$lang"; cat "$3"; echo -e "\n\`\`\`\n"; } >> "$1"
}

write_json_final() {
    jq -n --arg date "$(date)" --arg url "$REPO_URL" --argjson count "$3" --slurpfile files "$1" \
    '{metadata: {date: $date, url: $url, file_count: $count}, files: $files}' > "$2"
}

# ============================================
# Hauptprogramm
# ============================================

# Abhängigkeiten
MISSING_PKGS=()
for pkg in git file zip jq pv; do
    command -v "$pkg" &>/dev/null || MISSING_PKGS+=("$pkg")
done
if [ ${#MISSING_PKGS[@]} -ne 0 ]; then
    echo "Fehler: Pakete fehlen: ${MISSING_PKGS[*]}"; exit 1
fi

OUTPUT_FORMAT="txt"
REPO_URL=""
flat=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--format) OUTPUT_FORMAT="$2"; shift 2 ;;
        --flat) flat=true; shift ;;
        -h|--help) show_help; exit 0 ;;
        *) REPO_URL="$1"; shift ;;
    esac
done

[[ ! "$OUTPUT_FORMAT" =~ ^(txt|json|md)$ ]] && echo "Format-Fehler" && exit 1

if [[ -z "$REPO_URL" ]]; then
    check_git_cleanliness
    DEFAULT_URL=$(get_git_remote_url)
    read -p "Repository-URL [${DEFAULT_URL}]: " input_url
    REPO_URL=${input_url:-$DEFAULT_URL}
fi

[ -z "$REPO_URL" ] && exit 1

REPO_URL=$(convert_ssh_to_https "$REPO_URL")
REPO_NAME=$(basename "$REPO_URL" .git)
TEMP_DIR="temp_repo_$(date +%s)"

echo "Klone $REPO_URL ..."
git clone --depth 1 "$REPO_URL" "$TEMP_DIR" &>/dev/null || exit 1

cd "$TEMP_DIR" && COMMIT_HASH=$(git rev-parse HEAD) && BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD) && cd ..

OUTPUT_FILE="${OUTPUT_FILE_PREFIX}_${REPO_NAME}_$(date +%Y%m%d_%H%M%S).${OUTPUT_FORMAT}"
echo 0 > .count.tmp

echo "Analysiere..."
total_files=$(find "$TEMP_DIR" -type f -not -path '*/.*' | wc -l)

echo "Extrahiere..."
find "$TEMP_DIR" -type f -not -path '*/.*' -print0 | pv -0 -p -t -e -r -s "$total_files" -l | while IFS= read -r -d '' full_path; do
    rel_path="${full_path#$TEMP_DIR/}"

    display_path="$rel_path"
    if $flat; then
        display_path=$(basename "$rel_path")
    fi

    if is_text_file "$full_path"; then
        case "$OUTPUT_FORMAT" in
            txt) write_txt_file "$OUTPUT_FILE" "$display_path" "$full_path" ;;
            md)  write_md_file  "$OUTPUT_FILE" "$display_path" "$full_path" ;;
            json) jq -n --arg p "$display_path" --arg c "$(cat "$full_path")" '{path: $p, content: $c}' >> "json.tmp" ;;
        esac
        echo $(($(cat .count.tmp) + 1)) > .count.tmp
    fi
done

file_count=$(cat .count.tmp)
rm .count.tmp

if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    write_json_final "json.tmp" "$OUTPUT_FILE" "$file_count" && rm "json.tmp"
else
    TEMP_H="h.tmp"
    [[ "$OUTPUT_FORMAT" == "txt" ]] && write_txt_header "$TEMP_H" "$file_count" || write_md_header "$TEMP_H" "$file_count"
    cat "$OUTPUT_FILE" >> "$TEMP_H" && mv "$TEMP_H" "$OUTPUT_FILE"
fi

zip -q "${OUTPUT_FILE}.zip" "$OUTPUT_FILE"
rm -rf "$TEMP_DIR"

echo "==============================================="
echo "Fertig! $file_count Dateien extrahiert."
echo "Output: $(pwd)/$OUTPUT_FILE"
echo "==============================================="

