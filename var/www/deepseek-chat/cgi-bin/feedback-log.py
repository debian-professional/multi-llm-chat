#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
feedback-log.py - Schreibt Like/Dislike Feedback in multi-llm-chat.log
/var/www/deepseek-chat/cgi-bin/feedback-log.py
"""

import sys
import json
import os
from datetime import datetime

LOG_PATH = '/var/www/deepseek-chat/logs/multi-llm-chat.log'

# Sicherheits-Fix (26.07.2026): CORS-Wildcard durch feste Origin ersetzt,
# zusaetzlich Request-Groessenlimit (Payload ist per Design winzig: Typ,
# msgId, max. 60 Zeichen Vorschau).
ALLOWED_ORIGIN = 'https://172.29.255.1'
MAX_REQUEST_SIZE = 64 * 1024  # 64 KB

def send_response(status_code, data):
    print(f"Status: {status_code}")
    print("Content-Type: application/json")
    print(f"Access-Control-Allow-Origin: {ALLOWED_ORIGIN}")
    print()
    print(json.dumps(data, ensure_ascii=False))
    sys.stdout.flush()

def main():
    try:
        if os.environ.get('REQUEST_METHOD') != 'POST':
            send_response(405, {"error": "Nur POST erlaubt"})
            return

        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        if content_length > MAX_REQUEST_SIZE:
            send_response(413, {"error": f"Anfrage zu gross (max. {MAX_REQUEST_SIZE // 1024} KB)"})
            return
        raw_data = sys.stdin.buffer.read(content_length)
        data = json.loads(raw_data.decode('utf-8'))

        feedback_type = data.get('type', '').upper()   # LIKE oder DISLIKE
        msg_id = data.get('msgId', 'unknown')
        preview = data.get('preview', '')[:60]          # Erste 60 Zeichen der Nachricht
        ip = os.environ.get('REMOTE_ADDR', 'unknown')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if feedback_type not in ('LIKE', 'DISLIKE'):
            send_response(400, {"error": "Ungueltiger Feedback-Typ"})
            return

        log_line = f"{timestamp} | IP: {ip} | FEEDBACK | {feedback_type} | msgId: {msg_id} | \"{preview}\"\n"

        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(log_line)

        send_response(200, {"status": "ok", "logged": feedback_type})

    except Exception as e:
        send_response(500, {"error": str(e)})

if __name__ == '__main__':
    main()



