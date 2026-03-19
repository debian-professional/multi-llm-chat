############ FILE: var/www/deepseek-chat/cgi-bin/deepseek-api.py ############
#!/usr/bin/python3
# -*- coding: utf-8 -*-

# =============================================================================
# DEEPSEEK API PROXY
# Importiert / aktualisiert: 08.03.2026
# =============================================================================
#
# Unterstuetzte Modelle:
#
#   deepseek-chat  (DeepSeek V3)
#     Version      : V3 (Stand 08.03.2026)
#     Kontext      : 64.000 Token Input / 8.192 Token Output
#     Faehigkeiten : Nur Text (kein Bild, kein Audio, kein Video)
#
#   deepseek-reasoner  (DeepSeek R1)
#     Version      : R1 (Stand 08.03.2026)
#     Kontext      : 64.000 Token Input / 32.768 Token Output
#     Faehigkeiten : Nur Text (kein Bild, kein Audio, kein Video)
#                    Internes Chain-of-Thought Reasoning (DeepThink)
#
# Quelle: https://api-docs.deepseek.com (Stand 08.03.2026)
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
        if isinstance(response_data, dict):
            error_msg = response_data.get('error')
        log_line = f"{timestamp} | IP: {ip} | {method} {path} | Status: {status_code}"
        if error_msg:
            log_line += f" | Error: {error_msg}"
        log_line += "\n"
        with open(log_path, 'a') as f:
            f.write(log_line)
    except Exception:
        pass

def send_error(status_code, data):
    """Sendet Fehler-Response als JSON (vor dem Streaming-Start)."""
    print(f"Status: {status_code}")
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()
    print(json.dumps(data, ensure_ascii=False))
    sys.stdout.flush()
    log_to_file(status_code, data)

def main():
    try:
        # API-Key aus Umgebungsvariable laden
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            send_error(500, {
                'error': 'API-Key nicht konfiguriert. Bitte DEEPSEEK_API_KEY in /etc/apache2/envvars setzen.'
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
        model = request_data.get('model', 'deepseek-chat')
        messages = request_data.get('messages', [])
        max_tokens = request_data.get('max_tokens', 2000)
        no_training = request_data.get('no_training', True)

        if not messages or not isinstance(messages, list):
            send_error(400, {
                'error': 'Ungueltige Anfrage: messages Array erforderlich'
            })
            return

        # DeepSeek API Request vorbereiten (mit Streaming)
        api_url = 'https://api.deepseek.com/v1/chat/completions'

        api_request_data = {
            'model': model,
            'messages': messages,
            'max_tokens': max_tokens,
            'stream': True
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        # X-No-Training Header setzen falls aktiviert
        if no_training:
            headers['X-No-Training'] = 'true'

        req = urllib.request.Request(
            api_url,
            data=json.dumps(api_request_data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        # API-Verbindung herstellen (VOR dem Senden der SSE-Header)
        # So können bei Verbindungsfehlern noch JSON-Fehler gesendet werden
        try:
            response = urllib.request.urlopen(req, timeout=60)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            # HTTP 402: Guthaben aufgebraucht
            if e.code == 402:
                send_error(e.code, {
                    'error': f'DeepSeek API Fehler: {e.code}',
                    'error_type': 'insufficient_quota',
                    'details': error_body
                })
            # HTTP 400: prüfen ob Kontextfenster überschritten
            elif e.code == 400:
                context_keywords = ['context', 'length', 'token', 'maximum']
                is_context = sum(1 for kw in context_keywords if kw.lower() in error_body.lower()) >= 2
                if is_context:
                    send_error(e.code, {
                        'error': f'DeepSeek API Fehler: {e.code}',
                        'error_type': 'context_exceeded',
                        'details': error_body
                    })
                else:
                    send_error(e.code, {
                        'error': f'DeepSeek API Fehler: {e.code}',
                        'details': error_body
                    })
            else:
                send_error(e.code, {
                    'error': f'DeepSeek API Fehler: {e.code}',
                    'details': error_body
                })
            return
        except urllib.error.URLError as e:
            send_error(500, {
                'error': 'Verbindung zur DeepSeek API fehlgeschlagen',
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

        # Stream von DeepSeek direkt an den Client weiterleiten
        with response:
            for line in response:
                decoded = line.decode('utf-8')
                sys.stdout.write(decoded)
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



