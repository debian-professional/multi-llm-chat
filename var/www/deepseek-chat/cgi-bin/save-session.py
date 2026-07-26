#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import sys
import os
import re
import datetime
import hashlib
from pathlib import Path

SESSIONS_DIR = '/var/www/deepseek-chat/sessions'

# Sicherheits-Fix (26.07.2026): Vorher wurde nur der Datum- und Zeit-Teil der
# Session-ID geprueft, der Zufallsteil (parts[2]) ueberhaupt nicht. Eine ID wie
# "2026-07-26_120000_../../../etc/cron.d/evil" bestand die alte Pruefung
# vollstaendig und ermoeglichte Path Traversal beim Schreiben der Session-Datei.
SESSION_ID_RE = re.compile(r'^\d{4}-\d{2}-\d{2}_\d{6}_[A-Za-z0-9]{6}$')

def create_sessions_dir():
    """Erstellt das Sessions-Verzeichnis falls nicht vorhanden."""
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR, mode=0o700)

def validate_session_id(session_id):
    """Validiert die Session-ID strikt gegen das Format YYYY-MM-DD_HHMMSS_xxxxxx."""
    if not isinstance(session_id, str) or not SESSION_ID_RE.fullmatch(session_id):
        return False
    try:
        datetime.datetime.strptime(session_id[:10], '%Y-%m-%d')
        datetime.datetime.strptime(session_id[11:17], '%H%M%S')
        return True
    except ValueError:
        return False

def resolve_session_path(session_id):
    """Loest den Session-Dateipfad auf und stellt sicher, dass er innerhalb
    von SESSIONS_DIR bleibt (Verteidigung gegen Path Traversal)."""
    sessions_dir = Path(SESSIONS_DIR).resolve()
    session_file = (sessions_dir / f'{session_id}.json').resolve()
    if session_file.parent != sessions_dir:
        raise ValueError('Ungültiger Session-Pfad')
    return str(session_file)

def send_response(status_code, data):
    """Sendet HTTP-Response zurück."""
    print(f"Status: {status_code}")
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()
    print(json.dumps(data, ensure_ascii=False))
    sys.stdout.flush()

def main():
    try:
        # Request-Methode prüfen
        request_method = os.environ.get('REQUEST_METHOD', '')

        # OPTIONS Request (CORS Preflight)
        if request_method == 'OPTIONS':
            send_response(200, {'status': 'ok'})
            return

        # Nur POST erlaubt
        if request_method != 'POST':
            send_response(405, {'error': f'Methode nicht erlaubt: {request_method}'})
            return

        # Sessions-Verzeichnis erstellen
        create_sessions_dir()

        # Content-Length lesen
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        if content_length == 0:
            send_response(400, {'error': 'Leere Anfrage'})
            return

        # POST-Daten lesen
        post_data = sys.stdin.read(content_length)
        request_data = json.loads(post_data)

        # Session-ID validieren
        session_id = request_data.get('sessionId')
        if not validate_session_id(session_id):
            send_response(400, {'error': 'Ungültige Session-ID'})
            return

        # Chat-Daten holen
        chat_data = request_data.get('chatData')
        if not chat_data:
            send_response(400, {'error': 'Keine Chat-Daten'})
            return

        # Session-Datei speichern (sicherer, aufgeloester Pfad)
        try:
            session_file = resolve_session_path(session_id)
        except ValueError:
            send_response(400, {'error': 'Ungültige Session-ID'})
            return

        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)

        # Dateirechte setzen (nur für Webserver lesbar)
        os.chmod(session_file, 0o600)

        send_response(200, {
            'success': True,
            'sessionId': session_id,
            'message': 'Chat erfolgreich gespeichert'
        })

    except json.JSONDecodeError as e:
        send_response(400, {'error': 'Ungültiges JSON', 'details': str(e)})
    except Exception as e:
        send_response(500, {'error': 'Interner Serverfehler', 'details': str(e)})

if __name__ == '__main__':
    main()




