#!/usr/bin/python3
# -*- coding: utf-8 -*-

# =============================================================================
# KOMPRESSOR — KONTEXT-KOMPRIMIERUNG
# Erstellt: 12.03.2026
# =============================================================================
#
# Empfaengt die aelteste Haelfte des contextHistory-Arrays (messages),
# schickt diese an LLM #2 (frei waehlbarer Anbieter) mit einem festen
# System-Prompt zur Zusammenfassung und gibt das Ergebnis als JSON zurueck:
#
#   { "summary": "<komprimierter Kontext als Text>" }
#
# Unterstuetzte Anbieter (compressorService):
#
#   deepseek    — DeepSeek API  (DEEPSEEK_API_KEY)
#   openai      — OpenAI API    (OPENAI_API_KEY)
#   google      — Gemini API    (GOOGLE_API_KEY)
#   huggingface — HF Router     (HF_API_KEY)
#   groq        — GroqCloud     (GRQ_API_KEY)
#
# Request-Format (POST, application/json):
#
#   {
#     "messages":          [ { "role": "...", "content": "..." }, ... ],
#     "compressorService": "deepseek" | "openai" | "google" | "huggingface" | "groq",
#     "compressorModel":   "<Modellname>"
#   }
#
# Response-Format (application/json):
#
#   { "summary": "<Text>" }
#
# Fehler-Response:
#
#   { "error": "<Meldung>", "details": "<Detail>" }
#
# Hinweis: Dieses Skript verwendet KEIN Streaming, da die vollstaendige
#          Zusammenfassung benoetigt wird, bevor contextHistory veraendert wird.
#
# =============================================================================

import json
import sys
import os
import traceback
import urllib.request
import urllib.error
import datetime

# =============================================================================
# SYSTEM-PROMPT FUER DIE KOMPRIMIERUNG
# =============================================================================
COMPRESS_SYSTEM_PROMPT = """You are a context compression assistant. Your task is to create a compact but complete summary of a conversation history.

Summarize the provided conversation in a structured format. Extract and preserve:
1. All key facts, data, and information exchanged
2. All decisions made and conclusions reached
3. All open questions and unresolved topics
4. Important context needed to continue the conversation coherently

Rules:
- Write in the same language as the conversation
- Be concise but complete — no important information must be lost
- Use a structured format with clear sections
- Do NOT add commentary or meta-information about the compression itself
- Output ONLY the summary, nothing else"""

COMPRESS_USER_TEMPLATE = "Please compress the following conversation history into a structured summary:\n\n{conversation}"


# =============================================================================
# LOGGING (identisch zu den anderen Proxy-Skripten)
# =============================================================================
def log_to_file(status_code, response_data):
    """Schreibt ausgewaehlte Informationen in die Log-Datei (ohne API-Key)."""
    try:
        if os.environ.get('REQUEST_METHOD') == 'OPTIONS':
            return
        log_path = '/var/www/deepseek-chat/cgi-bin/deepseek-chat.log'
        ip        = os.environ.get('REMOTE_ADDR', 'unknown')
        method    = os.environ.get('REQUEST_METHOD', 'unknown')
        path      = os.environ.get('REQUEST_URI', 'unknown')
        timestamp = datetime.datetime.now().isoformat()
        error_msg = None
        details   = None
        if isinstance(response_data, dict):
            error_msg = response_data.get('error')
            details   = response_data.get('details')
        log_line = f"{timestamp} | IP: {ip} | {method} {path} | Status: {status_code} | KOMPRESSOR"
        if error_msg:
            log_line += f" | Error: {error_msg}"
        if details:
            details_short = details[:300].replace('\n', ' ')
            log_line += f" | Details: {details_short}"
        log_line += "\n"
        with open(log_path, 'a') as f:
            f.write(log_line)
    except Exception:
        pass


# =============================================================================
# RESPONSE HELPERS
# =============================================================================
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


def send_success(summary):
    """Sendet Erfolgs-Response mit der Zusammenfassung."""
    print("Status: 200")
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()
    print(json.dumps({'summary': summary}, ensure_ascii=False))
    sys.stdout.flush()
    log_to_file(200, {})


# =============================================================================
# KONVERSATIONS-AUFBEREITUNG
# =============================================================================
def build_conversation_text(messages):
    """Wandelt das messages-Array in lesbaren Text um."""
    lines = []
    for msg in messages:
        role    = msg.get('role', 'user')
        content = msg.get('content', '')
        if not content:
            continue
        # Komprimierte System-Eintraege ueberspringen (wuerden rekursiv komprimiert)
        if role == 'system' and str(content).startswith('[COMPRESSED CONTEXT]'):
            lines.append(f"[Previously compressed context]:\n{content}")
            continue
        if role == 'system':
            lines.append(f"[System]: {content}")
        elif role == 'assistant':
            lines.append(f"[Assistant]: {content}")
        else:
            lines.append(f"[User]: {content}")
    return "\n\n".join(lines)


# =============================================================================
# API-AUFRUFE (nicht-streamend, alle 5 Anbieter)
# =============================================================================

def call_openai_compatible(api_url, api_key, model, compress_messages, extra_headers=None):
    """
    Ruft eine OpenAI-kompatible API nicht-streamend auf.
    Funktioniert fuer: OpenAI, DeepSeek, GroqCloud, Hugging Face.
    Gibt den Antworttext als String zurueck.
    """
    api_request_data = {
        'model':      model,
        'messages':   compress_messages,
        'max_tokens': 2000,
        'stream':     False
    }

    headers = {
        'Content-Type':  'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    if extra_headers:
        headers.update(extra_headers)

    req = urllib.request.Request(
        api_url,
        data=json.dumps(api_request_data).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    try:
        response = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise RuntimeError(f"API HTTP-Fehler {e.code}: {error_body[:300]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Verbindungsfehler: {e.reason}")

    response_body = response.read().decode('utf-8')
    data = json.loads(response_body)

    # Antworttext extrahieren
    choices = data.get('choices', [])
    if not choices:
        raise RuntimeError(f"Leere choices in API-Antwort: {response_body[:200]}")
    message = choices[0].get('message', {})
    text = message.get('content', '')
    if not text:
        raise RuntimeError(f"Kein content in API-Antwort: {response_body[:200]}")
    return text


def call_google(api_key, model, compress_messages):
    """
    Ruft die Google Gemini API nicht-streamend auf.
    Gibt den Antworttext als String zurueck.
    """
    # System-Message und Contents trennen
    system_instruction = None
    contents = []
    for msg in compress_messages:
        role    = msg.get('role', 'user')
        content = msg.get('content', '')
        if role == 'system':
            system_instruction = content
        elif role == 'assistant':
            contents.append({'role': 'model', 'parts': [{'text': content}]})
        else:
            contents.append({'role': 'user', 'parts': [{'text': content}]})

    # Fallback: leere contents verhindern
    if not contents:
        contents.append({'role': 'user', 'parts': [{'text': '(no content)'}]})

    api_url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'

    api_request_data = {
        'contents': contents,
        'generationConfig': {
            'maxOutputTokens': 2000
        }
    }
    if system_instruction:
        api_request_data['system_instruction'] = {
            'parts': [{'text': system_instruction}]
        }

    headers = {'Content-Type': 'application/json'}

    req = urllib.request.Request(
        api_url,
        data=json.dumps(api_request_data).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    try:
        response = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise RuntimeError(f"Gemini API HTTP-Fehler {e.code}: {error_body[:300]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Verbindungsfehler: {e.reason}")

    response_body = response.read().decode('utf-8')
    data = json.loads(response_body)

    candidates = data.get('candidates', [])
    if not candidates:
        raise RuntimeError(f"Leere candidates in Gemini-Antwort: {response_body[:200]}")
    parts = candidates[0].get('content', {}).get('parts', [])
    if not parts:
        raise RuntimeError(f"Keine parts in Gemini-Antwort: {response_body[:200]}")
    text = parts[0].get('text', '')
    if not text:
        raise RuntimeError(f"Kein text in Gemini-Antwort: {response_body[:200]}")
    return text


# =============================================================================
# MAIN
# =============================================================================
def main():
    try:
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
                'error': 'Leere Anfrage. Bitte messages, compressorService und compressorModel senden.'
            })
            return

        # POST-Daten lesen
        post_data    = sys.stdin.read(content_length)
        request_data = json.loads(post_data)

        # Parameter validieren
        messages           = request_data.get('messages', [])
        compressor_service = request_data.get('compressorService', 'deepseek')
        compressor_model   = request_data.get('compressorModel', 'deepseek-chat')

        if not messages or not isinstance(messages, list):
            send_error(400, {
                'error': 'Ungueltige Anfrage: messages Array erforderlich'
            })
            return

        if len(messages) < 2:
            send_error(400, {
                'error': 'Zu wenig Nachrichten zum Komprimieren (mindestens 2 erforderlich).'
            })
            return

        # Konversationstext aufbauen
        conversation_text = build_conversation_text(messages)
        if not conversation_text.strip():
            send_error(400, {
                'error': 'Keine komprimierbaren Inhalte in den messages gefunden.'
            })
            return

        # Komprimierungs-Messages fuer LLM #2 zusammenstellen
        # HINWEIS: replace() statt format() — conversation_text kann
        # geschweifte Klammern enthalten (JSON, Code etc.)
        user_content = COMPRESS_USER_TEMPLATE.replace('{conversation}', conversation_text)
        compress_messages = [
            {'role': 'system',  'content': COMPRESS_SYSTEM_PROMPT},
            {'role': 'user',    'content': user_content}
        ]

        # API-Aufruf je nach Anbieter
        summary = ''

        if compressor_service == 'deepseek':
            api_key = os.environ.get('DEEPSEEK_API_KEY')
            if not api_key:
                send_error(500, {
                    'error': 'DEEPSEEK_API_KEY nicht konfiguriert in /etc/apache2/envvars.'
                })
                return
            summary = call_openai_compatible(
                api_url  = 'https://api.deepseek.com/v1/chat/completions',
                api_key  = api_key,
                model    = compressor_model,
                compress_messages = compress_messages
            )

        elif compressor_service == 'openai':
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                send_error(500, {
                    'error': 'OPENAI_API_KEY nicht konfiguriert in /etc/apache2/envvars.'
                })
                return
            summary = call_openai_compatible(
                api_url  = 'https://api.openai.com/v1/chat/completions',
                api_key  = api_key,
                model    = compressor_model,
                compress_messages = compress_messages,
                extra_headers = {'User-Agent': 'Mozilla/5.0 (compatible; kompressor/1.0)'}
            )

        elif compressor_service == 'google':
            api_key = os.environ.get('GOOGLE_API_KEY')
            if not api_key:
                send_error(500, {
                    'error': 'GOOGLE_API_KEY nicht konfiguriert in /etc/apache2/envvars.'
                })
                return
            summary = call_google(
                api_key = api_key,
                model   = compressor_model,
                compress_messages = compress_messages
            )

        elif compressor_service == 'huggingface':
            api_key = os.environ.get('HF_API_KEY')
            if not api_key:
                send_error(500, {
                    'error': 'HF_API_KEY nicht konfiguriert in /etc/apache2/envvars.'
                })
                return
            summary = call_openai_compatible(
                api_url  = 'https://router.huggingface.co/v1/chat/completions',
                api_key  = api_key,
                model    = compressor_model,
                compress_messages = compress_messages
            )

        elif compressor_service == 'groq':
            api_key = os.environ.get('GRQ_API_KEY')
            if not api_key:
                send_error(500, {
                    'error': 'GRQ_API_KEY nicht konfiguriert in /etc/apache2/envvars.'
                })
                return
            summary = call_openai_compatible(
                api_url  = 'https://api.groq.com/openai/v1/chat/completions',
                api_key  = api_key,
                model    = compressor_model,
                compress_messages = compress_messages,
                extra_headers = {'User-Agent': 'Mozilla/5.0 (compatible; kompressor/1.0)'}
            )

        else:
            send_error(400, {
                'error': f'Unbekannter compressorService: {compressor_service}. '
                         f'Erlaubt: deepseek, openai, google, huggingface, groq'
            })
            return

        # Erfolg
        send_success(summary.strip())

    except json.JSONDecodeError as e:
        send_error(400, {
            'error': 'Ungültiges JSON',
            'details': str(e)
        })

    except RuntimeError as e:
        send_error(502, {
            'error': 'LLM-Aufruf fehlgeschlagen',
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
