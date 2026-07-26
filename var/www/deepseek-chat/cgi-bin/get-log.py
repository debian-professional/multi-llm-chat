#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from collections import deque

# Absoluter Pfad zur Log-Datei
LOG_FILE_PATH = '/var/www/deepseek-chat/logs/multi-llm-chat.log'

# Sicherheits-Fix (26.07.2026): CORS-Wildcard "*" erlaubte jeder beliebigen
# Webseite (z.B. in einem anderen Tab desselben VPN-verbundenen Geraets),
# per Cross-Site-Request die kompletten Server-Logs auszulesen.
# Fix: nur die eigene Origin des Frontends darf zugreifen.
ALLOWED_ORIGIN = 'https://172.29.255.1'

# Sicherheits-Fix Stufe 3 (26.07.2026): bisher wurde die komplette Log-Datei
# ungefiltert zurueckgegeben, was bei langer Laufzeit unnoetig viele
# (potenziell sensible) historische Eintraege preisgibt. Jetzt werden nur
# noch die letzten MAX_LOG_LINES Zeilen ausgegeben.
MAX_LOG_LINES = 300

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

    # Datei zeilenweise lesen, dabei nur die letzten MAX_LOG_LINES Zeilen
    # im Speicher behalten (deque verwirft aeltere Zeilen automatisch)
    with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
        last_lines = deque(f, maxlen=MAX_LOG_LINES)

    if last_lines:
        print(f"[Anzeige begrenzt auf die letzten {MAX_LOG_LINES} Zeilen]\n")
        print(''.join(last_lines), end='')
    else:
        print("Keine Log-Einträge vorhanden.")

except Exception as e:
    print(f"Fehler beim Lesen der Log-Datei: {str(e)}")





