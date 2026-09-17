#!/usr/bin/python3
# -*- coding: utf-8 -*-

# =============================================================================
# BOOKMARK SPEICHERN
# Erstellt: 17.09.2026
# Feature: Bookmarks (gespeicherte, wiederverwendbare Prompts) - unabhaengig
# von Chat-Sessions. Uebernimmt bewusst 1:1 das bereits sicherheitsgehaertete
# Muster von save-session.py (gleiche ID-Regex-Form, gleicher
# Path-Traversal-Schutz via resolve_bookmark_path(), gleiche CORS-/
# Request-Groessenlimit-Absicherung), nur mit anderem Datenmodell
# (title + promptText statt chatData mit messages-Array).
# =============================================================================

import json
import sys
import os
import re
import datetime
from pathlib import Path

BOOKMARKS_DIR = '/var/www/deepseek-chat/bookmarks'

ALLOWED_ORIGIN = 'https://172.29.255.1'
MAX_REQUEST_SIZE = 1 * 1024 * 1024  # 1 MB (ein einzelner Prompt-Text, kein Chat-Verlauf)

# Gleiches Format wie Session-IDs (client-seitig ueber dieselbe
# generateSessionId()-Funktion erzeugt): YYYY-MM-DD_HHMMSS_xxxxxx
BOOKMARK_ID_RE = re.compile(r'^\d{4}-\d{2}-\d{2}_\d{6}_[A-Za-z0-9]{6}$')

# Kurzer Titel: Laenge begrenzen, um Missbrauch/UI-Sprengung zu verhindern
MAX_TITLE_LENGTH = 200
MAX_PROMPT_LENGTH = 500_000  # grosszuegig, aber nicht unbegrenzt

def create_bookmarks_dir():
    """Erstellt das Bookmarks-Verzeichnis falls nicht vorhanden."""
    if not os.path.exists(BOOKMARKS_DIR):
        os.makedirs(BOOKMARKS_DIR, mode=0o700)

def validate_bookmark_id(bookmark_id):
    """Validiert die Bookmark-ID strikt gegen das Format YYYY-MM-DD_HHMMSS_xxxxxx."""
    if not isinstance(bookmark_id, str) or not BOOKMARK_ID_RE.fullmatch(bookmark_id):
        return False
    try:
        datetime.datetime.strptime(bookmark_id[:10], '%Y-%m-%d')
        datetime.datetime.strptime(bookmark_id[11:17], '%H%M%S')
        return True
    except ValueError:
        return False

def resolve_bookmark_path(bookmark_id):
    """Loest den Bookmark-Dateipfad auf und stellt sicher, dass er innerhalb
    von BOOKMARKS_DIR bleibt (Verteidigung gegen Path Traversal)."""
    bookmarks_dir = Path(BOOKMARKS_DIR).resolve()
    bookmark_file = (bookmarks_dir / f'{bookmark_id}.json').resolve()
    if bookmark_file.parent != bookmarks_dir:
        raise ValueError('Ungültiger Bookmark-Pfad')
    return str(bookmark_file)

def send_response(status_code, data):
    """Sendet HTTP-Response zurück."""
    print(f"Status: {status_code}")
    print("Content-Type: application/json")
    print(f"Access-Control-Allow-Origin: {ALLOWED_ORIGIN}")
    print("Access-Control-Allow-Methods: POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()
    print(json.dumps(data, ensure_ascii=False))
    sys.stdout.flush()

def main():
    try:
        request_method = os.environ.get('REQUEST_METHOD', '')

        if request_method == 'OPTIONS':
            send_response(200, {'status': 'ok'})
            return

        if request_method != 'POST':
            send_response(405, {'error': f'Methode nicht erlaubt: {request_method}'})
            return

        create_bookmarks_dir()

        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        if content_length == 0:
            send_response(400, {'error': 'Leere Anfrage'})
            return

        if content_length > MAX_REQUEST_SIZE:
            send_response(413, {'error': f'Anfrage zu gross (max. {MAX_REQUEST_SIZE // (1024*1024)} MB)'})
            return

        # Rohe Bytes lesen und explizit als UTF-8 dekodieren (gleicher Fix
        # wie in den Session-Skripten - umgeht CGI-Locale-Probleme bei
        # Mehrbyte-UTF-8-Zeichen wie Emojis).
        post_data = sys.stdin.buffer.read(content_length).decode('utf-8')
        request_data = json.loads(post_data)

        bookmark_id = request_data.get('bookmarkId')
        if not validate_bookmark_id(bookmark_id):
            send_response(400, {'error': 'Ungültige Bookmark-ID'})
            return

        title = request_data.get('title')
        prompt_text = request_data.get('promptText')

        if not isinstance(title, str) or not title.strip():
            send_response(400, {'error': 'Kein Titel angegeben'})
            return
        if not isinstance(prompt_text, str) or not prompt_text.strip():
            send_response(400, {'error': 'Kein Prompt-Text angegeben'})
            return
        if len(title) > MAX_TITLE_LENGTH:
            send_response(400, {'error': f'Titel zu lang (max. {MAX_TITLE_LENGTH} Zeichen)'})
            return
        if len(prompt_text) > MAX_PROMPT_LENGTH:
            send_response(400, {'error': 'Prompt-Text zu lang'})
            return

        try:
            bookmark_file = resolve_bookmark_path(bookmark_id)
        except ValueError:
            send_response(400, {'error': 'Ungültige Bookmark-ID'})
            return

        bookmark_data = {
            'title': title,
            'promptText': prompt_text,
            'timestamp': datetime.datetime.now().isoformat()
        }

        with open(bookmark_file, 'w', encoding='utf-8') as f:
            json.dump(bookmark_data, f, ensure_ascii=False, indent=2)

        os.chmod(bookmark_file, 0o600)

        send_response(200, {
            'success': True,
            'bookmarkId': bookmark_id,
            'message': 'Bookmark erfolgreich gespeichert'
        })

    except json.JSONDecodeError as e:
        send_response(400, {'error': 'Ungültiges JSON', 'details': str(e)})
    except Exception as e:
        send_response(500, {'error': 'Interner Serverfehler', 'details': str(e)})

if __name__ == '__main__':
    main()
