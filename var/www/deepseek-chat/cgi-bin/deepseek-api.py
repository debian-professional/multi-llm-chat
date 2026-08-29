#!/usr/bin/python3
# -*- coding: utf-8 -*-


# =============================================================================
# DEEPSEEK API PROXY
# Importiert / aktualisiert: 29.08.2026 (Fix: UTF-8-Dekodierung des Request-Body)
# =============================================================================
#
# Unterstuetzte Modelle:
#
#   deepseek-v4-flash  (DeepSeek V4 Flash)
#     Version      : V4 Preview (Stand 11.05.2026)
#     Kontext      : 1.048.576 Token Input / 8.192 Token Output
#     Faehigkeiten : Nur Text (kein Bild, kein Audio, kein Video)
#                    Thinking- und Non-Thinking-Mode verfuegbar
#
#   deepseek-v4-pro  (DeepSeek V4 Pro)
#     Version      : V4 Preview (Stand 11.05.2026)
#     Kontext      : 1.048.576 Token Input / 32.768 Token Output
#     Faehigkeiten : Nur Text (kein Bild, kein Audio, kein Video)
#                    Thinking- und Non-Thinking-Mode verfuegbar
#
# Hinweis: deepseek-chat und deepseek-reasoner werden ab 24.07.2026
#          abgeschaltet (routen aktuell auf deepseek-v4-flash).
#
# Fix (28.08.2026): Der DeepSeek-Thinking-Mode ist API-seitig standardmaessig
# aktiv (High-Effort) - unabhaengig vom Modellnamen, seit deepseek-chat/
# deepseek-reasoner nicht mehr die einzigen Modell-IDs sind. Ohne explizite
# Steuerung lief daher bisher JEDE Anfrage (auch der "Chat"-Modus im Frontend)
# stillschweigend mit vollem Reasoning-Aufwand. Das Frontend sendet jetzt ein
# Feld thinking_enabled (bool); dieses Proxy-Skript setzt daraus den
# tatsaechlichen DeepSeek-API-Parameter:
#   thinking_enabled == True  -> {"thinking": {"type": "enabled"},
#                                 "reasoning_effort": "high"}
#   thinking_enabled == False -> {"thinking": {"type": "disabled"}}
# Quelle: https://api-docs.deepseek.com/guides/thinking_mode (Stand 28.08.2026)
#
# Quelle: https://api-docs.deepseek.com (Stand 11.05.2026)
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

def log_to_file(status_code, response_data, model=None, thinking=None):
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
        if model:
            log_line += f" | Model: {model}"
        # Fix (28.08.2026): Thinking-Mode-Status mitloggen, um serverseitig
        # verifizieren zu koennen, dass Chat/DeepThink tatsaechlich
        # unterschiedliche Reasoning-Parameter an die DeepSeek-API senden.
        if thinking is not None:
            log_line += f" | Thinking: {'enabled' if thinking else 'disabled'}"
        if error_msg:
            log_line += f" | Error: {error_msg}"
        log_line += "\n"
        with open(log_path, 'a') as f:
            f.write(log_line)
    except Exception:
        pass

def send_error(status_code, data, model=None):
    """Sendet Fehler-Response als JSON (vor dem Streaming-Start)."""
    print(f"Status: {status_code}")
    print("Content-Type: application/json")
    print(f"Access-Control-Allow-Origin: {ALLOWED_ORIGIN}")
    print("Access-Control-Allow-Methods: POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()
    print(json.dumps(data, ensure_ascii=False))
    sys.stdout.flush()
    log_to_file(status_code, data, model)

def main():
    model = None  # wird nach dem Parsen der Anfrage gesetzt, fuer Logging auch bei spaeteren Fehlern verfuegbar
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
        model = request_data.get('model', 'deepseek-v4-flash')  # ueberschreibt das None von oben
        messages = request_data.get('messages', [])
        max_tokens = request_data.get('max_tokens', 2000)
        no_training = request_data.get('no_training', True)
        # Fix (28.08.2026): siehe Kommentar am Dateianfang. False ist der
        # sichere Default, falls das Feld fehlt (z.B. aeltere Frontend-Version) -
        # damit verhaelt sich ein Client ohne dieses Feld wie "Chat"-Modus statt
        # unbemerkt mit vollem Reasoning-Aufwand zu laufen.
        thinking_enabled = bool(request_data.get('thinking_enabled', False))

        if not messages or not isinstance(messages, list):
            send_error(400, {
                'error': 'Ungueltige Anfrage: messages Array erforderlich'
            }, model)
            return

        # DeepSeek API Request vorbereiten (mit Streaming)
        api_url = 'https://api.deepseek.com/v1/chat/completions'

        api_request_data = {
            'model': model,
            'messages': messages,
            'max_tokens': max_tokens,
            'stream': True
        }

        # Fix (28.08.2026): Thinking-Mode explizit setzen statt den API-Default
        # (immer aktiv, High-Effort) unkontrolliert wirken zu lassen.
        if thinking_enabled:
            api_request_data['thinking'] = {'type': 'enabled'}
            api_request_data['reasoning_effort'] = 'high'
        else:
            api_request_data['thinking'] = {'type': 'disabled'}

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
                }, model)
            # HTTP 400: prüfen ob Kontextfenster überschritten
            elif e.code == 400:
                context_keywords = ['context', 'length', 'token', 'maximum']
                is_context = sum(1 for kw in context_keywords if kw.lower() in error_body.lower()) >= 2
                if is_context:
                    send_error(e.code, {
                        'error': f'DeepSeek API Fehler: {e.code}',
                        'error_type': 'context_exceeded',
                        'details': error_body
                    }, model)
                else:
                    send_error(e.code, {
                        'error': f'DeepSeek API Fehler: {e.code}',
                        'details': error_body
                    }, model)
            else:
                send_error(e.code, {
                    'error': f'DeepSeek API Fehler: {e.code}',
                    'details': error_body
                }, model)
            return
        except urllib.error.URLError as e:
            send_error(500, {
                'error': 'Verbindung zur DeepSeek API fehlgeschlagen',
                'details': str(e.reason)
            }, model)
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

        # Stream von DeepSeek direkt an den Client weiterleiten
        with response:
            for line in response:
                decoded = line.decode('utf-8')
                sys.stdout.write(decoded)
                sys.stdout.flush()

        log_to_file(200, {}, model, thinking_enabled)

    except json.JSONDecodeError as e:
        send_error(400, {
            'error': 'Ungültiges JSON',
            'details': str(e)
        }, model)

    except Exception as e:
        error_details = traceback.format_exc()
        send_error(500, {
            'error': 'Interner Serverfehler',
            'message': str(e),
            'details': error_details
        }, model)

if __name__ == '__main__':
    main()
