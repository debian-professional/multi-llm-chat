############ FILE: var/www/deepseek-chat/cgi-bin/groq-api.py ############
---------------------------------------------------------
#!/usr/bin/python3
# -*- coding: utf-8 -*-

# =============================================================================
# GROQCLOUD API PROXY
# Importiert / aktualisiert: 08.03.2026
# =============================================================================
#
# Unterstuetzte Modelle:
#
#   --- FREE PLAN ---
#
#   llama-3.3-70b-versatile  [Free + Paid]
#     Version      : Llama 3.3 70B Versatile (Stand 08.03.2026)
#     Kontext      : 128.000 Token Input / 8.192 Token Output
#     Faehigkeiten : Nur Text (kein Bild, kein Audio, kein Video)
#
#   llama-3.1-8b-instant  [Free + Paid]
#     Version      : Llama 3.1 8B Instant (Stand 08.03.2026)
#     Kontext      : 131.072 Token Input / 8.192 Token Output
#     Faehigkeiten : Nur Text (kein Bild, kein Audio, kein Video)
#
#   mixtral-8x7b-32768  [Free + Paid]
#     Version      : Mixtral 8x7B Instruct v0.1 (Stand 08.03.2026)
#     Kontext      : 32.768 Token Input / 32.768 Token Output
#     Faehigkeiten : Nur Text (kein Bild, kein Audio, kein Video)
#
#   gemma2-9b-it  [Free + Paid]
#     Version      : Gemma 2 9B IT (Stand 08.03.2026)
#     Kontext      : 8.192 Token Input / 8.192 Token Output
#     Faehigkeiten : Nur Text (kein Bild, kein Audio, kein Video)
#
# Hinweis: Alle Groq-Modelle profitieren von Hardware-beschleunigter Inferenz
#          (LPU - Language Processing Unit) fuer sehr geringe Latenz.
#
# Quelle: https://console.groq.com/docs/models (Stand 08.03.2026)
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

def main():
    try:
        # API-Key aus Umgebungsvariable laden
        api_key = os.environ.get('GRQ_API_KEY')
        if not api_key:
            send_error(500, {
                'error': 'API-Key nicht konfiguriert. Bitte GRQ_API_KEY in /etc/apache2/envvars setzen.'
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
        model = request_data.get('model', 'llama-3.3-70b-versatile')
        messages = request_data.get('messages', [])
        max_tokens = request_data.get('max_tokens', 2000)

        if not messages or not isinstance(messages, list):
            send_error(400, {
                'error': 'Ungueltige Anfrage: messages Array erforderlich'
            })
            return

        # GroqCloud API — OpenAI-kompatibler Endpunkt
        api_url = 'https://api.groq.com/openai/v1/chat/completions'

        api_request_data = {
            'model':      model,
            'messages':   messages,
            'max_tokens': max_tokens,
            'stream':     True
        }

        headers = {
            'Content-Type':  'application/json',
            'Authorization': f'Bearer {api_key}',
            'User-Agent':    'Mozilla/5.0 (compatible; groq-proxy/1.0)'
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
            # HTTP 429: GroqCloud Free Tier Limit erreicht
            if e.code == 429:
                send_error(e.code, {
                    'error': f'GroqCloud API Fehler: {e.code}',
                    'error_type': 'daily_limit',
                    'details': error_body
                })
            else:
                # HTTP 400: prüfen ob Kontextfenster überschritten
                if e.code == 400:
                    try:
                        error_json = json.loads(error_body)
                        error_code = error_json.get('error', {}).get('code', '')
                        if error_code == 'context_length_exceeded' or 'context_length_exceeded' in error_body:
                            send_error(e.code, {
                                'error': f'GroqCloud API Fehler: {e.code}',
                                'error_type': 'context_exceeded',
                                'details': error_body
                            })
                            return
                    except Exception:
                        context_keywords = ['context', 'length', 'token', 'maximum']
                        if sum(1 for kw in context_keywords if kw.lower() in error_body.lower()) >= 2:
                            send_error(e.code, {
                                'error': f'GroqCloud API Fehler: {e.code}',
                                'error_type': 'context_exceeded',
                                'details': error_body
                            })
                            return
                send_error(e.code, {
                    'error': f'GroqCloud API Fehler: {e.code}',
                    'details': error_body
                })
            return
        except urllib.error.URLError as e:
            send_error(500, {
                'error': 'Verbindung zur GroqCloud API fehlgeschlagen',
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

        # Groq gibt OpenAI-kompatibles SSE-Format zurück — direkt weiterleiten
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
                            # Groq gibt exakt das OpenAI-Format zurück
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






FILE: var/www/deepseek-chat/cgi-bin/export-pdf.py
---------------------------------------------------------
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import sys
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def send_response(status_code, data, content_type='application/json'):
    """Sendet HTTP-Response zurück."""
    if isinstance(data, bytes):
        # Für Binärdaten: alles über stdout.buffer schreiben
        headers = f"Status: {status_code}\r\n"



