#!/usr/bin/python3
# -*- coding: utf-8 -*-

# =============================================================================
# OPENAI API PROXY
# Erstellt: 10.03.2026
# Aktualisiert: 19.07.2026 (Bild-Uebertragung ergaenzt; Modelle auf GPT-5.5/5.6 aktualisiert)
# =============================================================================
#
# Unterstuetzte Modelle:
#
#   --- FREE PLAN (guenstige Einstiegs-Modelle; OpenAI selbst bietet aktuell
#                   keinen echten kostenlosen API-Tier — siehe Hinweis unten) ---
#
#   gpt-4o-mini  [Free]
#     Version      : GPT-4o Mini (Stand 10.03.2026)
#     Kontext      : 128.000 Token Input / 16.384 Token Output
#     Faehigkeiten : Text, Bilder (Vision), JSON-Mode, Function Calling
#     Achtung      : Abschaltung angekuendigt fuer 23.10.2026 (mit GPT-4o,
#                    GPT-4, GPT-4 Turbo, GPT-3.5 Turbo u.a.)
#
#   gpt-5.6-luna  [Free]
#     Version      : GPT-5.6 Luna (Veroeffentlicht 09.07.2026)
#     Kontext      : 1.050.000 Token Input / 128.000 Token Output
#     Faehigkeiten : Text, Bilder, Function Calling — guenstigste/schnellste
#                    Stufe der GPT-5.6-Familie (entspricht der frueheren "nano"-Stufe)
#
#   --- PAID PLAN ---
#
#   gpt-5.6-sol  [Paid]
#     Version      : GPT-5.6 Sol (Veroeffentlicht 09.07.2026)
#     Kontext      : 1.050.000 Token Input / 128.000 Token Output
#     Faehigkeiten : Text, Bilder, Computer Use, Function Calling, Tool Search
#     Hinweis      : Aktuelles Flaggschiff-Modell (Alias 'gpt-5.6' zeigt auf Sol)
#
#   gpt-5.6-terra  [Paid]
#     Version      : GPT-5.6 Terra (Veroeffentlicht 09.07.2026)
#     Kontext      : 1.050.000 Token Input / 128.000 Token Output
#     Faehigkeiten : Text, Bilder, Function Calling — ausgewogen zwischen
#                    Leistung und Kosten
#
#   gpt-5.5  [Paid]
#     Version      : GPT-5.5 (Veroeffentlicht 23.04.2026)
#     Kontext      : 1.050.000 Token Input / 128.000 Token Output
#     Faehigkeiten : Text, Bilder, Function Calling
#
#   gpt-5.4  [Paid]
#     Version      : GPT-5.4 (Veroeffentlicht 05.03.2026)
#     Kontext      : 1.050.000 Token Input / 16.384 Token Output
#     Faehigkeiten : Text, Bilder, Computer Use, Function Calling, Tool Search
#
#   gpt-4o  [Paid]
#     Version      : GPT-4o (Stand 10.03.2026)
#     Kontext      : 128.000 Token Input / 16.384 Token Output
#     Faehigkeiten : Text, Bilder, Audio, Function Calling
#     Achtung      : Abschaltung angekuendigt fuer 23.10.2026
#
#   gpt-4.1  [Paid]
#     Version      : GPT-4.1 (Stand 10.03.2026)
#     Kontext      : 1.048.576 Token Input / 32.768 Token Output
#     Faehigkeiten : Text, Bilder, Function Calling (optimiert fuer Coding)
#
#   gpt-4o-mini  [Paid]
#     (auch im Free Plan verfuegbar)
#
# ENTFERNT (nicht mehr auf OpenAIs offizieller Modell-/Preisliste gefuehrt,
# Stand 19.07.2026): gpt-5-mini, gpt-5.2-chat-latest
#
# Hinweis: GPT-5.4/5.5/5.6 Pro-Varianten sind ausschliesslich ueber die
#          Responses API verfuegbar und werden hier nicht unterstuetzt
#          (Chat Completions API only). Fuer GPT-5.4/5.5/5.6 existiert kein
#          offizieller kostenloser API-Tier (Stand 19.07.2026) — die "Free"-
#          Einstufung hier bezeichnet lediglich die guenstigsten Modelle.
#
# Quelle: https://platform.openai.com/docs/models (Stand 19.07.2026)
# =============================================================================

import json
import sys
import os
import traceback
import urllib.request
import urllib.error
import datetime

# Sicherheits-Fix (26.07.2026): CORS-Wildcard durch feste Origin ersetzt,
# zusaetzlich serverseitiges Request-Groessenlimit gegen Missbrauch/DoS.
ALLOWED_ORIGIN = 'https://172.29.255.1'
MAX_REQUEST_SIZE = 20 * 1024 * 1024  # 20 MB

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
    print(f"Access-Control-Allow-Origin: {ALLOWED_ORIGIN}")
    print("Access-Control-Allow-Methods: POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()
    print(json.dumps(data, ensure_ascii=False))
    sys.stdout.flush()
    log_to_file(status_code, data)

def main():
    try:
        # API-Key aus Umgebungsvariable laden
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            send_error(500, {
                'error': 'API-Key nicht konfiguriert. Bitte OPENAI_API_KEY in /etc/apache2/envvars setzen.'
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

        # Sicherheits-Fix (26.07.2026): Request-Groessenlimit gegen Missbrauch/DoS
        if content_length > MAX_REQUEST_SIZE:
            send_error(413, {
                'error': f'Anfrage zu gross (max. {MAX_REQUEST_SIZE // (1024*1024)} MB)'
            })
            return

        # POST-Daten lesen
        # Fix (29.08.2026): sys.stdin.read() im Textmodus kann je nach
        # CGI-Locale Mehrbyte-UTF-8-Zeichen (z.B. Emojis) fehlerhaft dekodieren
        # und dabei ungueltige Steuerzeichen einstreuen, was json.loads() mit
        # "Invalid control character" zum Absturz bringt. Rohe Bytes lesen und
        # explizit als UTF-8 dekodieren umgeht das CGI-Locale-Problem komplett.
        post_data = sys.stdin.buffer.read(content_length).decode('utf-8')
        request_data = json.loads(post_data)

        # Validierung
        model = request_data.get('model', 'gpt-4o-mini')
        messages = request_data.get('messages', [])
        max_tokens = request_data.get('max_tokens', 2000)
        audio_data = request_data.get('audio_data', None)
        audio_mime_type = request_data.get('audio_mime_type', 'audio/webm')
        image_data = request_data.get('image_data', None)
        image_mime_type = request_data.get('image_mime_type', 'image/jpeg')

        if not messages or not isinstance(messages, list):
            send_error(400, {
                'error': 'Ungueltige Anfrage: messages Array erforderlich'
            })
            return

        # Audio- und/oder Bild-Daten an letzte User-Message anhaengen
        if audio_data or image_data:
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    text = msg.get('content', '')
                    content_parts = [{'type': 'text', 'text': text}]
                    if audio_data:
                        fmt = 'mp4' if (audio_mime_type and 'mp4' in audio_mime_type) else 'webm'
                        content_parts.append({
                            'type': 'input_audio',
                            'input_audio': {'data': audio_data, 'format': fmt}
                        })
                    if image_data:
                        content_parts.append({
                            'type': 'image_url',
                            'image_url': {'url': f'data:{image_mime_type};base64,{image_data}'}
                        })
                    msg['content'] = content_parts
                    break

        # OpenAI API — Chat Completions Endpunkt
        api_url = 'https://api.openai.com/v1/chat/completions'

        api_request_data = {
            'model':      model,
            'messages':   messages,
            # max_completion_tokens statt max_tokens: funktioniert bei ALLEN
            # Modellen (alt und neu), waehrend max_tokens von den neueren
            # GPT-5.x-Modellen mit HTTP 400 abgelehnt wird ("Unsupported
            # parameter: 'max_tokens' is not supported with this model.
            # Use 'max_completion_tokens' instead.")
            'max_completion_tokens': max_tokens,
            'stream':     True
        }

        headers = {
            'Content-Type':  'application/json',
            'Authorization': f'Bearer {api_key}',
            'User-Agent':    'Mozilla/5.0 (compatible; openai-proxy/1.0)'
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
            # HTTP 429: prüfen ob Guthaben aufgebraucht (insufficient_quota)
            # oder nur ein temporäres Rate-Limit
            error_type = None
            if e.code == 429:
                try:
                    error_json = json.loads(error_body)
                    error_code = error_json.get('error', {}).get('code', '')
                    if error_code == 'insufficient_quota':
                        error_type = 'insufficient_quota'
                    elif error_code == 'daily_request_limit_exceeded':
                        error_type = 'daily_limit_exceeded'
                except Exception:
                    pass
            # HTTP 400: prüfen ob Kontextfenster überschritten
            elif e.code == 400:
                try:
                    error_json = json.loads(error_body)
                    error_code = error_json.get('error', {}).get('code', '')
                    if error_code == 'context_length_exceeded' or 'context_length_exceeded' in error_body:
                        error_type = 'context_exceeded'
                except Exception:
                    context_keywords = ['context', 'length', 'token', 'maximum']
                    if sum(1 for kw in context_keywords if kw.lower() in error_body.lower()) >= 2:
                        error_type = 'context_exceeded'
            if error_type:
                send_error(e.code, {
                    'error': f'OpenAI API Fehler: {e.code}',
                    'error_type': error_type,
                    'details': error_body
                })
            else:
                send_error(e.code, {
                    'error': f'OpenAI API Fehler: {e.code}',
                    'details': error_body
                })
            return
        except urllib.error.URLError as e:
            send_error(500, {
                'error': 'Verbindung zur OpenAI API fehlgeschlagen',
                'details': str(e.reason)
            })
            return

        # SSE-Header senden (erst nach erfolgreicher API-Verbindung)
        print("Status: 200")
        print("Content-Type: text/event-stream")
        print(f"Access-Control-Allow-Origin: {ALLOWED_ORIGIN}")
        print("Access-Control-Allow-Methods: POST, OPTIONS")
        print("Access-Control-Allow-Headers: Content-Type")
        print("Cache-Control: no-cache")
        print("X-Accel-Buffering: no")
        print()
        sys.stdout.flush()

        # OpenAI gibt OpenAI-kompatibles SSE-Format zurueck — direkt weiterleiten
        # Format: data: {"choices":[{"delta":{"content":"token"}}]}
        with response:
            buffer = ''
            for chunk in response:
                decoded = chunk.decode('utf-8')
                buffer += decoded
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('data: '):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        if data_str == '[DONE]':
                            sys.stdout.write('data: [DONE]\n\n')
                            sys.stdout.flush()
                            continue
                        try:
                            chunk_data = json.loads(data_str)
                            choices = chunk_data.get('choices', [])
                            if choices:
                                delta = choices[0].get('delta', {})
                                text_token = delta.get('content', '')
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
