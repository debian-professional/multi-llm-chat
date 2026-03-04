#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
        log_path = '/var/www/deepseek-chat/cgi-bin/deepseek-chat.log'
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
        api_key = os.environ.get('HF_API_KEY')
        if not api_key:
            send_error(500, {
                'error': 'API-Key nicht konfiguriert. Bitte HF_API_KEY in /etc/apache2/envvars setzen.'
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
        model = request_data.get('model', 'Qwen/Qwen2.5-72B-Instruct')
        messages = request_data.get('messages', [])
        max_tokens = request_data.get('max_tokens', 2000)

        if not messages or not isinstance(messages, list):
            send_error(400, {
                'error': 'Ungueltige Anfrage: messages Array erforderlich'
            })
            return

        # Hugging Face Serverless Inference API — OpenAI-kompatibler Endpunkt
        
        api_url = f'https://router.huggingface.co/v1/chat/completions'

        api_request_data = {
            'model':      model,
            'messages':   messages,
            'max_tokens': max_tokens,
            'stream':     True
        }

        headers = {
            'Content-Type':  'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        req = urllib.request.Request(
            api_url,
            data=json.dumps(api_request_data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        # API-Verbindung herstellen (VOR dem Senden der SSE-Header)
        try:
            response = urllib.request.urlopen(req, timeout=120)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            send_error(e.code, {
                'error': f'Hugging Face API Fehler: {e.code}',
                'details': error_body
            })
            return
        except urllib.error.URLError as e:
            send_error(500, {
                'error': 'Verbindung zur Hugging Face API fehlgeschlagen',
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

        # HF gibt OpenAI-kompatibles SSE-Format zurück — direkt weiterleiten
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
                            # HF gibt exakt das OpenAI-Format zurück
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
