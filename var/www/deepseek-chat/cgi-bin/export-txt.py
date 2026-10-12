#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export-txt.py - Chat als TXT exportieren
/var/www/deepseek-chat/cgi-bin/export-txt.py
"""

import sys
import json
import os
from datetime import datetime

# Sicherheits-Fix (26.07.2026): Request-Groessenlimit gegen Missbrauch/DoS.
# Hinweis: Dieses Skript setzt bereits keinen CORS-Header, d.h. Cross-Origin-
# Lesezugriffe sind per Browser-Default bereits blockiert.
MAX_REQUEST_SIZE = 20 * 1024 * 1024  # 20 MB (Chat kann eingebettete Bilder enthalten)

# Changelog 117 (12.10.2026): Beschriftungen kommen uebersetzt vom Frontend
# (chatData.labels, aus language.xml). Fehlen sie, gelten diese deutschen
# Standardwerte - alte Frontends funktionieren also unveraendert weiter.
DEFAULT_LABELS = {
    'title': 'Multi-LLM-Chat - Export', 'server': 'Server', 'date': 'Datum',
    'time': 'Uhrzeit', 'messages': 'Nachrichten', 'user': 'Benutzer', 'ai': 'KI',
    'exported': 'Exportiert', 'export_date': 'Export-Datum',
    'settings': 'Einstellungen', 'form_mode': '{0}-Form, Modus: {1}',
    'stats': 'Statistiken', 'total': 'Nachrichten gesamt',
    'modes': 'Verwendete Modi', 'files': 'Hochgeladene Dateien',
    'tokens': 'Geschaetzte Token-Nutzung', 'duration': 'Chat-Dauer',
    'none': 'Keine Nachrichten', 'to': 'bis', 'toc': 'Inhaltsverzeichnis',
    'history': 'Chat-Verlauf', 'message': 'Nachricht', 'unknown': 'Unbekannt',
    'footer': 'Exportiert mit Multi-LLM-Chat',
}

def get_labels(chat_data):
    """Liefert die Beschriftungen (Frontend-Labels ueberschreiben die Standardwerte)."""
    labels = dict(DEFAULT_LABELS)
    custom = chat_data.get('labels')
    if isinstance(custom, dict):
        for key, value in custom.items():
            if key in labels and isinstance(value, str) and value.strip() and len(value) <= 200:
                labels[key] = value
    return labels

def send_response(content, content_type, filename):
    if isinstance(content, str):
        content = content.encode('utf-8')
    sys.stdout.buffer.write(f"Content-Type: {content_type}\r\n".encode())
    sys.stdout.buffer.write(f"Content-Disposition: attachment; filename=\"{filename}\"\r\n".encode())
    sys.stdout.buffer.write(f"Content-Length: {len(content)}\r\n".encode())
    sys.stdout.buffer.write(b"\r\n")
    sys.stdout.buffer.write(content)
    sys.stdout.buffer.flush()

def send_error(message, code=500):
    sys.stdout.write(f"Status: {code}\r\n")
    sys.stdout.write("Content-Type: application/json\r\n\r\n")
    sys.stdout.write(json.dumps({"error": message}))
    sys.stdout.flush()

def main():
    try:
        if os.environ.get('REQUEST_METHOD') != 'POST':
            send_error("Nur POST erlaubt", 405)
            return

        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        if content_length > MAX_REQUEST_SIZE:
            send_error(f"Anfrage zu gross (max. {MAX_REQUEST_SIZE // (1024*1024)} MB)", 413)
            return
        raw_data = sys.stdin.buffer.read(content_length)
        data = json.loads(raw_data.decode('utf-8'))
        chat_data = data.get('chatData', {})
        messages = chat_data.get('messages', [])
        server_info = chat_data.get('serverInfo', {})
        timestamp = chat_data.get('timestamp', datetime.now().isoformat())
        L = get_labels(chat_data)

        lines = []
        lines.append("=" * 60)
        lines.append(L['title'].upper())
        lines.append("=" * 60)
        lines.append(f"{L['server']}: {server_info.get('name', 'Multi-LLM Chat')}")
        lines.append(f"IP: {server_info.get('ip', L['unknown'].lower())}")
        lines.append(f"{L['date']}: {timestamp[:10]}  {L['time']}: {timestamp[11:19]}")
        lines.append(f"{L['messages']}: {len(messages)}")
        lines.append("=" * 60)
        lines.append("")

        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            msg_time = msg.get('timestamp', '')[:19].replace('T', ' ')

            if role == 'user':
                lines.append(f"{L['user'].upper()} [{msg_time}]:")
                lines.append("-" * 40)
            else:
                lines.append(f"{L['ai'].upper()} [{msg_time}]:")
                lines.append("-" * 40)

            lines.append(content)
            lines.append("")
            lines.append("=" * 60)
            lines.append("")

        txt_content = "\n".join(lines)
        filename = f"deepseek-chat-{timestamp[:10]}.txt"
        send_response(txt_content, "text/plain; charset=utf-8", filename)

    except Exception as e:
        send_error(str(e))

if __name__ == '__main__':
    main()






