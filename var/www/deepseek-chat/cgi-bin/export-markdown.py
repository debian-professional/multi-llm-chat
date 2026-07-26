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

def calculate_statistics(messages):
    """Berechnet Statistiken aus den Nachrichten."""
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
        duration = f"{first_time} bis {last_time}"
    else:
        duration = "Keine Nachrichten"
    
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
    lines = []
    
    # Titel
    lines.append("# DeepSeek Chat - Export")
    lines.append("")
    
    # Server-Info
    server_info = chat_data.get('serverInfo', {})
    lines.append(f"**Server:** {server_info.get('name', 'Unbekannt')} (IP: {server_info.get('ip', 'Unbekannt')})")
    lines.append(f"**Export-Datum:** {chat_data.get('timestamp', 'Unbekannt')}")
    
    settings = chat_data.get('settings', {})
    lines.append(f"**Einstellungen:** {settings.get('addressForm', 'sie')}-Form, Modus: {settings.get('defaultMode', 'chat')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Statistiken
    messages = chat_data.get('messages', [])
    stats = calculate_statistics(messages)
    
    lines.append("## Statistiken")
    lines.append("")
    lines.append(f"- **Nachrichten gesamt:** {stats['total']} (Benutzer: {stats['user']}, KI: {stats['ai']})")
    
    modes_text = ", ".join([f"{mode}: {count}x" for mode, count in stats['modes'].items()])
    lines.append(f"- **Verwendete Modi:** {modes_text}")
    lines.append(f"- **Hochgeladene Dateien:** {stats['files']}")
    lines.append(f"- **Geschaetzte Token-Nutzung:** {stats['tokens']}")
    lines.append(f"- **Chat-Dauer:** {stats['duration']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Inhaltsverzeichnis
    lines.append("## Inhaltsverzeichnis")
    lines.append("")
    for idx, msg in enumerate(messages, 1):
        role = "Benutzer" if msg['role'] == 'user' else "KI"
        preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
        lines.append(f"- [Nachricht {idx} ({role})](#nachricht-{idx}): {preview}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Nachrichten
    lines.append("## Chat-Verlauf")
    lines.append("")
    
    for idx, msg in enumerate(messages, 1):
        role = "Benutzer" if msg['role'] == 'user' else "KI"
        timestamp = msg.get('timestamp', '')
        mode = msg.get('mode', 'chat')
        content = msg['content']
        
        lines.append(f"### Nachricht {idx} - {role} [{mode.upper()}] {{#nachricht-{idx}}}")
        lines.append(f"*{timestamp}*")
        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Footer
    lines.append("*Exportiert mit DeepSeek Chat v1.0*")
    
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
        post_data = sys.stdin.read(content_length)
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



