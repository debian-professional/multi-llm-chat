#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys

# Absoluter Pfad zur Log-Datei
LOG_FILE_PATH = '/var/www/deepseek-chat/logs/multi-llm-chat.log'

# Sicherheits-Fix (26.07.2026): CORS-Wildcard "*" erlaubte jeder beliebigen
# Webseite (z.B. in einem anderen Tab desselben VPN-verbundenen Geraets),
# per Cross-Site-Request die kompletten Server-Logs auszulesen.
# Fix: nur die eigene Origin des Frontends darf zugreifen.
ALLOWED_ORIGIN = 'https://172.29.255.1'

# Header
print("Content-Type: text/plain; charset=utf-8")
print(f"Access-Control-Allow-Origin: {ALLOWED_ORIGIN}")
print()

try:
    # Prüfe ob die Datei existiert
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    if not os.path.exists(LOG_FILE_PATH):
        print(f"Log-Datei nicht gefunden unter: {LOG_FILE_PATH}")
        sys.exit(0)

    # Datei lesen
    with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        if content.strip():
            print(content, end='')
        else:
            print("Keine Log-Einträge vorhanden.")

except Exception as e:
    print(f"Fehler beim Lesen der Log-Datei: {str(e)}")





