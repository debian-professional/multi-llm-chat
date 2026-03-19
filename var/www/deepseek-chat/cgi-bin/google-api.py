############ FILE: var/www/deepseek-chat/cgi-bin/google-api.py ############
---------------------------------------------------------
#!/usr/bin/python3
# -*- coding: utf-8 -*-

# =============================================================================
# GOOGLE GEMINI API PROXY
# Importiert / aktualisiert: 08.03.2026
# =============================================================================
#
# Unterstuetzte Modelle:
#
#   gemini-2.5-flash  [Free + Paid]
#     Version      : Gemini 2.5 Flash (Stand 08.03.2026)
#     Kontext      : 1.048.576 Token Input / 8.192 Token Output
#     Faehigkeiten : Text, Bilder, Audio, Video
#     Free-Limit   : 20 Anfragen/Tag, 5 Anfragen/Minute
#
#   gemini-2.5-pro  [Paid]
#     Version      : Gemini 2.5 Pro (Stand 08.03.2026)
#     Kontext      : 1.048.576 Token Input / 65.536 Token Output
#     Faehigkeiten : Text, Bilder, Audio, Video
#
#   gemini-2.0-flash  [Paid]
#     Version      : Gemini 2.0 Flash (Stand 08.03.2026)
#     Kontext      : 1.048.576 Token Input / 8.192 Token Output
#     Faehigkeiten : Text, Bilder, Audio, Video
#
#   gemini-1.5-pro  [Paid]
#     Version      : Gemini 1.5 Pro (Stand 08.03.2026)
#     Kontext      : 2.097.152 Token Input / 8.192 Token Output
#     Faehigkeiten : Text, Bilder, Audio, Video
#
# Quelle: https://ai.google.dev/gemini-api/docs (Stand 08.03.2026)
# =============================================================================

import json
import sys
import os
import traceback
import urllib.request
import urllib.error
import datetime

def log_to_file(status_code, response_data):
    """Schreibt ausgewählte Informationen in die Log-Datei (ohne API-Key)."""
    try:
        if os.environ.get('REQUEST_METHOD') == 'OPTIONS':
            return
        log_path = '/var/www/deepseek-chat/logs/multi-llm-chat.log'
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        ip = os.environ.get('REMOTE_ADDR', 'unknown')
        method = os.environ.get('REQUEST_METHOD', 'unknown')
        path = os.environ.get('REQUEST_URI', 'unknown')
        timestamp = datetime.datetime.now().isoformat()
        error_msg = None
        details = None
        if isinstance(response_data, dict):
            error_msg = response_data.get('error')
            details = response_data.get('details')
        log_line = f"{timestamp} | IP: {ip} | {method} {path} | Status: {status_code}"
        if error_msg:
            log_line += f" | Error: {error_msg}"
        if details:
            # Details auf 300 Zeichen begrenzen
            details_short = details[:300].replace('\n', ' ')
            log_line += f" | Details: {details_short}"
        log_line += "\n"
        with open(log_path, 'a') as f:
            f.write(log_line)
    except Exception:
        pass

def send_error(status_code, data):
    """Sendet Fehler-Response als JSON."""
    print(f"Status: {status_code}")
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()
    print(json.dumps(data, ensure_ascii=False))
    sys.stdout.flush()
    log_to_file(status_code, data)

def convert_messages_to_gemini(messages, audio_data=None, audio_mime_type=None):
    """Konvertiert OpenAI-Format messages in Gemini-Format."""
    system_instruction = None
    contents = []
    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        if role == 'system':
            system_instruction = content
        elif role == 'assistant':
            contents.append({'role': 'model', 'parts': [{'text': content}]})
        else:
            contents.append({'role': 'user', 'parts': [{'text': content}]})
    # Audio-Daten an letzte User-Message anhaengen
    if audio_data and audio_mime_type and contents:
        last_user = next((c for c in reversed(contents) if c['role'] == 'user'), None)
        if last_user:
            last_user['parts'].append({
                'inline_data': {
                    'mime_type': audio_mime_type,
                    'data': audio_data
                }
            })
    return system_instruction, contents

def main():
    try:
        # API-Key aus Umgebungsvariable laden
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            send_error(500, {
                'error': 'API-Key nicht konfiguriert. Bitte GOOGLE_API_KEY in /etc/apache2/envvars setzen.'
            })
            return

        request_method = os.environ.get('REQUEST_METHOD', '')

        # OPTIONS Request (CORS Preflight)
        if request_method == 'OPTIONS':
            send_error(200, {'status': 'ok'})
            return

        # Nur POST erlaubt
        if request_method != 'POST':
            send_error(405, {
                'error': f'Methode nicht erlaubt: {request_method}. Nur POST ist erlaubt.'
            })
            return

        # Content-Length lesen
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        if content_length == 0:
            send_error(400, {
                'error': 'Leere Anfrage. Bitte model, messages und max_tokens senden.'
            })
            return

        # POST-Daten lesen
        post_data = sys.stdin.read(content_length)
        request_data = json.loads(post_data)

        # Validierung
        model = request_data.get('model', 'gemini-2.0-flash')
        messages = request_data.get('messages', [])
        max_tokens = request_data.get('max_tokens', 2000)
        audio_data = request_data.get('audio_data', None)
        audio_mime_type = request_data.get('audio_mime_type', None)

        if not messages or not isinstance(messages, list):
            send_error(400, {
                'error': 'Ungueltige Anfrage: messages Array erforderlich'
            })
            return

        # Messages in Gemini-Format konvertieren
        system_instruction, contents = convert_messages_to_gemini(messages, audio_data, audio_mime_type)

        # Google Gemini API Request vorbereiten (mit Streaming)
        api_url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}'

        api_request_data = {
            'contents': contents,
            'generationConfig': {
                'maxOutputTokens': max_tokens
            }
        }

        if system_instruction:
            api_request_data['system_instruction'] = {
                'parts': [{'text': system_instruction}]
            }

        headers = {
            'Content-Type': 'application/json'
        }

        req = urllib.request.Request(
            api_url,
            data=json.dumps(api_request_data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        # API-Verbindung herstellen (VOR dem Senden der SSE-Header)
        try:
            response = urllib.request.urlopen(req, timeout=60)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            # HTTP 429: prüfen ob Tageslimit (RESOURCE_EXHAUSTED per_day)
            # oder nur ein temporäres RPM-Limit (wird clientseitig retried)
            if e.code == 429:
                daily_keywords = ['per_day', 'daily', 'RATE_LIMIT_EXCEEDED']
                is_daily = any(kw.lower() in error_body.lower() for kw in daily_keywords)
                if is_daily:
                    send_error(e.code, {
                        'error': f'Google Gemini API Fehler: {e.code}',
                        'error_type': 'daily_limit',
                        'details': error_body
                    })
                else:
                    send_error(e.code, {
                        'error': f'Google Gemini API Fehler: {e.code}',
                        'details': error_body
                    })
            else:
                # HTTP 400: prüfen ob Kontextfenster überschritten
                if e.code == 400:
                    context_keywords = ['token', 'context', 'length', 'maximum', 'INVALID_ARGUMENT']
                    if sum(1 for kw in context_keywords if kw.lower() in error_body.lower()) >= 2:
                        send_error(e.code, {
                            'error': f'Google Gemini API Fehler: {e.code}',
                            'error_type': 'context_exceeded',
                            'details': error_body
                        })
                        return
                send_error(e.code, {
                    'error': f'Google Gemini API Fehler: {e.code}',
                    'details': error_body
                })
            return
        except urllib.error.URLError as e:
            send_error(500, {
                'error': 'Verbindung zur Google Gemini API fehlgeschlagen',
                'details': str(e.reason)
            })
            return

        # SSE-Header senden (erst nach erfolgreicher API-Verbindung)
        print("Status: 200")
        print("Content-Type: text/event-stream")
        print("Access-Control-Allow-Origin: *")
        print("Access-Control-Allow-Methods: POST, OPTIONS")
        print("Access-Control-Allow-Headers: Content-Type")
        print("Cache-Control: no-cache")
        print("X-Accel-Buffering: no")
        print()
        sys.stdout.flush()

        # Gemini SSE-Stream lesen und in DeepSeek-kompatibles Format konvertieren
        with response:
            buffer = ''
            for chunk in response:
                decoded = chunk.decode('utf-8')
                buffer += decoded
                # Zeilen verarbeiten
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('data: '):
                        data_str = line[6:].strip()
                        if not data_str or data_str == '[DONE]':
                            sys.stdout.write('data: [DONE]\n\n')
                            sys.stdout.flush()
                            continue
                        try:
                            gemini_data = json.loads(data_str)
                            # Gemini -> DeepSeek Format konvertieren
                            candidates = gemini_data.get('candidates', [])
                            if candidates:
                                parts = candidates[0].get('content', {}).get('parts', [])
                                if parts:
                                    text_token = parts[0].get('text', '')
                                    if text_token:
                                        openai_chunk = {
                                            'choices': [{
                                                'delta': {'content': text_token}
                                            }]
                                        }
                                        sys.stdout.write(f'data: {json.dumps(openai_chunk)}\n\n')
                                        sys.stdout.flush()
                        except json.JSONDecodeError:
                            pass

        sys.stdout.write('data: [DONE]\n\n')
        sys.stdout.flush()
        log_to_file(200, {})

    except json.JSONDecodeError as e:
        send_error(400, {
            'error': 'Ungültiges JSON',
            'details': str(e)
        })

    except Exception as e:
        error_details = traceback.format_exc()
        send_error(500, {
            'error': 'Interner Serverfehler',
            'message': str(e),
            'details': error_details
        })

if __name__ == '__main__':
    main()



