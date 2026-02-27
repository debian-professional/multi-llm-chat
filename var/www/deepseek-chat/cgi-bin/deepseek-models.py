#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deepseek-models.py - Query DeepSeek /v1/models endpoint
Returns available models as JSON
"""

import os
import sys
import json
import urllib.request
import urllib.error

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
MODELS_URL = 'https://api.deepseek.com/v1/models'

def log_to_file(message):
    try:
        log_path = os.path.join(os.path.dirname(__file__), 'deepseek-chat.log')
        with open(log_path, 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | models | {message}\n")
    except Exception:
        pass

def send_json(data, status=200):
    status_text = '200 OK' if status == 200 else f'{status} Error'
    print(f'Status: {status_text}')
    print('Content-Type: application/json')
    print('Access-Control-Allow-Origin: *')
    print()
    print(json.dumps(data))

try:
    if not DEEPSEEK_API_KEY:
        send_json({'error': 'API key not configured'}, 500)
        sys.exit(0)

    req = urllib.request.Request(
        MODELS_URL,
        headers={
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json',
        },
        method='GET'
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode('utf-8')
        data = json.loads(body)
        send_json(data)
        log_to_file('models fetched: ' + str([m.get('id') for m in data.get('data', [])]))

except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    log_to_file(f'HTTP error {e.code}: {body}')
    send_json({'error': f'HTTP {e.code}', 'details': body}, e.code)
except Exception as e:
    log_to_file(f'Exception: {str(e)}')
    send_json({'error': str(e)}, 500)
