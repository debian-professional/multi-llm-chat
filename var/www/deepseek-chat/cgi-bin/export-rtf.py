#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export-rtf.py - Chat als RTF exportieren (ohne externe Library)
/var/www/deepseek-chat/cgi-bin/export-rtf.py
"""

import sys
import json
import os
from datetime import datetime

# Sicherheits-Fix (26.07.2026): Request-Groessenlimit gegen Missbrauch/DoS.
# Hinweis: Dieses Skript setzt bereits keinen CORS-Header, d.h. Cross-Origin-
# Lesezugriffe sind per Browser-Default bereits blockiert.
MAX_REQUEST_SIZE = 20 * 1024 * 1024  # 20 MB (Chat kann eingebettete Bilder enthalten)

def send_response(content, content_type, filename):
    if isinstance(content, str):
        content = content.encode('latin-1', errors='replace')
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

def escape_rtf(text):
    """Text fuer RTF escapen und Umlaute konvertieren"""
    # RTF Sonderzeichen escapen
    text = text.replace('\\', '\\\\')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    # Nicht-ASCII-Zeichen als RTF-Codes (Umlaute, Spanisch usw.; ansicpg1252)
    # Changelog 117: vorher nur ae/oe/ue/ss, jetzt alle Zeichen ab 128.
    out = []
    for ch in text:
        code = ord(ch)
        if code < 128:
            out.append(ch)
        elif code < 256:
            out.append("\\'%02x" % code)
        else:
            signed = code if code < 32768 else code - 65536
            out.append("\\u%d?" % signed)
    text = ''.join(out)
    # Zeilenumbrueche
    text = text.replace('\n', '\\par\n')
    return text

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

        date_str = timestamp[:10]
        time_str = timestamp[11:19]

        # RTF Dokument aufbauen
        rtf_parts = []
        rtf_parts.append(r'{\rtf1\ansi\ansicpg1252\deff0')
        rtf_parts.append(r'{\fonttbl{\f0\fswiss\fcharset0 Arial;}{\f1\fmodern\fcharset0 Courier New;}}')
        rtf_parts.append(r'{\colortbl;\red0\green86\blue179;\red40\green40\blue40;\red220\green53\blue69;\red40\green167\blue69;}')
        rtf_parts.append(r'\f0\fs22\sa200')
        rtf_parts.append('')

        # Titel
        rtf_parts.append(r'{\pard\qc\sb300{\b\fs32\cf1 ' + escape_rtf(L['title']) + r'}\par}')
        rtf_parts.append(r'{\pard\qc\sb100{\fs20\cf2 ' + f'{escape_rtf(L["server"])}: {escape_rtf(server_info.get("name", "Multi-LLM Chat"))}' + r'}\par}')
        rtf_parts.append(r'{\pard\qc\sb100{\fs20\cf2 ' + f'IP: {escape_rtf(server_info.get("ip", L["unknown"].lower()))}' + r'}\par}')
        rtf_parts.append(r'{\pard\qc\sb100{\fs20\cf2 ' + f'{escape_rtf(L["date"])}: {date_str}  {escape_rtf(L["time"])}: {time_str}' + r'}\par}')
        rtf_parts.append(r'{\pard\qc\sb100{\fs20\cf2 ' + f'{escape_rtf(L["messages"])}: {len(messages)}' + r'}\par}')
        rtf_parts.append(r'{\pard\brdrb\brdrs\brdrw10\brsp20 \par}')
        rtf_parts.append('')

        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            msg_time = msg.get('timestamp', '')[:19].replace('T', ' ')

            if role == 'user':
                label = f'{L["user"].upper()} [{msg_time}]'
                color = r'\cf1'
            else:
                label = f'{L["ai"].upper()} [{msg_time}]'
                color = r'\cf4'

            # Rolle als Header
            rtf_parts.append(r'{\pard\sb200{\b\fs24' + color + ' ' + escape_rtf(label) + r'}\par}')
            rtf_parts.append(r'{\pard\sb50\brdrb\brdrs\brdrw5\brsp10 \par}')
            # Nachrichtentext
            rtf_parts.append(r'{\pard\sb100\f0\fs22\cf2 ' + escape_rtf(content) + r'\par}')
            rtf_parts.append(r'{\pard\sb200\brdrb\brdrs\brdrw15\brsp20 \par}')
            rtf_parts.append('')

        rtf_parts.append('}')

        rtf_content = '\n'.join(rtf_parts)
        filename = f"deepseek-chat-{date_str}.rtf"
        send_response(rtf_content, "application/rtf", filename)

    except Exception as e:
        send_error(str(e))

if __name__ == '__main__':
    main()







