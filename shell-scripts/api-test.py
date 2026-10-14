#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api-test.py - Testet die Provider-APIs von multi-llm-chat mit denselben
Parametern, die die CGI-Proxys senden (Stand 12.10.2026).

Liest die Modelllisten und Output-Limits direkt aus index.html
(MODEL_CONFIG, *_MODELS, MODEL_CAPABILITIES, AUDIO_CAPABLE_MODELS), damit
getestet wird, was die App wirklich anbietet.

Tests:
  0  Verfuegbarkeit  : Modell-ID in der Modellliste des Anbieters
  A  Text            : kurze Frage, max. Output-Tokens = Wert aus MODEL_CONFIG
  B  Bild            : 64x64-Rot-PNG (nur Modelle mit images:true)
  C  Audio           : 0,5 s Sinuston als WAV (nur Modelle aus AUDIO_CAPABLE_MODELS
                       sowie gpt-4.1 als Gegenprobe); mit ffmpeg zusaetzlich WebM,
                       das ist das Format, das der Browser tatsaechlich sendet
  D  DeepThink       : DeepSeek mit thinking enabled / reasoning_effort high
  E  Alias           : deepseek-v4-flash (abgeloester Alias) wird noch angenommen

Ablage: shell-scripts/api-test.py im Repo (NICHT in cgi-bin - wird von
deploy.sh nicht nach Produktion kopiert und ist kein Web-Skript).

Aufruf (auf swtor10, als root, damit /etc/apache2/envvars lesbar ist; aus dem
Repo-Verzeichnis oder mit vollem Pfad):
  sudo python3 shell-scripts/api-test.py                 # alle Anbieter
  sudo python3 shell-scripts/api-test.py google openai   # nur bestimmte Anbieter
  sudo python3 shell-scripts/api-test.py --no-media      # nur Test 0, A, D, E
  sudo python3 shell-scripts/api-test.py --dry           # nur anzeigen, was getestet wuerde
  sudo python3 shell-scripts/api-test.py groq hf --list  # verfuegbare Modell-IDs des Anbieters auflisten
  --html=PFAD   andere index.html verwenden (Standard: Produktion)
  --timeout=SEK Wartezeit je Anfrage in Sekunden (Standard 120, erlaubt 5-600); bei langsamen
                Anbietern (z. B. Google-Ueberlast) kuerzer waehlen, z. B. --timeout=30.
                Ein Timeout wird als WARN gemeldet (HTTP 0), nicht als FAIL.
Waehrend einer laufenden Anfrage zeigt das Terminal eine Zeile "... wartet auf <Anbieter Modell
Test>" (nur bei interaktiver Ausgabe, nicht beim Umleiten in eine Datei).

Host-Schutz (seit 14.10.2026): Das Skript laeuft NUR auf dem Server, auf dem multi-llm-chat
betrieben wird, und bricht sonst vor jeder Anfrage mit einer Fehlermeldung ab (Exit-Code 2):
  - Apache2 muss installiert sein (apache2 / apache2ctl),
  - die Produktion /var/www/deepseek-chat (index.html und cgi-bin) muss vorhanden sein,
  - /etc/apache2/envvars muss existieren und lesbar sein (als root starten),
  - die API-Keys der gewaehlten Anbieter muessen dort gesetzt und plausibel sein (nicht leer,
    kein Platzhalter, mindestens 16 Zeichen). Keys aus Umgebungsvariablen werden NICHT verwendet.
Das gilt fuer alle Betriebsarten (auch --dry, --list, --html=). Ob ein Key beim Anbieter gueltig
ist, zeigen die Tests selbst (HTTP 401/403 = FAIL).

Einstufung: FAIL = Konfiguration/Anfrage fehlerhaft. WARN bei HTTP 402/429/503 oder
Timeout = Konto-/Anbieterproblem (Guthaben leer, Kontingent, Ueberlast); die Konfiguration
ist dann weder bestaetigt noch widerlegt - spaeter wiederholen.

Kosten: wenige Cent. Es werden keine API-Keys ausgegeben.
"""

import base64
import io
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import wave
import zlib

PROD_DIR = '/var/www/deepseek-chat'
HTML_PATH = PROD_DIR + '/index.html'
ENVVARS = '/etc/apache2/envvars'
APACHE_BINARIES = ('/usr/sbin/apache2', '/usr/sbin/apache2ctl')
MIN_KEY_LEN = 16
TIMEOUT = 120

PROVIDERS = {
    'deepseek': dict(key='DEEPSEEK_API_KEY', lists=['DEEPSEEK_MODELS']),
    'openai':   dict(key='OPENAI_API_KEY',   lists=['OPENAI_MODELS_FREE', 'OPENAI_MODELS_PAID']),
    'google':   dict(key='GOOGLE_API_KEY',   lists=['GOOGLE_MODELS_FREE', 'GOOGLE_MODELS_PAID']),
    'groq':     dict(key='GRQ_API_KEY',      lists=['GROQ_MODELS_FREE', 'GROQ_MODELS_PAID']),
    'hf':       dict(key='HF_API_KEY',       lists=['HF_MODELS_FREE', 'HF_MODELS_PAID']),
}

# ----------------------------------------------------------------------------
# Hilfsfunktionen
# ----------------------------------------------------------------------------
def load_keys():
    """Liest die API-Keys NUR aus /etc/apache2/envvars (wie die CGI-Proxys). Umgebungsvariablen
    werden bewusst nicht beruecksichtigt, damit das Skript nicht auf fremden Rechnern laeuft."""
    keys = {}
    try:
        with open(ENVVARS, encoding='utf-8') as f:
            for line in f:
                m = re.match(r'\s*(?:export\s+)?([A-Z_]+_API_KEY)\s*=\s*(.*?)\s*$', line)
                if m and m.group(1) not in keys:
                    v = m.group(2).strip().strip('"').strip("'")
                    if v:
                        keys[m.group(1)] = v
    except OSError:
        pass  # check_host() meldet das mit einer verstaendlichen Fehlermeldung
    return keys


def default_html():
    """index.html der Produktion (der Host-Schutz stellt sicher, dass sie existiert)."""
    return HTML_PATH


def key_problem(name, value):
    """Gibt einen Fehlertext zurueck, wenn der Key fehlt oder nicht plausibel ist, sonst None."""
    if not value:
        return f'{name} ist in {ENVVARS} nicht gesetzt'
    if re.search(r'\s', value):
        return f'{name} enthaelt Leerzeichen'
    if len(value) < MIN_KEY_LEN or re.search(
            r'your|change|dummy|example|placeholder|xxxx|todo|<|>|\.\.\.', value, re.I):
        return f'{name} ist leer, zu kurz oder ein Platzhalter'
    return None


def check_host(providers, keys):
    """Prueft, ob das Skript auf dem richtigen Host laeuft. Gibt eine Liste von Problemen zurueck
    (leer = alles in Ordnung)."""
    problems = []
    if not (any(os.access(p, os.X_OK) for p in APACHE_BINARIES) or shutil.which('apache2')
            or shutil.which('apache2ctl')):
        problems.append('Apache2 ist auf diesem Rechner nicht installiert.')
    if not (os.path.isfile(HTML_PATH) and os.path.isdir(PROD_DIR + '/cgi-bin')):
        problems.append(f'Die Produktion {PROD_DIR} (index.html, cgi-bin) ist nicht vorhanden.')
    if not os.path.isfile(ENVVARS):
        problems.append(f'{ENVVARS} existiert nicht (dort stehen die API-Keys).')
    elif not os.access(ENVVARS, os.R_OK):
        problems.append(f'{ENVVARS} ist nicht lesbar - als root starten (sudo).')
    else:
        for p in providers:
            name = PROVIDERS[p]['key']
            err = key_problem(name, keys.get(name, ''))
            if err:
                problems.append(f'{p}: {err}.')
    return problems


def require_host(providers):
    """Bricht mit Exit-Code 2 ab, wenn der Host nicht stimmt. Gibt sonst die Keys zurueck."""
    keys = load_keys()
    problems = check_host(providers, keys)
    if problems:
        print('ABBRUCH: api-test.py darf nur auf dem Server laufen, auf dem multi-llm-chat '
              'betrieben wird (Apache2 installiert, Produktion vorhanden, gueltige API-Keys '
              f'in {ENVVARS}).', file=sys.stderr)
        for pr in problems:
            print('  - ' + pr, file=sys.stderr)
        print('Es wurde keine Anfrage an einen Anbieter gesendet.', file=sys.stderr)
        sys.exit(2)
    return keys


def parse_html(path):
    s = open(path, encoding='utf-8').read()
    cfg = {m.group(1): int(m.group(3)) for m in re.finditer(
        r"'([^']+)':\s*\{\s*maxContextTokens:\s*(\d+),\s*maxOutputTokens:\s*(\d+)", s)}
    caps = {m.group(1): (m.group(2) == 'true') for m in re.finditer(
        r"'([^']+)':\s*\{\s*images:\s*(true|false)", s)}
    lists = {}
    for m in re.finditer(r"const\s+([A-Z_]+_MODELS(?:_FREE|_PAID)?|AUDIO_CAPABLE_MODELS)\s*=\s*\[(.*?)\]", s, re.S):
        lists[m.group(1)] = re.findall(r"'([^']+)'", m.group(2))
    return cfg, caps, lists


def make_png():
    w = h = 64  # Groq verlangt mind. 32x32 Pixel
    raw = b''.join(b'\x00' + b'\xff\x00\x00' * w for _ in range(h))
    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def make_wav():
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b''.join(struct.pack('<h', int(12000 * math.sin(2 * math.pi * 440 * i / 16000)))
                               for i in range(8000)))
    return buf.getvalue()


def make_webm(wav_bytes):
    """Mit ffmpeg WebM/Opus erzeugen (Format der Browser-Aufnahme). None, falls kein ffmpeg."""
    if not shutil.which('ffmpeg'):
        return None
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, 'a.wav'), os.path.join(d, 'a.webm')
        open(src, 'wb').write(wav_bytes)
        r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-c:a', 'libopus', dst],
                           capture_output=True)
        if r.returncode != 0 or not os.path.exists(dst):
            return None
        return open(dst, 'rb').read()


def http(url, payload=None, headers=None, method=None, label=None):
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method or ('POST' if data else 'GET'))
    t0 = time.time()
    show = bool(label) and sys.stdout.isatty()
    if show:  # Wartehinweis, damit ein langsamer Anbieter nicht wie ein Haenger aussieht
        sys.stdout.write(f'      ... wartet auf {label} (max. {TIMEOUT}s)')
        sys.stdout.flush()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read().decode('utf-8', 'replace')
            return r.status, body, time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace'), time.time() - t0
    except Exception as e:
        return 0, str(e), time.time() - t0
    finally:
        if show:
            sys.stdout.write('\r\033[K')
            sys.stdout.flush()


def bad(st):
    """FAIL, ausser bei Konto-/Anbieterproblemen (Guthaben, Kontingent, Ueberlast, Timeout):
    dann WARN - die App-Konfiguration ist damit weder bestaetigt noch widerlegt."""
    return 'WARN' if st in (0, 402, 429, 503) else 'FAIL'


def clean(text, keys, n=150):
    for k in keys.values():
        if k:
            text = text.replace(k, '***')
    return re.sub(r'\s+', ' ', text)[:n]


# ----------------------------------------------------------------------------
# Anfrage-Bauer je Anbieter (identisch zu den CGI-Proxys, nur ohne Streaming)
# ----------------------------------------------------------------------------
def build(provider, model, key, prompt, max_out, image=None, audio=None, deepthink=None):
    """Liefert (url, headers, payload)."""
    if provider == 'google':
        parts = [{'text': prompt}]
        if image:
            parts.append({'inline_data': {'mime_type': 'image/png', 'data': image}})
        if audio:
            parts.append({'inline_data': {'mime_type': audio[1], 'data': audio[0]}})
        return (f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                {'Content-Type': 'application/json', 'x-goog-api-key': key},
                {'contents': [{'role': 'user', 'parts': parts}],
                 'generationConfig': {'maxOutputTokens': max_out}})
    content = prompt
    if image or audio:
        content = [{'type': 'text', 'text': prompt}]
        if audio:
            content.append({'type': 'input_audio', 'input_audio': {'data': audio[0], 'format': audio[2]}})
        if image:
            content.append({'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + image}})
    payload = {'model': model, 'messages': [{'role': 'user', 'content': content}]}
    h = {'Content-Type': 'application/json', 'Authorization': f'Bearer {key}',
         'User-Agent': 'Mozilla/5.0 (compatible; api-test/1.0)'}
    if provider == 'openai':
        payload['max_completion_tokens'] = max_out
        return 'https://api.openai.com/v1/chat/completions', h, payload
    payload['max_tokens'] = max_out
    if provider == 'deepseek':
        if deepthink:
            payload['thinking'] = {'type': 'enabled'}
            payload['reasoning_effort'] = 'high'
        else:
            payload['thinking'] = {'type': 'disabled'}
        return 'https://api.deepseek.com/v1/chat/completions', h, payload
    if provider == 'groq':
        return 'https://api.groq.com/openai/v1/chat/completions', h, payload
    return 'https://router.huggingface.co/v1/chat/completions', h, payload


def parse_reply(provider, status, body):
    """-> (ok, text, info)"""
    try:
        j = json.loads(body)
    except Exception:
        return False, '', body[:150]
    if status != 200:
        err = j.get('error', j)
        msg = err.get('message') if isinstance(err, dict) else str(err)
        return False, '', msg or body[:150]
    if provider == 'google':
        c = (j.get('candidates') or [{}])[0]
        txt = ''.join(p.get('text', '') for p in c.get('content', {}).get('parts', []))
        u = j.get('usageMetadata', {})
        info = f"finish={c.get('finishReason')} out={u.get('candidatesTokenCount')} think={u.get('thoughtsTokenCount', 0)}"
    else:
        c = (j.get('choices') or [{}])[0]
        txt = (c.get('message') or {}).get('content') or ''
        u = j.get('usage', {})
        info = f"finish={c.get('finish_reason')} out={u.get('completion_tokens')}"
    return bool(txt.strip()), txt.strip(), info


# ----------------------------------------------------------------------------
# Hauptprogramm
# ----------------------------------------------------------------------------
def list_models(provider, key, keys):
    """Gibt die vom Anbieter gemeldeten Modell-IDs aus (ohne Tests, ohne Keys)."""
    if provider == 'google':
        st, body, _ = http('https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000',
                           headers={'x-goog-api-key': key})
        if st != 200:
            print(f'FAIL  HTTP {st}: {clean(body, keys)}')
            return
        ids = sorted(m['name'].split('/', 1)[1] for m in json.loads(body).get('models', [])
                     if 'generateContent' in m.get('supportedGenerationMethods', []))
    else:
        url = {'deepseek': 'https://api.deepseek.com/v1/models',
               'openai': 'https://api.openai.com/v1/models',
               'groq': 'https://api.groq.com/openai/v1/models',
               'hf': 'https://router.huggingface.co/v1/models'}[provider]
        st, body, _ = http(url, headers={'Authorization': f'Bearer {key}',
                                         'User-Agent': 'Mozilla/5.0 (compatible; api-test/1.0)'})
        if st != 200:
            print(f'FAIL  HTTP {st}: {clean(body, keys)}')
            return
        try:
            ids = sorted(m['id'] for m in json.loads(body).get('data', []))
        except Exception:
            print('FAIL  Antwort nicht lesbar')
            return
    print(f'{len(ids)} Modelle:')
    for i in ids:
        print('  ' + i)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry' in sys.argv
    no_media = '--no-media' in sys.argv
    todo = [p for p in PROVIDERS if not args or p in args]
    keys = require_host(todo)  # bricht ab, wenn Host/Apache2/Keys nicht stimmen
    global TIMEOUT
    for a in sys.argv[1:]:
        if a.startswith('--timeout='):
            try:
                TIMEOUT = int(a.split('=', 1)[1])
                if not 5 <= TIMEOUT <= 600:
                    raise ValueError
            except ValueError:
                print('FEHLER: --timeout=SEK erwartet eine ganze Zahl von 5 bis 600.', file=sys.stderr)
                sys.exit(2)
    html = default_html()
    for a in sys.argv[1:]:
        if a.startswith('--html='):
            html = a.split('=', 1)[1]
    cfg, caps, lists = parse_html(html)

    if '--list' in sys.argv:
        for p in todo:
            key = keys.get(PROVIDERS[p]['key'], '')
            print(f'\n=== {p.upper()} ===')
            if not key:
                print(f"FAIL  {PROVIDERS[p]['key']} nicht gefunden")
                continue
            list_models(p, key, keys)
        return

    png = base64.b64encode(make_png()).decode()
    wav_b = make_wav()
    wav = base64.b64encode(wav_b).decode()
    webm_b = make_webm(wav_b)
    webm = base64.b64encode(webm_b).decode() if webm_b else None

    results = []  # (provider, model, test, status, detail)

    def add(p, m, t, st, d):
        results.append((p, m, t, st, d))
        print(f'{st:5} {p:8} {m:42} {t:12} {d}', flush=True)

    audio_models = set(lists.get('AUDIO_CAPABLE_MODELS', [])) | {'gpt-4.1'}

    for p in todo:
        spec = PROVIDERS[p]
        models = []
        for ln in spec['lists']:
            for m in lists.get(ln, []):
                if m not in models:
                    models.append(m)
        if not models:
            add(p, '-', 'config', 'FAIL', 'keine Modelle in index.html gefunden')
            continue
        key = keys.get(spec['key'], '')
        if not key and not dry:
            add(p, '-', 'config', 'FAIL', f"{spec['key']} nicht gefunden")
            continue
        print(f'\n=== {p.upper()} ({len(models)} Modelle) ===', flush=True)

        # Test 0: Verfuegbarkeit
        avail = None
        if not dry:
            if p == 'google':
                st, body, _ = http('https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000',
                                   headers={'x-goog-api-key': key})
                if st == 200:
                    avail = {m['name'].split('/', 1)[1] for m in json.loads(body).get('models', [])}
            else:
                url = {'deepseek': 'https://api.deepseek.com/v1/models',
                       'openai': 'https://api.openai.com/v1/models',
                       'groq': 'https://api.groq.com/openai/v1/models',
                       'hf': 'https://router.huggingface.co/v1/models'}[p]
                st, body, _ = http(url, headers={'Authorization': f'Bearer {key}',
                                                 'User-Agent': 'Mozilla/5.0 (compatible; api-test/1.0)'})
                if st == 200:
                    try:
                        avail = {m['id'] for m in json.loads(body).get('data', [])}
                    except Exception:
                        pass
            if avail is None:
                add(p, '-', 'models-list', 'WARN', f'Modellliste nicht abrufbar (HTTP {st})')

        for m in models:
            limit = cfg.get(m)
            if not limit:
                add(p, m, 'config', 'FAIL', 'kein MODEL_CONFIG-Eintrag (App fiele auf DeepSeek-Limits zurueck)')
                continue
            if dry:
                add(p, m, 'plan', 'DRY', f'A(max={limit})' + (' B(Bild)' if caps.get(m) else '')
                    + (' C(Audio)' if m in audio_models and p in ('openai', 'google') else ''))
                continue
            if avail is not None:
                add(p, m, '0-verfueg.', 'PASS' if m in avail else 'WARN',
                    'in Modellliste' if m in avail else 'NICHT in der Modellliste des Anbieters')
            # A: Text mit vollem Output-Limit
            url, h, pl = build(p, m, key, 'Antworte nur mit dem Wort OK.', limit)
            st, body, dt = http(url, pl, h, label=f'{p} {m} A-text')
            ok, txt, info = parse_reply(p, st, body)
            if st == 200 and ok:
                add(p, m, 'A-text', 'PASS', f'{dt:4.1f}s max={limit} "{clean(txt, keys, 30)}" {info}')
            elif st == 200:
                add(p, m, 'A-text', 'WARN', f'{dt:4.1f}s HTTP 200 aber leere Antwort {info}')
            else:
                add(p, m, 'A-text', bad(st), f'HTTP {st} max={limit}: {clean(txt or info, keys)}')
            if no_media:
                continue
            # B: Bild
            if caps.get(m):
                url, h, pl = build(p, m, key, 'Welche Farbe hat dieses Bild? Antworte mit einem Wort.', limit, image=png)
                st, body, dt = http(url, pl, h, label=f'{p} {m} B-bild')
                ok, txt, info = parse_reply(p, st, body)
                if st == 200 and ok:
                    good = bool(re.search(r'rot|red|rojo', txt, re.I))
                    add(p, m, 'B-bild', 'PASS' if good else 'WARN', f'{dt:4.1f}s "{clean(txt, keys, 40)}" {info}')
                else:
                    add(p, m, 'B-bild', bad(st), f'HTTP {st}: {clean(txt or info, keys)}')
            # C: Audio
            if m in audio_models and p in ('openai', 'google'):
                variants = [('wav', wav, 'audio/wav', 'wav')]
                if webm:
                    variants.append(('webm', webm, 'audio/webm', 'webm'))
                for label, data, mime, fmt in variants:
                    url, h, pl = build(p, m, key, 'Beschreibe das Geraeusch in hoechstens fuenf Worten.', limit,
                                       audio=(data, mime, fmt))
                    st, body, dt = http(url, pl, h, label=f'{p} {m} C-audio-{label}')
                    ok, txt, info = parse_reply(p, st, body)
                    if st == 200 and ok:
                        add(p, m, f'C-audio-{label}', 'PASS', f'{dt:4.1f}s "{clean(txt, keys, 50)}"')
                    elif m not in set(lists.get('AUDIO_CAPABLE_MODELS', [])) and st == 400:
                        add(p, m, f'C-audio-{label}', 'PASS', 'Gegenprobe: Audio wie erwartet abgelehnt (HTTP 400)')
                    else:
                        add(p, m, f'C-audio-{label}', bad(st), f'HTTP {st}: {clean(txt or info, keys)}')
                if not webm and m in set(lists.get('AUDIO_CAPABLE_MODELS', [])):
                    add(p, m, 'C-audio-webm', 'SKIP', 'ffmpeg fehlt - echtes Browser-Format (WebM) nicht getestet')

        # D / E nur DeepSeek
        if p == 'deepseek' and not dry:
            for m in [x for x in models]:
                url, h, pl = build(p, m, key, 'Was ist 17 * 23? Nur die Zahl.', cfg.get(m, 8192), deepthink=True)
                st, body, dt = http(url, pl, h, label=f'{p} {m} D-deepthink')
                ok, txt, info = parse_reply(p, st, body)
                if st == 200 and ok:
                    add(p, m, 'D-deepthink', 'PASS' if '391' in txt else 'WARN', f'{dt:4.1f}s "{clean(txt, keys, 30)}" {info}')
                else:
                    add(p, m, 'D-deepthink', bad(st), f'HTTP {st}: {clean(txt or info, keys)}')
            url, h, pl = build(p, 'deepseek-v4-flash', key, 'Antworte nur mit dem Wort OK.', 384000)
            st, body, dt = http(url, pl, h, label=f'{p} deepseek-v4-flash E-alias')
            ok, txt, info = parse_reply(p, st, body)
            add(p, 'deepseek-v4-flash', 'E-alias', 'PASS' if (st == 200 and ok) else 'WARN',
                f'HTTP {st} (abgeloester Alias; WARN waere nur Hinweis): {clean(txt or info, keys, 80)}')

    if dry:
        return
    n = {s: sum(1 for r in results if r[3] == s) for s in ('PASS', 'WARN', 'FAIL', 'SKIP')}
    print(f"\n=== ZUSAMMENFASSUNG: {n['PASS']} PASS, {n['WARN']} WARN, {n['FAIL']} FAIL, {n['SKIP']} SKIP ===")
    for r in results:
        if r[3] in ('FAIL', 'WARN'):
            print(f'  {r[3]:4} {r[0]}/{r[1]} [{r[2]}] {r[4]}')


if __name__ == '__main__':
    main()
