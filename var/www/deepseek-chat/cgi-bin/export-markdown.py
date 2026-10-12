#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import sys
import os

# Sicherheits-Fix (26.07.2026): CORS-Wildcard durch feste Origin ersetzt,
# zusaetzlich Request-Groessenlimit gegen Missbrauch/DoS.
ALLOWED_ORIGIN = 'https://172.29.255.1'
MAX_REQUEST_SIZE = 20 * 1024 * 1024  # 20 MB (Chat kann eingebettete Bilder enthalten)

def send_response(status_code, data, content_type='application/json'):
    """Sendet HTTP-Response zurück."""
    print(f"Status: {status_code}")
    print(f"Content-Type: {content_type}; charset=utf-8")
    print(f"Access-Control-Allow-Origin: {ALLOWED_ORIGIN}")
    print("Access-Control-Allow-Methods: POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    if content_type == 'text/markdown':
        print(f"Content-Disposition: attachment; filename=\"deepseek-chat-export.md\"")
    print()
    if isinstance(data, str):
        print(data)
    else:
        print(json.dumps(data, ensure_ascii=False))
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

def calculate_statistics(messages, L=None):
    """Berechnet Statistiken aus den Nachrichten."""
    L = L or DEFAULT_LABELS
    total_messages = len(messages)
    user_messages = len([m for m in messages if m['role'] == 'user'])
    ai_messages = len([m for m in messages if m['role'] == 'assistant'])
    
    modes = {}
    files_count = 0
    total_tokens = 0
    
    for msg in messages:
        mode = msg.get('mode', 'chat')
        modes[mode] = modes.get(mode, 0) + 1
        if msg.get('hasFile', False):
            files_count += 1
        total_tokens += msg.get('estimatedTokens', 0)
    
    # Chat-Dauer
    if messages:
        first_time = messages[0].get('timestamp', '')
        last_time = messages[-1].get('timestamp', '')
        duration = f"{first_time} {L['to']} {last_time}"
    else:
        duration = L['none']
    
    return {
        'total': total_messages,
        'user': user_messages,
        'ai': ai_messages,
        'modes': modes,
        'files': files_count,
        'tokens': total_tokens,
        'duration': duration
    }

def create_markdown(chat_data):
    """Erstellt Markdown aus Chat-Daten."""
    L = get_labels(chat_data)
    lines = []
    
    # Titel
    lines.append(f"# {L['title']}")
    lines.append("")
    
    # Server-Info
    server_info = chat_data.get('serverInfo', {})
    lines.append(f"**{L['server']}:** {server_info.get('name', L['unknown'])} (IP: {server_info.get('ip', L['unknown'])})")
    lines.append(f"**{L['export_date']}:** {chat_data.get('timestamp', L['unknown'])}")
    
    settings = chat_data.get('settings', {})
    lines.append(f"**{L['settings']}:** " + L['form_mode'].replace('{0}', str(settings.get('addressForm', 'sie'))).replace('{1}', str(settings.get('defaultMode', 'chat'))))
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Statistiken
    messages = chat_data.get('messages', [])
    stats = calculate_statistics(messages, L)
    
    lines.append(f"## {L['stats']}")
    lines.append("")
    lines.append(f"- **{L['total']}:** {stats['total']} ({L['user']}: {stats['user']}, {L['ai']}: {stats['ai']})")
    
    modes_text = ", ".join([f"{mode}: {count}x" for mode, count in stats['modes'].items()])
    lines.append(f"- **{L['modes']}:** {modes_text}")
    lines.append(f"- **{L['files']}:** {stats['files']}")
    lines.append(f"- **{L['tokens']}:** {stats['tokens']}")
    lines.append(f"- **{L['duration']}:** {stats['duration']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Inhaltsverzeichnis
    lines.append(f"## {L['toc']}")
    lines.append("")
    for idx, msg in enumerate(messages, 1):
        role = L['user'] if msg['role'] == 'user' else L['ai']
        preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
        lines.append(f"- [{L['message']} {idx} ({role})](#msg-{idx}): {preview}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Nachrichten
    lines.append(f"## {L['history']}")
    lines.append("")
    
    for idx, msg in enumerate(messages, 1):
        role = L['user'] if msg['role'] == 'user' else L['ai']
        timestamp = msg.get('timestamp', '')
        mode = msg.get('mode', 'chat')
        content = msg['content']
        
        lines.append(f"### {L['message']} {idx} - {role} [{mode.upper()}] {{#msg-{idx}}}")
        lines.append(f"*{timestamp}*")
        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Footer
    lines.append(f"*{L['footer']}*")
    
    return "\n".join(lines)

def main():
    try:
        request_method = os.environ.get('REQUEST_METHOD', '')

        # OPTIONS Request
        if request_method == 'OPTIONS':
            send_response(200, {'status': 'ok'})
            return

        # Nur POST erlaubt
        if request_method != 'POST':
            send_response(405, {'error': f'Methode nicht erlaubt: {request_method}'})
            return

        # Content-Length lesen
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        if content_length == 0:
            send_response(400, {'error': 'Leere Anfrage'})
            return

        # Sicherheits-Fix (26.07.2026): Request-Groessenlimit gegen Missbrauch/DoS
        if content_length > MAX_REQUEST_SIZE:
            send_response(413, {'error': f'Anfrage zu gross (max. {MAX_REQUEST_SIZE // (1024*1024)} MB)'})
            return

        # POST-Daten lesen
        # Fix (29.08.2026): sys.stdin.read() im Textmodus kann je nach
        # CGI-Locale Mehrbyte-UTF-8-Zeichen (z.B. Emojis) fehlerhaft dekodieren
        # und dabei ungueltige Steuerzeichen einstreuen, was json.loads() mit
        # "Invalid control character" zum Absturz bringt. Rohe Bytes lesen und
        # explizit als UTF-8 dekodieren umgeht das CGI-Locale-Problem komplett.
        post_data = sys.stdin.buffer.read(content_length).decode('utf-8')
        request_data = json.loads(post_data)
        
        chat_data = request_data.get('chatData')
        if not chat_data:
            send_response(400, {'error': 'Keine Chat-Daten'})
            return

        # Markdown erstellen
        markdown_data = create_markdown(chat_data)
        
        # Markdown zurückschicken
        send_response(200, markdown_data, content_type='text/markdown')

    except json.JSONDecodeError as e:
        send_response(400, {'error': 'Ungültiges JSON', 'details': str(e)})
    except Exception as e:
        send_response(500, {'error': 'Interner Serverfehler', 'details': str(e)})

if __name__ == '__main__':
    main()



