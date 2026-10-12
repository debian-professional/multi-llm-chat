#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web-test.py - Automatischer Browser-Test fuer die multi-llm-chat Webseite
(Etappe 1, Stand 12.10.2026). Gegenstueck zu api-test.py: dieses Skript testet
die OBERFLAECHE, api-test.py die Provider-APIs.

Es startet ein echtes Chromium (ohne Fenster) und bedient die Seite wie ein
Mensch. Die Antworten der Provider und die Speicher-Skripte (Sitzungen,
Lesezeichen) werden dabei SIMULIERT (Playwright-Route), es entstehen also keine
API-Kosten und es werden keine Daten auf dem Server angelegt. Die Export-Skripte
(PDF/Markdown/TXT/RTF) laufen echt: lokal als Python-Prozess, bei --url auf dem
Server.

Tests (Gruppen):
  vpn          nur bei --url: VPN-Tunnel ok? (TCP-Verbindungsversuch auf die interne
               Server-IP 172.29.255.1, Ports 443/22/80; kein ICMP noetig)
  laden        Seite laedt, Texte da, keine JavaScript-Fehler
  sprache      en/de/es: jede sichtbare Beschriftung muss zur gewaehlten Sprache
               gehoeren (findet deutsche Reste in en/es und umgekehrt), in der
               Hauptseite und in allen Dialogen
  einstellung  Anbieter/Plan -> Modellliste (gegen index.html), Speichern ueber
               Neuladen, Mikrofon-Knopf je Modell
  chat         Nachricht senden fuer alle 5 Anbieter (Endpunkt, Modell, Limit,
               Streaming), Regenerieren, DeepThink, Download-Modus, Anonym, XSS
  fehler       Guthaben-/Limit-Banner, Retry mit Countdown, ueberlastet,
               Kontext zu gross (simulierte Fehlerantworten)
  export       Einzelexport TXT/MD/RTF/PDF und globaler Export je Sprache:
               Titel, Rollen, Akzente, Zeitstempel, RTF-Kodierung
  speicher     Sitzungen und Lesezeichen speichern/laden/loeschen
  dateien      Textdatei hochladen, ausfuehrbare Datei wird abgelehnt
  upload       Bild- und PDF-Upload: Bild nur bei bildfaehigem Modell, falsche Endung,
               PDF-Text wird gelesen und mitgesendet (PDF braucht pdf.js vom CDN)
  zwischenablage  Copy-Knopf, Export "Copy to clipboard", Einfuegen von Text (am Cursor /
               als Datei / abbrechen), Einfuegen von Bild und Dateipfaden
  mikrofon     Aufnahme-Knopf (Fake-Mikrofon): aufnehmen, senden, entfernen, Meldungen
               bei fehlender Berechtigung / fehlender Mikrofon-Schnittstelle
  kompressor   Kontext-Komprimierung bei hoher Auslastung, Fehlerfall, abgeschaltet

Einrichtung (einmalig, auf dem Rechner mit Browser, z.B. hpenvy):
  python3 -m venv ~/.venvs/webtest
  ~/.venvs/webtest/bin/pip install playwright
  ~/.venvs/webtest/bin/playwright install chromium

Voraussetzungen pruefen (zeigt bei Fehlendem die Installationsanleitung):
  ~/.venvs/webtest/bin/python shell-scripts/web-test.py --check
  (laeuft auch mit dem normalen python3, wenn Playwright noch fehlt)

Aufruf (aus dem Repo-Verzeichnis):
  ~/.venvs/webtest/bin/python shell-scripts/web-test.py              # alles, lokale Repo-Kopie
  ~/.venvs/webtest/bin/python shell-scripts/web-test.py --only=sprache,export
  ~/.venvs/webtest/bin/python shell-scripts/web-test.py --url=https://swtor10-chat.ddnsfree.com
  ~/.venvs/webtest/bin/python shell-scripts/web-test.py --list       # Tests auflisten
  --headed      Browserfenster anzeigen (zum Zuschauen)
  --insecure    Zertifikatsfehler ignorieren (bei --url)
  --keep=DIR    Downloads der Exporte in DIR behalten (zum Nachschauen)
  --pdfjs=DIR   pdf.min.js + pdf.worker.min.js aus DIR statt vom CDN laden (Offline;
                ohne Internet wird der PDF-Test sonst uebersprungen)
  --check       nur die installierte Zusatzsoftware pruefen, kein Test
  --no-check    die kurze Voraussetzungspruefung vor dem Test ueberspringen
  --vpn-ip=IP   Adresse fuer den VPN-Test (Standard 172.29.255.1)
  --no-vpn      den VPN-Test bei --url weglassen (--no-ping wird weiter akzeptiert)

Ohne --url wird die Seite aus var/www/deepseek-chat/ im Repo ueber einen lokalen
Mini-Server (127.0.0.1) ausgeliefert - getestet wird also der Stand VOR dem
Deploy. Mit --url wird die laufende Seite getestet (nur Lesen; Sitzungen und
Lesezeichen werden trotzdem simuliert).

Einstufung: PASS / FAIL; SKIP wenn eine Voraussetzung fehlt (z.B. pdftotext,
reportlab). Exit-Code 1 bei mindestens einem FAIL.
"""

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import struct
import tempfile
import zlib
import threading
import functools
import http.server
import socketserver
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None   # --check und main() melden das mit Anleitung

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
WEBROOT = os.path.join(REPO, 'var', 'www', 'deepseek-chat')
CGI = os.path.join(WEBROOT, 'cgi-bin')
VPN_IP = '172.29.255.1'   # interne Adresse des Servers im VPN (ICMP erreichbar, wenn der Tunnel laeuft)


def NOVPN(args):
    return '--no-vpn' in args or '--no-ping' in args


def vpn_probe(ip, ports=(443, 22, 80), timeout=3):
    """Prueft den VPN-Tunnel per TCP statt ICMP: Verbindungsversuch auf die interne Server-IP.
    Antwortet der Server (Verbindung oder 'Connection refused'), ist die Route durch den
    Tunnel da. Nur Zeitueberschreitung / 'Network unreachable' bedeutet: Tunnel down.
    Rueckgabe: (ok, Detail)."""
    import socket
    import time
    reasons = []
    for port in ports:
        t0 = time.time()
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                ms = (time.time() - t0) * 1000
                return True, f'TCP {ip}:{port} offen, {ms:.0f} ms'
        except ConnectionRefusedError:
            ms = (time.time() - t0) * 1000
            # RST kam von der Gegenseite zurueck -> Route/Tunnel funktioniert
            return True, f'TCP {ip}:{port} antwortet (geschlossen), {ms:.0f} ms - Tunnel ok'
        except socket.timeout:
            reasons.append(f'{port}: Zeitueberschreitung')
        except OSError as e:
            reasons.append(f'{port}: {e.strerror or e}')
    return False, f'keine TCP-Antwort von {ip} (' + '; '.join(reasons) + ')'


# ---------------------------------------------------------------------------
# Hilfen: Sprachdatei und index.html lesen
# ---------------------------------------------------------------------------

def load_texts(webroot):
    """language.xml -> {lang: {id(int): text}}"""
    tree = ET.parse(os.path.join(webroot, 'language.xml'))
    out = {}
    for lang in tree.getroot().iter('language'):
        out[lang.get('id')] = {(int(t.get('id')) if t.get('id').isdigit() else t.get('id')): (t.text or '') for t in lang.iter('text')}
    return out


def load_lists(html):
    """Liest Modelllisten, MODEL_CONFIG und AUDIO_CAPABLE_MODELS aus index.html."""
    lists = {}
    for m in re.finditer(r'const\s+([A-Z_]+_MODELS(?:_FREE|_PAID)?)\s*=\s*\[(.*?)\]', html, re.S):
        lists[m.group(1)] = re.findall(r"'([^']+)'", m.group(2))
    cfg = {}
    block = re.search(r'const MODEL_CONFIG = \{(.*?)\n        \};', html, re.S)
    if block:
        for m in re.finditer(r"'([^']+)':\s*\{[^}]*?maxOutputTokens:\s*(\d+)", block.group(1), re.S):
            cfg[m.group(1)] = int(m.group(2))
    return lists, cfg


# ---------------------------------------------------------------------------
# Simuliertes Backend
# ---------------------------------------------------------------------------

class Mock:
    def __init__(self, base, local, keep):
        self.base = base
        self.local = local            # True: Export-Skripte lokal ausfuehren
        self.keep = keep
        self.reset()

    def reset(self):
        self.requests = []            # (name, json-body) aller Chat-Anfragen
        self.sessions = {}
        self.bookmarks = {}
        self.saves = 0
        self.chat_reply = None        # None = normale Antwort, sonst (status, dict)
        self.chat_text = 'Hallo! Das ist die Mock-Antwort mit Umlauten äöü und ¿Qué tal? Gruss.'
        self.export_calls = []
        self.compress_calls = []      # Nutzdaten der Kompressor-Anfragen
        self.compress_reply = None    # None = Erfolg, sonst (status, dict)

    # --- Chat ---
    def sse(self, text):
        chunks = [text[i:i + 12] for i in range(0, len(text), 12)]
        body = ''.join('data: ' + json.dumps({'choices': [{'delta': {'content': c}}]}) + '\n\n' for c in chunks)
        return body + 'data: [DONE]\n\n'

    def chat(self, route, name, payload):
        self.requests.append((name, payload))
        if self.chat_reply is not None:
            status, body = self.chat_reply
            route.fulfill(status=status, headers={'Content-Type': 'application/json'}, body=json.dumps(body))
        else:
            route.fulfill(status=200, headers={'Content-Type': 'text/event-stream'}, body=self.sse(self.chat_text))

    # --- Export-Skripte echt ausfuehren ---
    def run_cgi(self, name, raw):
        script = os.path.join(CGI, name)
        py = '/usr/bin/python3' if os.path.exists('/usr/bin/python3') else sys.executable
        env = dict(os.environ, REQUEST_METHOD='POST', CONTENT_LENGTH=str(len(raw)))
        r = subprocess.run([py, script], input=raw, capture_output=True, env=env, timeout=60)
        out = r.stdout
        m = re.search(rb'\r?\n\r?\n', out)
        head, body = (out[:m.start()], out[m.end():]) if m else (b'', out)
        status, headers = 200, {}
        for line in head.decode('utf-8', 'replace').splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                if k.strip().lower() == 'status':
                    status = int(v.strip().split()[0])
                elif k.strip().lower() not in ('content-length',):
                    headers[k.strip()] = v.strip()
        if r.returncode != 0 and not out:
            return 500, {'Content-Type': 'text/plain'}, r.stderr
        return status, headers, body

    def handle(self, route):
        req = route.request
        path = urlparse(req.url).path
        if not path.startswith('/cgi-bin/'):
            return route.continue_()
        name = path.rsplit('/', 1)[1]
        raw = req.post_data_buffer or b''
        try:
            payload = json.loads(raw.decode('utf-8')) if raw else {}
        except Exception:
            payload = {}
        j = lambda obj, st=200: route.fulfill(status=st, headers={'Content-Type': 'application/json'}, body=json.dumps(obj))

        if name in ('deepseek-api.py', 'google-api.py', 'hugging-api.py', 'groq-api.py', 'openai-api.py'):
            if req.method == 'POST':
                return self.chat(route, name, payload)
            return j({'data': []})
        if name == 'deepseek-models.py':
            return j({'data': [{'id': 'deepseek-flash'}, {'id': 'deepseek-v4-pro'}]})
        if name == 'save-session.py':
            self.saves += 1
            self.sessions[payload['sessionId']] = payload['chatData']
            return j({'success': True})
        if name == 'load-session.py':
            if req.method == 'POST':
                sid = payload.get('sessionId')
                if sid in self.sessions:
                    return j({'success': True, 'chatData': self.sessions[sid]})
                return j({'success': False, 'error': 'nicht gefunden'}, 404)
            lst = []
            for sid, cd in self.sessions.items():
                first = next((m['content'][:50] for m in cd['messages'] if m['role'] == 'user'), '')
                lst.append({'sessionId': sid, 'timestamp': cd.get('timestamp'), 'messageCount': len(cd['messages']), 'preview': first})
            return j({'success': True, 'sessions': lst})
        if name == 'delete-session.py':
            self.sessions.pop(payload.get('sessionId'), None)
            return j({'success': True})
        if name == 'save-bookmark.py':
            self.bookmarks[payload['bookmarkId']] = {'bookmarkId': payload['bookmarkId'], 'title': payload['title'],
                                                     'promptText': payload['promptText'], 'timestamp': '2026-10-12T10:00:00'}
            return j({'success': True})
        if name == 'load-bookmark.py':
            if req.method == 'POST':
                b = self.bookmarks.get(payload.get('bookmarkId'))
                return j({'success': True, 'bookmarkData': b}) if b else j({'success': False}, 404)
            return j({'success': True, 'bookmarks': [dict(b, preview=b['promptText'][:60]) for b in self.bookmarks.values()]})
        if name == 'delete-bookmark.py':
            self.bookmarks.pop(payload.get('bookmarkId'), None)
            return j({'success': True})
        if name == 'compress-context.py':
            self.compress_calls.append(payload)
            if self.compress_reply is not None:
                return j(self.compress_reply[1], self.compress_reply[0])
            return j({'summary': 'Mock-Zusammenfassung'})
        if name == 'feedback-log.py':
            return j({'success': True})
        if name == 'get-log.py':
            return route.fulfill(status=200, headers={'Content-Type': 'text/plain'}, body='Mock-Log')
        if name.startswith('export-'):
            self.export_calls.append((name, payload))
            if self.local:
                st, h, body = self.run_cgi(name, raw)
                return route.fulfill(status=st, headers=h, body=body)
            return route.continue_()
        return route.continue_()


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def start_static(root):
    handler = functools.partial(Quiet, directory=root)
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f'http://127.0.0.1:{srv.server_address[1]}/'


# ---------------------------------------------------------------------------
# Testgeruest
# ---------------------------------------------------------------------------

class Ctx:
    """Alles, was die Tests brauchen."""
    pass


RESULTS = []


def add(group, name, ok, detail=''):
    st = 'PASS' if ok is True else ('SKIP' if ok is None else 'FAIL')
    RESULTS.append((group, name, st, detail))
    print(f'{st:5} {group:12} {name:44} {detail}', flush=True)


TESTS = []   # (group, funktion)


def test(group):
    def deco(fn):
        TESTS.append((group, fn))
        return fn
    return deco


def new_page(C, settings=None, fast=False, lang=None):
    """Frische Seite mit leerem Speicher; optional vorbelegten Einstellungen."""
    ctx = C.browser.new_context(accept_downloads=True, ignore_https_errors=C.insecure,
                                viewport={'width': 1280, 'height': 900}, locale='en-US')
    C.mock.reset()
    ctx.route('**/cgi-bin/*', C.mock.handle)
    page = ctx.new_page()
    page.errors = []
    page.on('pageerror', lambda e: page.errors.append('pageerror: ' + str(e)))
    page.on('console', lambda m: page.errors.append('console: ' + m.text) if (m.type == 'error' and 'net::ERR_' not in m.text) else None)  # reine Netzwerkfehler (z.B. CDN offline) ignorieren
    page.dialogs = []   # Texte aller alert()-Meldungen
    def on_dialog(d):
        page.dialogs.append(d.message)
        d.accept(page.dialog_answer if hasattr(page, 'dialog_answer') else '')
    page.on('dialog', on_dialog)
    try:   # Zwischenablage und Mikrofon fuer die Tests freigeben (nur fuer diese Adresse)
        ctx.grant_permissions(['clipboard-read', 'clipboard-write', 'microphone'], origin=C.base.rstrip('/'))
    except Exception:
        pass
    if getattr(C, 'pdfjs', None):   # pdf.js lokal statt vom CDN ausliefern (Offline-Betrieb)
        def pdfjs_route(route):
            name = 'pdf.worker.min.js' if 'worker' in route.request.url else 'pdf.min.js'
            path = os.path.join(C.pdfjs, name)
            hdr = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/javascript'}
            if os.path.exists(path):
                route.fulfill(status=200, headers=hdr, body=b'' if route.request.method == 'HEAD' else open(path, 'rb').read())
            else:
                route.abort()
        ctx.route(re.compile(r'https://(cdnjs\.cloudflare\.com/ajax/libs/pdf\.js/[\d.]+|unpkg\.com/pdfjs-dist@[\d.]+/build)/pdf(\.worker)?\.min\.js'), pdfjs_route)
    if fast:   # Wartezeiten ab 1 s (Retry-Countdown) auf 10 ms kuerzen
        page.add_init_script("(() => { const st = window.setTimeout; "
                             "window.setTimeout = (f, d, ...a) => st(f, (d >= 1000 ? 10 : d), ...a); })()")
    if settings is not None:
        s = dict(settings)
        s.setdefault('language', lang or 'en')
        # nur beim ersten Laden setzen - sonst wuerde jedes Neuladen die Einstellungen ueberschreiben
        page.add_init_script('if (!localStorage.getItem("deepseekSettings")) localStorage.setItem('
                             '"deepseekSettings", JSON.stringify(Object.assign({version: 0}, ' + json.dumps(s) + ')));')
    page.goto(C.base)
    page.wait_for_selector('#sendButton')
    page.wait_for_function('document.getElementById("sendButton").textContent.trim().length > 0')
    page.ctx = ctx
    return page


def close(page):
    page.ctx.close()


def tx(C, lang, i, *args):
    t = C.texts[lang][i]
    for n, a in enumerate(args):
        t = t.replace('{%d}' % n, str(a))
    return t


def send(page, text, wait_reply=True):
    page.fill('#input', text)
    page.click('#sendButton')
    if wait_reply:
        page.wait_for_function('!document.getElementById("sendButton").disabled', timeout=20000)


def chat_texts(page):
    return page.eval_on_selector_all('#chat .ai-message', 'els => els.map(e => e.textContent)')


def ignore_errors(page, patterns=()):
    """JS-Fehler der Seite, die nicht zu erwarteten Testfaellen gehoeren."""
    return [e for e in page.errors if not any(p in e for p in patterns)]


# ---------------------------------------------------------------------------
# Gruppe: laden
# ---------------------------------------------------------------------------

@test('vpn')
def t_vpn(C):
    if not C.url_mode:
        add('vpn', f'VPN-Tunnel (TCP {C.vpn_ip})', None, 'lokaler Modus - kein Server, nicht noetig')
        return
    if C.no_vpn:
        add('vpn', f'VPN-Tunnel (TCP {C.vpn_ip})', None, '--no-vpn')
        return
    ok, detail = vpn_probe(C.vpn_ip)
    add('vpn', f'VPN-Tunnel (TCP {C.vpn_ip})', ok,
        detail if ok else detail + ' - VPN-Tunnel pruefen')


@test('laden')
def t_laden(C):
    p = new_page(C)
    add('laden', 'Seite laedt, Sendeknopf beschriftet', p.inner_text('#sendButton').strip() == tx(C, 'en', 205), p.inner_text('#sendButton'))
    add('laden', 'Kopfzeile mit Servername sichtbar', p.is_visible('#serverTitle'))
    add('laden', 'Eingabefeld-Platzhalter gesetzt', bool(p.get_attribute('#input', 'placeholder')), p.get_attribute('#input', 'placeholder') or '')
    errs = ignore_errors(p, ('/cgi-bin/deepseek-models.py',))
    add('laden', 'keine JavaScript-Fehler beim Laden', not errs, '; '.join(errs)[:200])
    close(p)


# ---------------------------------------------------------------------------
# Gruppe: sprache
# ---------------------------------------------------------------------------

LEAF_JS = """
() => {
  const out = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const t = n.nodeValue.replace(/\\s+/g, ' ').trim();
    if (!t) continue;
    const el = n.parentElement;
    if (!el || ['SCRIPT', 'STYLE', 'OPTION'].includes(el.tagName)) continue;
    if (el.closest('#chat')) continue;
    if (!(el.getClientRects().length > 0)) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    out.push(t);
  }
  const attrs = [];
  document.querySelectorAll('[title],[placeholder]').forEach(e => {
    if (!(e.getClientRects().length > 0)) return;
    ['title', 'placeholder'].forEach(a => { const v = e.getAttribute(a); if (v) attrs.push(v.trim()); });
  });
  return out.concat(attrs);
}
"""

PANELS = [
    ('Hauptseite', None, None),
    ('Export-Menue', '#exportButton', '#exportButton'),
    ('Einstellungen', '#settingsButton', '#closeSettings'),
    ('LLM-Einstellungen', '#llmSettingsButton', '#closeLlmSettings'),
    ('Gespeicherte Chats', ['#exportButton', '#loadSessionBtn'], '#closeSessions'),
    ('Lesezeichen', '#bookmarksButton', '#closeBookmarks'),
    ('Log', '#logButton', '#closeLog'),
]


def other_lang_texts(C, lang):
    """Texte, die es in einer ANDEREN Sprache gibt, aber nicht in der gewaehlten."""
    mine = set(C.texts[lang].values())
    others = {}
    for l, d in C.texts.items():
        if l == lang or l == 'custom':
            continue
        for i, t in d.items():
            if t and t not in mine:
                others.setdefault(t.strip(), l)
    return others


@test('sprache')
def t_sprache(C):
    for lang, item in (('en', '#langEnItem'), ('de', '#langDeItem'), ('es', '#langEsItem')):
        p = new_page(C, {'apiService': 'deepseek'}, lang=lang)
        wrong = []
        for label, opener, closer in PANELS:
            if opener:
                for sel in (opener if isinstance(opener, list) else [opener]):
                    p.click(sel)
                p.wait_for_timeout(150)
            texts = p.evaluate(LEAF_JS)
            others = other_lang_texts(C, lang)
            for t in texts:
                if t in others:
                    wrong.append(f'{label}: "{t[:50]}" ({others[t]})')
            if opener and closer:
                p.click(closer) if closer != opener else p.click(opener)
                p.wait_for_timeout(100)
            p.evaluate("document.getElementById('exportMenu').classList.remove('show')")
        add('sprache', f'{lang}: keine Texte einer anderen Sprache sichtbar', not wrong, '; '.join(wrong[:3]))
        exp = {205: p.inner_text('#sendButton'), 213: p.inner_text('#settingsButton'), 214: p.inner_text('#logButton')}
        good = all(exp[i].strip() == C.texts[lang][i] for i in exp)
        add('sprache', f'{lang}: Hauptknoepfe (Send/Settings/Log) richtig', good, str(list(exp.values())))
        ph = p.get_attribute('#input', 'placeholder') or ''
        add('sprache', f'{lang}: Eingabe-Platzhalter in {lang}', bool(ph) and ph not in other_lang_texts(C, lang), ph)
        close(p)

    # Umschalten im laufenden Betrieb ueber die Einstellungen
    p = new_page(C, {'apiService': 'deepseek'}, lang='en')
    p.click('#settingsButton')
    p.click('#langDeItem')
    p.wait_for_timeout(200)
    de_ok = p.inner_text('#sendButton').strip() == C.texts['de'][205]
    p.click('#langEsItem')
    p.wait_for_timeout(200)
    es_ok = p.inner_text('#sendButton').strip() == C.texts['es'][205]
    add('sprache', 'Umschalten en -> de -> es im Betrieb', de_ok and es_ok, p.inner_text('#sendButton'))
    p.click('#saveSettings')
    p.reload()
    p.wait_for_selector('#sendButton')
    p.wait_for_timeout(300)
    add('sprache', 'gewaehlte Sprache bleibt nach Neuladen', p.inner_text('#sendButton').strip() == C.texts['es'][205], p.inner_text('#sendButton'))
    close(p)


# ---------------------------------------------------------------------------
# Gruppe: einstellung
# ---------------------------------------------------------------------------

def model_options(p):
    return p.eval_on_selector_all('#modelSelect option', 'els => els.map(e => e.value)')


@test('einstellung')
def t_einstellung(C):
    L = C.lists
    cases = [
        ('openai', 'free', '#openaiServiceItem', '#openaiFreeTierItem', L.get('OPENAI_MODELS_FREE')),
        ('openai', 'paid', '#openaiServiceItem', '#openaiPaidTierItem', L.get('OPENAI_MODELS_PAID')),
        ('google', 'free', '#googleServiceItem', '#googleFreeTierItem', L.get('GOOGLE_MODELS_FREE')),
        ('google', 'paid', '#googleServiceItem', '#googlePaidTierItem', L.get('GOOGLE_MODELS_PAID')),
        ('groq', 'free', '#groqServiceItem', '#groqFreeTierItem', L.get('GROQ_MODELS_FREE')),
        ('groq', 'paid', '#groqServiceItem', '#groqPaidTierItem', L.get('GROQ_MODELS_PAID')),
        ('huggingface', 'free', '#huggingfaceServiceItem', '#hfFreeTierItem', L.get('HF_MODELS_FREE')),
        ('huggingface', 'paid', '#huggingfaceServiceItem', '#hfPaidTierItem', L.get('HF_MODELS_PAID')),
    ]
    p = new_page(C, {'apiService': 'deepseek'})
    for prov, tier, svc, tr, expected in cases:
        if not expected:
            add('einstellung', f'{prov}/{tier}: Modellliste', None, 'Liste in index.html nicht gefunden')
            continue
        p.click('#settingsButton')
        p.click(svc)
        p.wait_for_timeout(100)
        p.click('#closeSettings')
        p.click('#llmSettingsButton')
        p.click(tr)
        p.wait_for_timeout(100)
        got = model_options(p)
        add('einstellung', f'{prov}/{tier}: Modellliste = index.html', got == expected, f'{len(got)} Modelle' if got == expected else f'{got} != {expected}')
        p.click('#closeLlmSettings')
    ds = model_options(p)
    close(p)

    # Speichern ueber Neuladen
    p = new_page(C, {'apiService': 'deepseek'})
    p.click('#settingsButton')
    p.click('#openaiServiceItem')
    p.click('#closeSettings')
    p.click('#llmSettingsButton')
    p.click('#openaiPaidTierItem')
    p.select_option('#modelSelect', 'gpt-6-astra')
    p.click('#saveLlmSettings')
    p.wait_for_timeout(200)
    s = p.evaluate('JSON.parse(localStorage.getItem("deepseekSettings"))')
    add('einstellung', 'OpenAI/Paid/gpt-6-astra wird gespeichert',
        s.get('apiService') == 'openai' and s.get('openaiTier') == 'paid' and s.get('selectedModel') == 'gpt-6-astra', json.dumps({k: s.get(k) for k in ('apiService', 'openaiTier', 'selectedModel')}))
    p.reload()
    p.wait_for_selector('#sendButton')
    p.wait_for_timeout(300)
    info = p.inner_text('#modelInfo')
    add('einstellung', 'Modell bleibt nach Neuladen (Kopfzeile)', 'gpt-6-astra' in info, info)
    close(p)

    # Mikrofon-Knopf je Modell
    audio = C.lists.get('AUDIO_CAPABLE_MODELS', [])
    for prov, model in (('openai', 'gpt-6-astra'), ('google', 'gemini-3.8-flash'), ('deepseek', 'deepseek-flash'), ('groq', 'openai/gpt-oss-120b')):
        p = new_page(C, {'apiService': prov, 'selectedModel': model, 'openaiTier': 'paid', 'googleTier': 'paid'})
        vis = p.is_visible('#audioButton')
        want = model in audio
        add('einstellung', f'Mikrofon-Knopf {model}: {"sichtbar" if want else "ausgeblendet"}', vis == want, f'sichtbar={vis}')
        close(p)


# ---------------------------------------------------------------------------
# Gruppe: chat
# ---------------------------------------------------------------------------

PROVIDERS = [
    ('deepseek', 'deepseek-api.py', 'deepseek-flash', {}),
    ('openai', 'openai-api.py', 'gpt-6-astra', {'openaiTier': 'paid'}),
    ('google', 'google-api.py', 'gemini-3.8-flash', {'googleTier': 'free'}),
    ('groq', 'groq-api.py', 'openai/gpt-oss-120b', {'groqTier': 'free'}),
    ('huggingface', 'hugging-api.py', 'Qwen/Qwen2.5-72B-Instruct', {'hfTier': 'free'}),
]


@test('chat')
def t_chat(C):
    for prov, endpoint, model, extra in PROVIDERS:
        p = new_page(C, dict({'apiService': prov, 'selectedModel': model}, **extra))
        send(p, 'Hallo Test')
        reqs = [r for r in C.mock.requests if r[0] == endpoint]
        ok_req = bool(reqs) and reqs[0][1].get('model') == model
        add('chat', f'{prov}: Anfrage an {endpoint} mit Modell {model}', ok_req, reqs[0][1].get('model', '?') if reqs else 'keine Anfrage')
        if reqs:
            exp = C.cfg.get(model)
            got = reqs[0][1].get('max_tokens')
            add('chat', f'{prov}: max_tokens = MODEL_CONFIG', exp is None or got == exp, f'{got} (erwartet {exp})')
            msgs = reqs[0][1].get('messages', [])
            add('chat', f'{prov}: System-Prompt + Nutzertext gesendet', len(msgs) >= 2 and msgs[0]['role'] == 'system' and msgs[-1]['content'] == 'Hallo Test', f'{len(msgs)} Nachrichten')
        txt = chat_texts(p)
        add('chat', f'{prov}: Antwort wird angezeigt (Umlaute, Streaming)', bool(txt) and txt[-1] == C.mock.chat_text, (txt[-1][:50] if txt else 'leer'))
        close(p)

    p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'})
    send(p, 'Hallo')
    btns = p.eval_on_selector_all('#chat .feedback-btn', 'els => els.map(e => e.textContent.trim())')
    want = [tx(C, 'en', i) for i in (217, 218, 219, 220)]
    add('chat', 'Knoepfe unter der Antwort (Copy/Like/Dislike/Regenerate)', btns == want, str(btns))
    n0 = len(C.mock.requests)
    p.dispatch_event('#chat .feedback-btn:nth-child(4)', 'click')   # Knoepfe erscheinen nur beim Ueberfahren
    p.wait_for_function('!document.getElementById("sendButton").disabled')
    p.wait_for_timeout(500)
    add('chat', 'Regenerieren sendet eine neue Anfrage', len(C.mock.requests) == n0 + 1, f'{n0} -> {len(C.mock.requests)}')
    close(p)

    # DeepThink
    p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'})
    send(p, 'ohne')
    p.click('#deepThinkButton')
    add('chat', 'DeepThink-Anzeige erscheint', p.is_visible('#deepThinkIndicator'))
    send(p, 'mit')
    a, b = C.mock.requests[0][1], C.mock.requests[1][1]
    add('chat', 'DeepSeek: thinking_enabled false/true je nach Modus', a.get('thinking_enabled') is False and b.get('thinking_enabled') is True,
        f'{a.get("thinking_enabled")} / {b.get("thinking_enabled")}')
    close(p)

    # Download-Modus
    p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'})
    p.click('#downloadModeButton')
    send(p, 'lang')
    txt = chat_texts(p)
    n = f'{len(C.mock.chat_text):,}'
    shown = txt[-1] if txt else ''
    add('chat', 'Download-Modus: nur Zeichenzaehler statt Text', C.mock.chat_text not in shown and any(ch.isdigit() for ch in shown), shown[:60])
    close(p)

    # Anonymer Chat speichert nichts
    p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'})
    p.click('#newChatAnonymousButton')
    add('chat', 'Anonymer Chat: Hinweis sichtbar', p.is_visible('#anonymousNotice'))
    send(p, 'geheim')
    p.wait_for_timeout(300)
    add('chat', 'Anonymer Chat: nichts gespeichert', C.mock.saves == 0 and not C.mock.sessions, f'saves={C.mock.saves}')
    close(p)

    # normaler Chat speichert
    p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'})
    send(p, 'normal')
    p.wait_for_timeout(300)
    add('chat', 'Normaler Chat: Sitzung wird gespeichert', C.mock.saves >= 1 and len(C.mock.sessions) == 1, f'saves={C.mock.saves}')
    close(p)

    # XSS: HTML in Nutzertext und Antwort darf nicht ausgefuehrt werden
    p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'})
    C.mock.chat_text = 'Antwort <img src=x onerror="window.__xss=1"> <script>window.__xss=2</script>'
    send(p, '<img src=x onerror="window.__xss=3"><b>fett</b>')
    p.wait_for_timeout(300)
    xss = p.evaluate('window.__xss')
    imgs = p.eval_on_selector_all('#chat img', 'e => e.length')
    add('chat', 'XSS: HTML in Nutzer-/KI-Text wird nicht ausgefuehrt', xss is None and imgs == 0, f'__xss={xss}, img={imgs}')
    close(p)
    C.mock.chat_text = Mock(None, True, None).chat_text


# ---------------------------------------------------------------------------
# Gruppe: fehler
# ---------------------------------------------------------------------------

def err_page(C, prov, model, extra=None):
    p = new_page(C, dict({'apiService': prov, 'selectedModel': model}, **(extra or {})), fast=True)
    return p


@test('fehler')
def t_fehler(C):
    EXPECTED = ('Failed to load resource', 'ERR_', '/cgi-bin/')

    def last_ai(p):
        t = chat_texts(p)
        return t[-1] if t else ''

    # OpenAI: Guthaben leer (402/429 insufficient_quota) -> rotes Banner
    p = err_page(C, 'openai', 'gpt-6-astra', {'openaiTier': 'paid'})
    C.mock.chat_reply = (429, {'error': 'quota', 'error_type': 'insufficient_quota'})
    send(p, 'x')
    p.wait_for_timeout(300)
    vis = p.is_visible('#guthabenBanner')
    add('fehler', 'OpenAI insufficient_quota: Guthaben-Banner (ID 256)', vis and tx(C, 'en', 256) in p.inner_text('#guthabenBannerText'), p.inner_text('#guthabenBannerText')[:60])
    add('fehler', 'OpenAI insufficient_quota: keine Wiederholung', len(C.mock.requests) == 1, f'{len(C.mock.requests)} Anfragen')
    close(p)

    # OpenAI: Ausgabenlimit
    p = err_page(C, 'openai', 'gpt-6-astra', {'openaiTier': 'paid'})
    C.mock.chat_reply = (429, {'error': 'limit', 'error_type': 'spend_limit'})
    send(p, 'x')
    p.wait_for_timeout(300)
    add('fehler', 'OpenAI spend_limit: Banner mit Text 277', p.is_visible('#guthabenBanner') and tx(C, 'en', 277) in p.inner_text('#guthabenBannerText'), p.inner_text('#guthabenBannerText')[:60])
    close(p)

    # OpenAI: 503 -> 3 Versuche, dann Meldung 278
    p = err_page(C, 'openai', 'gpt-6-astra', {'openaiTier': 'paid'})
    C.mock.chat_reply = (503, {'error': 'overloaded', 'error_type': 'overloaded'})
    send(p, 'x')
    p.wait_for_timeout(300)
    add('fehler', 'OpenAI 503: 3 Versuche', len(C.mock.requests) == 3, f'{len(C.mock.requests)} Anfragen')
    add('fehler', 'OpenAI 503: Meldung "Anbieter ueberlastet" (ID 278)', tx(C, 'en', 278) in last_ai(p), last_ai(p)[:80])
    close(p)

    # OpenAI: rate_limited -> wiederholt
    p = err_page(C, 'openai', 'gpt-6-astra', {'openaiTier': 'paid'})
    C.mock.chat_reply = (429, {'error': 'slow', 'error_type': 'rate_limited'})
    send(p, 'x')
    p.wait_for_timeout(300)
    add('fehler', 'OpenAI 429 rate_limited: 3 Versuche', len(C.mock.requests) == 3, f'{len(C.mock.requests)} Anfragen')
    close(p)

    # Google 429 daily_limit -> Tageslimit-Banner
    p = err_page(C, 'google', 'gemini-3.8-flash', {'googleTier': 'free'})
    C.mock.chat_reply = (429, {'error': 'daily', 'error_type': 'daily_limit'})
    send(p, 'x')
    p.wait_for_timeout(300)
    add('fehler', 'Google 429 daily_limit: Tageslimit-Banner (ID 257)', p.is_visible('#tageslimitBanner') and tx(C, 'en', 257) in p.inner_text('#tageslimitBannerText'), f'{len(C.mock.requests)} Anfragen')
    close(p)

    # Google 429 ohne Typ -> 3 Versuche, Text 143
    p = err_page(C, 'google', 'gemini-3.8-flash', {'googleTier': 'free'})
    C.mock.chat_reply = (429, {'error': 'rate', 'error_type': 'rate_limited'})
    send(p, 'x')
    p.wait_for_timeout(300)
    add('fehler', 'Google 429: 3 Versuche, dann Text 143', len(C.mock.requests) == 3 and tx(C, 'en', 143) in last_ai(p), f'{len(C.mock.requests)} Anfragen; {last_ai(p)[:60]}')
    close(p)

    # Google 503
    p = err_page(C, 'google', 'gemini-3.8-flash', {'googleTier': 'free'})
    C.mock.chat_reply = (503, {'error': 'x', 'error_type': 'overloaded'})
    send(p, 'x')
    p.wait_for_timeout(300)
    add('fehler', 'Google 503: 3 Versuche, Meldung 278', len(C.mock.requests) == 3 and tx(C, 'en', 278) in last_ai(p), f'{len(C.mock.requests)} Anfragen')
    close(p)

    # DeepSeek: Guthaben (402)
    p = err_page(C, 'deepseek', 'deepseek-flash')
    C.mock.chat_reply = (402, {'error': 'Insufficient Balance', 'error_type': 'insufficient_quota'})
    send(p, 'x')
    p.wait_for_timeout(300)
    add('fehler', 'DeepSeek insufficient_quota: Guthaben-Banner', p.is_visible('#guthabenBanner'), p.inner_text('#guthabenBannerText')[:60])
    close(p)

    # Kontext zu gross
    for prov, extra, model in (('openai', {'openaiTier': 'paid'}, 'gpt-6-astra'), ('deepseek', {}, 'deepseek-flash')):
        p = err_page(C, prov, model, extra)
        C.mock.chat_reply = (400, {'error': 'too long', 'error_type': 'context_exceeded'})
        send(p, 'x')
        p.wait_for_timeout(300)
        add('fehler', f'{prov} context_exceeded: Hinweisbox (ID 259)', p.is_visible('.context-exceeded-box') and tx(C, 'en', 259) in p.inner_text('.context-exceeded-box'), '')
        close(p)

    # Banner-Text folgt der Sprache (Umschalten bei sichtbarem Banner)
    p = err_page(C, 'openai', 'gpt-6-astra', {'openaiTier': 'paid'})
    C.mock.chat_reply = (429, {'error': 'quota', 'error_type': 'insufficient_quota'})
    send(p, 'x')
    p.wait_for_timeout(200)
    p.click('#settingsButton')
    p.click('#langDeItem')
    p.wait_for_timeout(200)
    add('fehler', 'Guthaben-Banner wechselt mit der Sprache auf Deutsch', tx(C, 'de', 256) in p.inner_text('#guthabenBannerText'), p.inner_text('#guthabenBannerText')[:60])
    close(p)


# ---------------------------------------------------------------------------
# Gruppe: export
# ---------------------------------------------------------------------------

def download(p, action, C, name):
    with p.expect_download(timeout=30000) as d:
        action()
    dl = d.value
    tmp = os.path.join(C.tmpdir, f'{name}-{dl.suggested_filename}')
    dl.save_as(tmp)
    if C.keep:
        shutil.copy(tmp, os.path.join(C.keep, os.path.basename(tmp)))
    return dl.suggested_filename, tmp


def pdf_text(path):
    if not shutil.which('pdftotext'):
        return None
    r = subprocess.run(['pdftotext', '-layout', path, '-'], capture_output=True)
    return r.stdout.decode('utf-8', 'replace')


def rtf_to_text(path):
    """RTF -> Text mit LibreOffice, falls vorhanden (sonst None)."""
    so = shutil.which('soffice') or shutil.which('libreoffice')
    if not so:
        return None
    outdir = tempfile.mkdtemp(dir=os.path.dirname(path))
    subprocess.run([so, '--headless', '--convert-to', 'txt:Text (encoded):UTF8', '--outdir', outdir, path],
                   capture_output=True, timeout=120)
    files = [f for f in os.listdir(outdir) if f.endswith('.txt')]
    if not files:
        return None
    return open(os.path.join(outdir, files[0]), encoding='utf-8-sig').read()


@test('export')
def t_export(C):
    msg = 'Frage: ¿Cómo está, María? Äöü € – 日本'
    for lang in ('es', 'en', 'de'):
        T = C.texts[lang]
        p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'}, lang=lang)
        C.mock.chat_text = 'Claro que sí: corazón, Lucía, ¿Quieres? 😊 Ünïcödé'   # nach new_page (reset)
        send(p, msg)
        p.wait_for_timeout(300)
        mid = p.evaluate('contextHistory.messages[contextHistory.messages.length - 1].id')

        # --- Einzelexport clientseitig ---
        for ext, fn in (('txt', 'exportSingleAsTxt'), ('md', 'exportSingleAsMarkdown'), ('rtf', 'exportSingleAsRtf')):
            name, path = download(p, lambda: p.evaluate(f'{fn}("{mid}")'), C, f'{lang}-single')
            data = open(path, 'rb').read()
            if ext == 'rtf':
                ascii_ok = all(b < 128 for b in data)
                add('export', f'{lang}: Einzel-RTF ist reines ASCII (Escape-Codes)', ascii_ok, 'nicht-ASCII-Bytes gefunden' if not ascii_ok else '')
                txt = rtf_to_text(path)
                if txt is None:
                    add('export', f'{lang}: Einzel-RTF Inhalt (LibreOffice)', None, 'LibreOffice fehlt - Inhalt nicht geprueft')
                else:
                    add('export', f'{lang}: Einzel-RTF: Akzente und Titel korrekt', T[283] in txt and 'corazón' in txt and '¿Quieres?' in txt and 'Ã' not in txt, T[283] in txt and 'ok' or txt[:80])
            else:
                txt = data.decode('utf-8')
                add('export', f'{lang}: Einzel-{ext.upper()}: Titel/Rolle/Akzente', T[283] in txt and T[289] in txt and 'corazón' in txt and '😊' in txt, txt[:60].replace('\n', ' '))
                ts = re.search(r'(\d{1,2}[./]\d{1,2}[./]\d{4}), ', txt)
                expect_fmt = {'en': r'^\d{1,2}/\d{1,2}/\d{4}$', 'de': r'^\d{1,2}\.\d{1,2}\.\d{4}$', 'es': r'^\d{1,2}/\d{1,2}/\d{4}$'}[lang]
                good_ts = bool(ts) and re.match(expect_fmt, ts.group(1)) is not None
                if lang == 'en' or lang == 'es':
                    pass
                if ext == 'txt':
                    add('export', f'{lang}: Zeitstempel im Format der Sprache', good_ts, ts.group(1) if ts else 'kein Datum')

        # --- globaler Export ueber das Menue ---
        def open_and_click(btn):
            p.click('#exportButton')
            p.click(btn)

        name, path = download(p, lambda: open_and_click('#exportTxtBtn'), C, f'{lang}-global')
        txt = open(path, encoding='utf-8').read()
        ok = T[283].upper() in txt and T[285] in txt and T[286] in txt and T[288].upper() in txt and T[289].upper() in txt and 'corazón' in txt
        add('export', f'{lang}: globaler TXT-Export (Beschriftungen, Akzente)', ok, txt[:70].replace('\n', ' '))
        add('export', f'{lang}: globaler TXT enthaelt kein "DEEPSEEK"', 'DEEPSEEK' not in txt.upper(), '')

        name, path = download(p, lambda: open_and_click('#exportMarkdownBtn'), C, f'{lang}-global')
        md = open(path, encoding='utf-8').read()
        ok = (md.startswith('# ' + T[283]) and f'## {T[294]}' in md and f'## {T[302]}' in md and f'## {T[303]}' in md
              and '(#msg-1)' in md and 'corazón' in md and ('sie' not in md.split('\n')[4] if lang != 'de' else True))
        add('export', f'{lang}: globaler Markdown (Titel, Statistik, Inhalt, Anker)', ok, md.split('\n')[0])
        cfgline = next((l for l in md.split('\n') if l.startswith(f'**{T[292]}:**')), '')
        rest = cfgline.split(':**', 1)[-1].strip()
        if lang == 'de':
            add('export', 'de: Konfigurationszeile "Sie-Form, Modus: chat"', rest == 'Sie-Form, Modus: chat', cfgline)
        elif lang == 'es':
            add('export', 'es: Konfigurationszeile "Usted" statt rohem "sie"', rest == 'Tratamiento: Usted, modo: chat', cfgline)
        else:
            add('export', 'en: Konfigurationszeile nur mit Modus', rest == 'Mode: chat', cfgline)

        name, path = download(p, lambda: open_and_click('#exportRtfBtn'), C, f'{lang}-global')
        raw = open(path, 'rb').read()
        add('export', f'{lang}: globaler RTF ist reines ASCII', all(b < 128 for b in raw), '')
        txt = rtf_to_text(path)
        if txt is None:
            add('export', f'{lang}: globaler RTF Inhalt (LibreOffice)', None, 'LibreOffice fehlt')
        else:
            add('export', f'{lang}: globaler RTF: Titel, Rollen, Akzente', T[283] in txt and T[288].upper() in txt and T[289].upper() in txt and 'corazón' in txt and 'Ã' not in txt, txt[:60].replace('\n', ' '))

        name, path = download(p, lambda: open_and_click('#exportPdfBtn'), C, f'{lang}-global')
        head = open(path, 'rb').read(5)
        if head != b'%PDF-':
            add('export', f'{lang}: globaler PDF-Export', False, 'keine PDF-Datei (reportlab auf dem Rechner/Server?)')
        else:
            txt = pdf_text(path)
            if txt is None:
                add('export', f'{lang}: globaler PDF-Export (nur Format)', None, 'pdftotext fehlt - Inhalt nicht geprueft')
            else:
                ok = T[283] in txt and T[294] in txt and T[302] in txt and T[303] in txt and 'corazón' in txt
                add('export', f'{lang}: globaler PDF (Titel, Statistik, Index, Verlauf, Akzente)', ok, txt.strip().split('\n')[0].strip())
                add('export', f'{lang}: PDF ohne Emoji-Kasten (Ersatz "?")', '😊' not in txt, '')

        # PDF-Einzelexport
        name, path = download(p, lambda: p.evaluate(f'exportSingleAsPdf("{mid}")'), C, f'{lang}-single')
        if open(path, 'rb').read(5) == b'%PDF-':
            txt = pdf_text(path)
            if txt is not None:
                add('export', f'{lang}: Einzel-PDF in {lang} (Ueberschriften)', T[303] in txt and f'{T[304]} 1' in txt, txt.strip().split('\n')[0].strip())
        else:
            add('export', f'{lang}: Einzel-PDF', False, 'keine PDF-Datei')
        close(p)
    C.mock.chat_text = Mock(None, True, None).chat_text


# ---------------------------------------------------------------------------
# Gruppe: speicher
# ---------------------------------------------------------------------------

def open_sessions(p):
    """'Chat-Verlauf laden' steckt im Export-Menue."""
    p.click('#exportButton')
    p.click('#loadSessionBtn')


@test('speicher')
def t_speicher(C):
    p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'})
    send(p, 'Erste Frage')
    p.wait_for_timeout(300)
    open_sessions(p)
    p.wait_for_selector('#sessionsList .session-item')
    n = p.eval_on_selector_all('#sessionsList .session-item', 'e => e.length')
    prev = p.inner_text('#sessionsList .session-preview')
    add('speicher', 'Sitzungsliste zeigt gespeicherten Chat', n == 1 and 'Erste Frage' in prev, f'{n} Eintraege; "{prev[:30]}"')
    p.click('#closeSessions')
    p.click('#newChatButton')
    p.wait_for_timeout(300)
    cleared = len(chat_texts(p)) <= 1
    open_sessions(p)
    p.wait_for_selector('#sessionsList .session-item')
    p.click('#sessionsList .session-load-btn')
    p.wait_for_timeout(500)
    restored = p.evaluate('contextHistory.messages.length')
    add('speicher', 'Chat laden stellt die Nachrichten wieder her', restored == 2, f'{restored} Nachrichten')
    open_sessions(p)
    p.wait_for_selector('#sessionsList .session-item')
    p.click('#sessionsList .session-delete-btn')
    p.wait_for_timeout(300)
    add('speicher', 'Chat loeschen entfernt ihn (Server und Liste)', not C.mock.sessions and p.eval_on_selector_all('#sessionsList .session-item', 'e => e.length') == 0, f'Server: {len(C.mock.sessions)}')
    close(p)

    p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'})
    p.dialog_answer = 'Mein Prompt'
    p.fill('#input', 'Das ist ein wiederverwendbarer Prompt')
    p.click('#saveBookmarkButton')
    p.wait_for_timeout(400)
    add('speicher', 'Lesezeichen speichern', len(C.mock.bookmarks) == 1 and list(C.mock.bookmarks.values())[0]['title'] == 'Mein Prompt', json.dumps([b['title'] for b in C.mock.bookmarks.values()]))
    p.fill('#input', '')
    p.click('#bookmarksButton')
    p.wait_for_selector('#bookmarksList .session-item')
    add('speicher', 'Lesezeichenliste zeigt Titel', 'Mein Prompt' in p.inner_text('#bookmarksList'), '')
    p.click('#bookmarksList .session-load-btn')
    p.wait_for_timeout(300)
    add('speicher', 'Lesezeichen laden fuellt das Eingabefeld', p.input_value('#input') == 'Das ist ein wiederverwendbarer Prompt', p.input_value('#input')[:40])
    p.click('#bookmarksButton')
    p.wait_for_selector('#bookmarksList .session-item')
    p.click('#bookmarksList .session-delete-btn')
    p.wait_for_timeout(300)
    add('speicher', 'Lesezeichen loeschen', not C.mock.bookmarks, f'{len(C.mock.bookmarks)} uebrig')
    close(p)


# ---------------------------------------------------------------------------
# Gruppe: dateien
# ---------------------------------------------------------------------------

@test('dateien')
def t_dateien(C):
    p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'})
    f = os.path.join(C.tmpdir, 'notiz.txt')
    open(f, 'w', encoding='utf-8').write('Geheimer Dateiinhalt 4711 mit Umlauten äöü')
    p.set_input_files('#fileUpload', f)
    p.wait_for_selector('#fileInfo.visible', timeout=10000)
    info = p.inner_text('#fileInfo')
    add('dateien', 'Textdatei: Name erscheint in der Dateianzeige', 'notiz.txt' in info, info[:60].replace('\n', ' '))
    send(p, 'Fasse zusammen')
    last = C.mock.requests[-1][1]['messages'][-1]['content'] if C.mock.requests else ''
    add('dateien', 'Textdatei: Inhalt wird mit der Frage gesendet', '4711' in last and 'Fasse zusammen' in last, last[:60].replace('\n', ' '))
    close(p)

    p = new_page(C, {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'})
    exe = os.path.join(C.tmpdir, 'harmlos.txt')
    open(exe, 'wb').write(b'\x7fELF\x02\x01\x01\x00' + b'\x00' * 64)
    p.set_input_files('#fileUpload', exe)
    p.wait_for_timeout(800)
    err = p.query_selector('#fileInfo .pdf-error')
    add('dateien', 'ELF-Datei (als .txt getarnt) wird abgelehnt', err is not None, (err.inner_text()[:60].replace('\n', ' ') if err else 'keine Ablehnung'))
    close(p)


# ---------------------------------------------------------------------------
# Testdateien erzeugen (ohne Zusatzpakete)
# ---------------------------------------------------------------------------

def make_png(path, w=8, h=8):
    """Kleines gueltiges PNG (rote Flaeche). Rueckgabe: Bytes."""
    raw = b''.join(b'\x00' + b'\xff\x00\x00' * w for _ in range(h))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))
    open(path, 'wb').write(data)
    return data


def make_pdf(path, text):
    """Einseitiges PDF mit einer Textzeile (nur ASCII)."""
    stream = ('BT /F1 18 Tf 72 720 Td (%s) Tj ET' % text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')).encode('latin-1')
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>',
            b'<< /Length %d >>\nstream\n' % len(stream) + stream + b'\nendstream',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    out = b'%PDF-1.4\n'
    offs = []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += b'%d 0 obj\n' % i + o + b'\nendobj\n'
    xref = len(out)
    out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1)
    for o in offs:
        out += b'%010d 00000 n \n' % o
    out += b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, xref)
    open(path, 'wb').write(out)


IMG_MODEL = {'apiService': 'deepseek', 'selectedModel': 'deepseek-flash'}                       # kann Bilder
TXT_MODEL = {'apiService': 'groq', 'groqTier': 'free', 'selectedModel': 'openai/gpt-oss-120b'}   # nur Text
AUDIO_MODEL = {'apiService': 'google', 'googleTier': 'free', 'selectedModel': 'gemini-3.8-flash'}


def last_payload(C):
    return C.mock.requests[-1][1] if C.mock.requests else {}


# ---------------------------------------------------------------------------
# Bild- und PDF-Upload
# ---------------------------------------------------------------------------

@test('upload')
def t_upload(C):
    png_path = os.path.join(C.tmpdir, 'bild.png')
    png = make_png(png_path)

    # Bild mit bildfaehigem Modell
    p = new_page(C, IMG_MODEL)
    p.set_input_files('#fileUpload', png_path)
    p.wait_for_selector('#fileInfo.visible', timeout=10000)
    info = p.inner_text('#fileInfo')
    add('upload', 'Bild: Name erscheint in der Dateianzeige', 'bild.png' in info, info[:60].replace('\n', ' '))
    send(p, 'Was ist auf dem Bild?')
    pl = last_payload(C)
    got = base64.b64decode(pl.get('image_data', '') or '')
    add('upload', 'Bild: Daten und Typ gehen an den Anbieter', got == png and pl.get('image_mime_type') == 'image/png',
        f"{len(got)} Bytes, {pl.get('image_mime_type')}")
    close(p)

    # Bild entfernen -> nicht mehr gesendet
    p = new_page(C, IMG_MODEL)
    p.set_input_files('#fileUpload', png_path)
    p.wait_for_selector('#removeFile', timeout=10000)
    p.click('#removeFile')
    vis = p.evaluate('document.getElementById("fileInfo").classList.contains("visible")')
    send(p, 'Nur Text')
    add('upload', 'Bild: Entfernen-Knopf, danach kein Bild im Request', not vis and 'image_data' not in last_payload(C),
        f'Anzeige sichtbar={vis}')
    close(p)

    # Bild mit reinem Textmodell -> Hinweis (ID 239), nichts wird gesendet
    p = new_page(C, TXT_MODEL)
    p.set_input_files('#fileUpload', png_path)
    p.wait_for_timeout(600)
    want = tx(C, 'en', 239)
    send(p, 'Hallo')
    add('upload', 'Bild bei Textmodell: Hinweis (ID 239)', want in p.dialogs, (p.dialogs[0][:60] if p.dialogs else 'kein Hinweis'))
    add('upload', 'Bild bei Textmodell: kein Bild im Request', 'image_data' not in last_payload(C), '')
    close(p)

    # nicht erlaubte Endung
    p = new_page(C, IMG_MODEL)
    z = os.path.join(C.tmpdir, 'daten.zip')
    open(z, 'wb').write(b'PK\x03\x04' + b'\x00' * 40)
    p.set_input_files('#fileUpload', z)
    p.wait_for_timeout(600)
    msg = p.dialogs[0] if p.dialogs else ''
    vis = p.evaluate('document.getElementById("fileInfo").classList.contains("visible")')
    add('upload', 'Falsche Endung (.zip): Hinweis ID 10 mit Endung', '.zip' in msg and msg.startswith(tx(C, 'en', 10).split('{0}')[0]), msg[:70])
    add('upload', 'Falsche Endung (.zip): nichts uebernommen', not vis, f'sichtbar={vis}')
    close(p)

    # PDF
    pdf_path = os.path.join(C.tmpdir, 'bericht.pdf')
    make_pdf(pdf_path, 'Geheimer PDF-Inhalt 4711')
    p = new_page(C, IMG_MODEL)
    if p.evaluate('typeof pdfjsLib') == 'undefined':
        add('upload', 'PDF: Text auslesen und mitsenden', None, 'pdf.js nicht geladen (CDN offline?) - Option --pdfjs=DIR')
        close(p)
        return
    p.set_input_files('#fileUpload', pdf_path)
    try:
        p.wait_for_selector('#removeFile, .pdf-error', timeout=30000)
    except Exception:
        pass
    info = p.inner_text('#fileInfo')
    err = p.query_selector('#fileInfo .pdf-error')
    add('upload', 'PDF: Text wird ausgelesen (Anzeige ID 35)', err is None and 'bericht.pdf' in info and p.query_selector('#removeFile') is not None,
        info[:70].replace('\n', ' '))
    send(p, 'Fasse das PDF zusammen')
    msgs = last_payload(C).get('messages', [])
    txt = msgs[-1]['content'] if msgs else ''
    add('upload', 'PDF: Inhalt wird mit der Frage gesendet', 'Geheimer PDF-Inhalt 4711' in txt and 'Fasse das PDF zusammen' in txt,
        txt[:70].replace('\n', ' '))
    close(p)

    # defektes PDF -> Fehleranzeige statt Absturz
    bad = os.path.join(C.tmpdir, 'kaputt.pdf')
    open(bad, 'wb').write(b'%PDF-1.4\nDas ist kein PDF\n')
    p = new_page(C, IMG_MODEL)
    p.set_input_files('#fileUpload', bad)
    p.wait_for_selector('.pdf-error, #removeFile', timeout=30000)
    add('upload', 'Defektes PDF: Fehlermeldung statt Absturz', p.query_selector('#fileInfo .pdf-error') is not None and not p.errors,
        (p.inner_text('#fileInfo')[:70].replace('\n', ' ')))
    close(p)


# ---------------------------------------------------------------------------
# Zwischenablage
# ---------------------------------------------------------------------------

PASTE_TEXT_JS = """(text) => { const dt = new DataTransfer(); dt.setData('text/plain', text);
    const e = new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true});
    document.getElementById('input').dispatchEvent(e); return e.defaultPrevented; }"""

PASTE_IMAGE_JS = """(b64) => { const bin = atob(b64); const u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    const dt = new DataTransfer(); dt.items.add(new File([u8], 'zwischenablage.png', {type: 'image/png'}));
    const e = new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true});
    document.getElementById('input').dispatchEvent(e); return e.defaultPrevented; }"""


def overlay_visible(p):
    return p.evaluate('getComputedStyle(document.getElementById("pasteOverlay")).display') != 'none'


@test('zwischenablage')
def t_zwischenablage(C):
    # --- Copy-Knopf unter der Antwort ---
    p = new_page(C, IMG_MODEL)
    send(p, 'Hallo')
    p.locator('#chat .feedback-btn', has_text=tx(C, 'en', 217)).first.dispatch_event('click')
    p.wait_for_timeout(400)
    try:
        clip = p.evaluate('navigator.clipboard.readText()')
    except Exception as e:
        clip = None
        add('zwischenablage', 'Copy-Knopf: Antworttext in der Zwischenablage', None, f'Zwischenablage nicht lesbar: {str(e)[:60]}')
    if clip is not None:
        add('zwischenablage', 'Copy-Knopf: Antworttext in der Zwischenablage', clip == C.mock.chat_text, clip[:50])
        label = p.locator('#chat .feedback-btn.copied').first.inner_text() if p.query_selector('#chat .feedback-btn.copied') else ''
        add('zwischenablage', 'Copy-Knopf: Bestaetigung (ID 14)', label.strip() == tx(C, 'en', 14), label.strip())

        # --- Export "Copy to clipboard" ---
        p.click('#exportButton')
        p.click('#exportClipboardBtn')
        p.wait_for_timeout(400)
        clip = p.evaluate('navigator.clipboard.readText()')
        want = [tx(C, 'en', 283).upper(), tx(C, 'en', 288).upper(), tx(C, 'en', 289).upper(), 'Hallo', C.mock.chat_text]
        missing = [w for w in want if w not in clip]
        add('zwischenablage', 'Export "Copy to clipboard": Kopf, Rollen und Chat', not missing, 'fehlt: ' + ', '.join(missing) if missing else f'{len(clip)} Zeichen')
        lbl = p.inner_text('#exportButton')
        add('zwischenablage', 'Export "Copy to clipboard": Bestaetigung am Knopf (ID 14)', tx(C, 'en', 14) in lbl, ' '.join(lbl.split()))
    close(p)

    # --- Text einfuegen ---
    text = 'Eingefuegter Text mit Umlauten äöü und ¿Qué?'
    p = new_page(C, IMG_MODEL)
    prevented = p.evaluate(PASTE_TEXT_JS, text)
    p.wait_for_timeout(300)
    prev = p.inner_text('#pastePreview')
    add('zwischenablage', 'Text einfuegen: Auswahldialog mit Vorschau', overlay_visible(p) and prev == text and prevented, prev[:50])
    p.click('#pasteAtCursorBtn')
    val = p.input_value('#input')
    add('zwischenablage', 'Text einfuegen: "Am Cursor einfuegen"', val == text and not overlay_visible(p), val[:50])

    p.evaluate(PASTE_TEXT_JS, 'Zweiter Text')
    p.wait_for_timeout(300)
    p.click('#pasteCancelBtn')
    add('zwischenablage', 'Text einfuegen: Abbrechen aendert nichts', p.input_value('#input') == text and not overlay_visible(p), '')

    p.evaluate(PASTE_TEXT_JS, 'Als Datei angehaengter Inhalt 8815')
    p.wait_for_timeout(300)
    p.click('#pasteAsFileBtn')
    info = p.inner_text('#fileInfo')
    send(p, 'Was steht drin?')
    msgs = last_payload(C).get('messages', [])
    last = msgs[-1]['content'] if msgs else ''
    add('zwischenablage', 'Text einfuegen: "Als Datei anhaengen" und senden', '8815' in last and 'Was steht drin?' in last and not overlay_visible(p),
        info[:50].replace('\n', ' '))
    close(p)

    # --- Dateipfade einfuegen -> Hinweis ID 240, kein Dialog ---
    p = new_page(C, IMG_MODEL)
    p.evaluate(PASTE_TEXT_JS, '/home/user/a.txt\n/home/user/b.txt')
    p.wait_for_timeout(300)
    add('zwischenablage', 'Dateipfade einfuegen: Hinweis (ID 240)', tx(C, 'en', 240) in p.dialogs and not overlay_visible(p),
        (p.dialogs[0][:50] if p.dialogs else 'kein Hinweis'))
    close(p)

    # --- Bild einfuegen ---
    png_path = os.path.join(C.tmpdir, 'clip.png')
    png = make_png(png_path)
    b64 = base64.b64encode(png).decode()
    p = new_page(C, IMG_MODEL)
    p.evaluate(PASTE_IMAGE_JS, b64)
    p.wait_for_selector('#clipboardImagePreview.visible', timeout=10000)
    info = p.inner_text('#clipboardImageInfo')
    add('zwischenablage', 'Bild einfuegen: Vorschau (ID 231)', info.startswith(tx(C, 'en', 231)), info)
    send(p, 'Beschreibe das Bild')
    pl = last_payload(C)
    add('zwischenablage', 'Bild einfuegen: Daten gehen an den Anbieter', base64.b64decode(pl.get('image_data', '') or '') == png and pl.get('image_mime_type') == 'image/png',
        f"{pl.get('image_mime_type')}")
    close(p)

    p = new_page(C, IMG_MODEL)
    p.evaluate(PASTE_IMAGE_JS, b64)
    p.wait_for_selector('#clipboardImagePreview.visible', timeout=10000)
    p.click('#clipboardImageRemove')
    vis = p.evaluate('document.getElementById("clipboardImagePreview").classList.contains("visible")')
    send(p, 'Nur Text')
    add('zwischenablage', 'Bild einfuegen: Entfernen-Knopf', not vis and 'image_data' not in last_payload(C), f'Vorschau sichtbar={vis}')
    close(p)

    p = new_page(C, TXT_MODEL)
    p.evaluate(PASTE_IMAGE_JS, b64)
    p.wait_for_timeout(500)
    add('zwischenablage', 'Bild einfuegen bei Textmodell: Hinweis (ID 239)', tx(C, 'en', 239) in p.dialogs, (p.dialogs[0][:50] if p.dialogs else 'kein Hinweis'))
    close(p)


# ---------------------------------------------------------------------------
# Mikrofon (Chromium-Fake-Mikrofon)
# ---------------------------------------------------------------------------

@test('mikrofon')
def t_mikrofon(C):
    p = new_page(C, AUDIO_MODEL)
    btn = lambda: p.inner_text('#audioButton').strip()
    add('mikrofon', 'Aufnahme-Knopf sichtbar, Beschriftung (ID 247)', btn() == tx(C, 'en', 247) and p.is_visible('#audioButton'), btn())
    p.click('#audioButton')
    try:
        p.wait_for_function(f'document.getElementById("audioButton").textContent.trim() === {json.dumps(tx(C, "en", 248))}', timeout=8000)
        rec = True
    except Exception:
        rec = False
    add('mikrofon', 'Aufnahme startet (Knopf zeigt "Stopp", ID 248)', rec and 'active' in (p.get_attribute('#audioButton', 'class') or ''), btn())
    if not rec:
        close(p)
        return
    p.wait_for_timeout(1500)
    p.click('#audioButton')
    try:
        p.wait_for_function('document.getElementById("removeAudio")', timeout=10000)
        done = True
    except Exception:
        done = False
    info = p.inner_text('#fileInfo')
    add('mikrofon', 'Aufnahme beendet: Hinweis (ID 249) und Entfernen-Knopf', done and tx(C, 'en', 249) in info and btn() == tx(C, 'en', 247), info[:50].replace('\n', ' '))
    send(p, 'Was wurde gesagt?')
    pl = last_payload(C)
    audio = pl.get('audio_data') or ''
    add('mikrofon', 'Audio geht an den Anbieter (Daten + Typ audio/...)', len(audio) > 100 and str(pl.get('audio_mime_type', '')).startswith('audio/'),
        f"{len(audio)} Zeichen base64, {pl.get('audio_mime_type')}")
    close(p)

    # Aufnahme verwerfen
    p = new_page(C, AUDIO_MODEL)
    p.click('#audioButton')
    p.wait_for_timeout(1200)
    p.click('#audioButton')
    p.wait_for_function('document.getElementById("removeAudio")', timeout=10000)
    p.click('#removeAudio')
    vis = p.evaluate('document.getElementById("fileInfo").classList.contains("visible")')
    send(p, 'Nur Text')
    add('mikrofon', 'Aufnahme verwerfen: kein Audio im Request', not vis and 'audio_data' not in last_payload(C), f'Anzeige sichtbar={vis}')
    close(p)

    # Zugriff verweigert -> Meldung ID 281
    p = new_page(C, AUDIO_MODEL)
    p.evaluate("() => { navigator.mediaDevices.getUserMedia = () => Promise.reject(new DOMException('Permission denied', 'NotAllowedError')); }")
    p.click('#audioButton')
    p.wait_for_timeout(600)
    add('mikrofon', 'Zugriff verweigert: Meldung (ID 281)', tx(C, 'en', 281) in p.dialogs and 'active' not in (p.get_attribute('#audioButton', 'class') or ''),
        (p.dialogs[0][:50] if p.dialogs else 'keine Meldung'))
    close(p)

    # keine Mikrofon-Schnittstelle (z.B. unsichere Verbindung) -> Meldung ID 280
    p = new_page(C, AUDIO_MODEL)
    p.evaluate("() => { Object.defineProperty(navigator, 'mediaDevices', {get: () => undefined}); }")
    p.click('#audioButton')
    p.wait_for_timeout(400)
    add('mikrofon', 'Keine Mikrofon-Schnittstelle: Meldung (ID 280)', tx(C, 'en', 280) in p.dialogs, (p.dialogs[0][:50] if p.dialogs else 'keine Meldung'))
    close(p)


# ---------------------------------------------------------------------------
# Kompressor (Kontext-Komprimierung)
# ---------------------------------------------------------------------------

HF_SETTINGS = {'apiService': 'huggingface', 'hfTier': 'free', 'selectedModel': 'Qwen/Qwen2.5-72B-Instruct',
               'compressorEnabled': True, 'compressorService': 'deepseek', 'compressorModel': 'deepseek-flash'}
BIG_TEXT = ('Lorem ipsum dolor sit amet. ' * 14500)[:400000]    # ~100000 Tokens = ~78 % von 128000


@test('kompressor')
def t_kompressor(C):
    # normaler Fall
    p = new_page(C, HF_SETTINGS)
    send(p, 'Erste Frage')
    send(p, 'Zweite Frage')
    add('kompressor', 'Kleiner Chat: keine Komprimierung', len(C.mock.compress_calls) == 0, f'{len(C.mock.compress_calls)} Aufrufe')
    send(p, BIG_TEXT)
    calls = C.mock.compress_calls
    ok = len(calls) == 1
    add('kompressor', 'Ab 70 % Auslastung: Kompressor wird einmal aufgerufen', ok, f'{len(calls)} Aufrufe')
    if ok:
        c = calls[0]
        add('kompressor', 'Kompressor-Anfrage: aeltere Haelfte, Anbieter und Modell',
            len(c.get('messages', [])) == 2 and c.get('compressorService') == 'deepseek' and c.get('compressorModel') == 'deepseek-flash',
            f"{len(c.get('messages', []))} Nachrichten, {c.get('compressorService')}/{c.get('compressorModel')}")
    pl = last_payload(C)
    msgs = pl.get('messages', [])
    system = msgs[0]['content'] if msgs else ''
    add('kompressor', 'Zusammenfassung steckt im System-Prompt der Chat-Anfrage',
        'Mock-Zusammenfassung' in system and 'COMPRESSED CONTEXT' in system, f'{len(msgs)} Nachrichten')
    add('kompressor', 'Alte Nachrichten ersetzt (System + 3 Nachrichten)', len(msgs) == 4 and msgs[-1]['content'] == BIG_TEXT, f'{len(msgs)} Nachrichten')
    info = p.inner_text('#compressorInfo').strip()
    warn = 'warning' in (p.get_attribute('#compressorInfo', 'class') or '')
    banner = p.evaluate('getComputedStyle(document.getElementById("kompressorBanner")).display')
    add('kompressor', 'Anzeige nach Komprimierung (ID 46), Banner weg', bool(info) and not warn and banner == 'none', info[:60])
    close(p)

    # Kompressor-Fehler: Chat laeuft weiter, Warnung (ID 47)
    p = new_page(C, HF_SETTINGS)
    C.mock.compress_reply = (500, {'error': 'kaputt'})
    send(p, 'Erste Frage')
    send(p, 'Zweite Frage')
    send(p, BIG_TEXT)
    info = p.inner_text('#compressorInfo').strip()
    warn = 'warning' in (p.get_attribute('#compressorInfo', 'class') or '')
    answered = chat_texts(p) and chat_texts(p)[-1] == C.mock.chat_text
    add('kompressor', 'Kompressor-Fehler: Warnung (ID 47) mit HTTP 500', warn and 'HTTP 500' in info, info[:60])
    add('kompressor', 'Kompressor-Fehler: Chat wird trotzdem beantwortet', bool(answered), '')
    close(p)

    # abgeschaltet
    p = new_page(C, dict(HF_SETTINGS, compressorEnabled=False))
    send(p, 'Erste Frage')
    send(p, 'Zweite Frage')
    send(p, BIG_TEXT)
    add('kompressor', 'Abgeschaltet: kein Aufruf trotz hoher Auslastung', len(C.mock.compress_calls) == 0, f'{len(C.mock.compress_calls)} Aufrufe')
    close(p)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Voraussetzungen pruefen (--check und automatisch vor jedem Lauf)
# ---------------------------------------------------------------------------

GUIDE_VENV = (
    '  sudo apt install python3-venv                    # falls "python3 -m venv" fehlschlaegt\n'
    '  python3 -m venv ~/.venvs/webtest\n'
    '  ~/.venvs/webtest/bin/pip install playwright\n'
    '  ~/.venvs/webtest/bin/playwright install chromium\n'
    '  Danach immer mit ~/.venvs/webtest/bin/python aufrufen.')


def check_requirements(url=None, insecure=False, launch=True, vpn_ip=VPN_IP, ping=True, pdfjs=None):
    """Prueft die Zusatzsoftware. Rueckgabe: (Pflicht_fehlt, Optional_fehlt, Zeilen)."""
    rows = []   # (Status, Name, Detail, Anleitung)

    def row(status, name, detail='', how=''):
        rows.append((status, name, detail, how))

    v = sys.version_info
    if v >= (3, 8):
        row('OK', 'Python', f'{v.major}.{v.minor}.{v.micro} ({sys.executable})')
    else:
        row('FEHLT', 'Python >= 3.8', f'{v.major}.{v.minor}', 'sudo apt install python3')

    pw_ok = sync_playwright is not None
    if pw_ok:
        try:
            from importlib.metadata import version
            ver = version('playwright')
        except Exception:
            ver = '?'
        row('OK', 'Playwright (Python-Modul)', ver)
    else:
        row('FEHLT', 'Playwright (Python-Modul)', 'import schlaegt fehl - falsches Python?', GUIDE_VENV)

    if pw_ok and launch:
        try:
            with sync_playwright() as pw:
                exe = pw.chromium.executable_path
                if not os.path.exists(exe):
                    row('FEHLT', 'Chromium (Browser fuer Playwright)', 'nicht installiert',
                        '  ~/.venvs/webtest/bin/playwright install chromium')
                else:
                    b = pw.chromium.launch(headless=True)
                    ver = b.version
                    b.close()
                    row('OK', 'Chromium (Browser fuer Playwright)', f'{ver}')
        except Exception as e:
            msg = str(e)
            if 'install-deps' in msg or 'shared libraries' in msg or 'Host system is missing' in msg:
                row('FEHLT', 'Chromium: Systembibliotheken', 'Browser startet nicht',
                    '  sudo ~/.venvs/webtest/bin/playwright install-deps chromium')
            elif "Executable doesn't exist" in msg or 'playwright install' in msg:
                row('FEHLT', 'Chromium (Browser fuer Playwright)', 'nicht installiert',
                    '  ~/.venvs/webtest/bin/playwright install chromium')
            else:
                row('FEHLT', 'Chromium startet nicht', msg.strip().splitlines()[0][:120],
                    '  ~/.venvs/webtest/bin/playwright install chromium\n'
                    '  sudo ~/.venvs/webtest/bin/playwright install-deps chromium')

    if not os.path.exists(os.path.join(WEBROOT, 'index.html')):
        row('FEHLT', 'Repo-Kopie der Webseite', f'{WEBROOT}/index.html fehlt',
            '  Skript aus dem Repo starten: cd ~/Desktop/ChatBoot/multi-llm-chat')
    else:
        row('OK', 'Repo-Kopie der Webseite', WEBROOT)

    if url and ping:
        ok, detail = vpn_probe(vpn_ip)
        if ok:
            row('OK', f'VPN-Tunnel (TCP {vpn_ip})', detail)
        else:
            how = ('  VPN-Verbindung starten/pruefen; ohne laufenden Tunnel ist der Server nicht erreichbar.\n'
                   '  Manuell testen: nc -vz -w 3 ' + vpn_ip + ' 443\n'
                   '  Nur lokale Repo-Kopie testen (ohne Server): --url weglassen.\n'
                   '  Test weglassen: --no-vpn')
            row('FEHLT', f'VPN-Tunnel (TCP {vpn_ip})', detail, how)

    if url:
        import ssl
        import urllib.request
        ctx = ssl._create_unverified_context() if insecure else None
        try:
            with urllib.request.urlopen(url, timeout=15, context=ctx) as r:
                row('OK', 'Server erreichbar', f'{url} -> HTTP {r.status}')
        except Exception as e:
            row('FEHLT', 'Server erreichbar', f'{url}: {str(e)[:100]}',
                '  VPN verbunden? Domain statt IP verwenden (sonst Zertifikatswarnung), '
                'notfalls --insecure')

    # Nur fuer den lokalen Modus Pflicht: dort laufen die Export-Skripte als Prozess
    local = not url
    py = '/usr/bin/python3' if os.path.exists('/usr/bin/python3') else sys.executable
    r = subprocess.run([py, '-c', 'import reportlab; print(reportlab.Version)'], capture_output=True)
    if r.returncode == 0:
        row('OK', 'reportlab (fuer PDF-Export, in ' + py + ')', r.stdout.decode().strip())
    elif local:
        row('FEHLT', 'reportlab (fuer PDF-Export, in ' + py + ')', 'im lokalen Modus laufen die Export-Skripte hier',
            '  sudo apt install python3-reportlab')
    else:
        row('OK', 'reportlab (fuer PDF-Export)', 'nicht installiert - bei --url nicht noetig (PDF entsteht auf dem Server)')

    # pdf.js fuer den PDF-Upload-Test: kommt vom CDN (oder lokal mit --pdfjs=DIR)
    if pdfjs:
        miss = [f for f in ('pdf.min.js', 'pdf.worker.min.js') if not os.path.exists(os.path.join(pdfjs, f))]
        if miss:
            row('OPTIONAL', 'pdf.js lokal (--pdfjs)', 'fehlt in ' + pdfjs + ': ' + ', '.join(miss),
                '  cd /tmp && npm install pdfjs-dist@3.11.174\n'
                '  --pdfjs=/tmp/node_modules/pdfjs-dist/build')
        else:
            row('OK', 'pdf.js lokal (--pdfjs)', pdfjs)
    else:
        import urllib.request
        try:
            urllib.request.urlopen(urllib.request.Request(
                'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js', method='HEAD'), timeout=6)
            row('OK', 'pdf.js vom CDN erreichbar (PDF-Upload-Test)', 'cdnjs.cloudflare.com')
        except Exception as e:
            row('OPTIONAL', 'pdf.js vom CDN erreichbar (PDF-Upload-Test)', 'ohne: PDF-Upload-Test wird uebersprungen (SKIP)',
                '  Internetzugang pruefen, oder pdf.js lokal bereitstellen:\n'
                '  cd /tmp && npm install pdfjs-dist@3.11.174\n'
                '  und mit --pdfjs=/tmp/node_modules/pdfjs-dist/build aufrufen')

    if shutil.which('pdftotext'):
        row('OK', 'pdftotext (PDF-Inhalt pruefen)', shutil.which('pdftotext'))
    else:
        row('OPTIONAL', 'pdftotext (PDF-Inhalt pruefen)', 'ohne: nur Dateiformat geprueft (SKIP)',
            '  sudo apt install poppler-utils')

    so = shutil.which('soffice') or shutil.which('libreoffice')
    if so:
        row('OK', 'LibreOffice (RTF-Inhalt pruefen)', so)
    else:
        row('OPTIONAL', 'LibreOffice (RTF-Inhalt pruefen)', 'ohne: RTF nur als ASCII geprueft (SKIP)',
            '  sudo apt install libreoffice-writer')

    must = [r_ for r_ in rows if r_[0] == 'FEHLT']
    opt = [r_ for r_ in rows if r_[0] == 'OPTIONAL']
    return must, opt, rows


def print_requirements(rows, quiet_ok=False):
    for status, name, detail, how in rows:
        if status == 'OK' and quiet_ok:
            continue
        mark = {'OK': 'OK      ', 'FEHLT': 'FEHLT   ', 'OPTIONAL': 'OPTIONAL'}[status]
        print(f'  {mark} {name}' + (f'  [{detail}]' if detail else ''))
        if status != 'OK' and how:
            print('           Loesung:')
            for line in how.splitlines():
                print('           ' + line)


def main():
    args = sys.argv[1:]
    opt = lambda k: next((a.split('=', 1)[1] for a in args if a.startswith(k + '=')), None)
    if '--list' in args:
        for g, fn in TESTS:
            print(f'{g:12} {fn.__name__}')
        return 0
    only = opt('--only')
    only = set(only.split(',')) if only else None
    url = opt('--url')
    vpn_ip = opt('--vpn-ip') or VPN_IP

    if '--check' in args:
        print('web-test.py - Pruefung der Voraussetzungen')
        must, optl, rows = check_requirements(url, '--insecure' in args, vpn_ip=vpn_ip, ping=not NOVPN(args), pdfjs=opt('--pdfjs'))
        print_requirements(rows)
        if must:
            print(f'\n=== {len(must)} Pflicht-Voraussetzung(en) fehlen - Test kann nicht laufen ===')
            return 2
        print('\n=== Alles Noetige ist installiert' +
              (f' ({len(optl)} optionale Hilfe(n) fehlen, die zugehoerigen Pruefungen werden uebersprungen)' if optl else '') +
              ' ===')
        return 0

    if sync_playwright is None:
        print('FEHLER: Playwright ist in diesem Python nicht installiert '
              f'({sys.executable}).\nEinrichtung:\n{GUIDE_VENV}\n'
              'Pruefen: web-test.py --check')
        return 2
    if '--no-check' not in args:
        must, optl, rows = check_requirements(url, '--insecure' in args, vpn_ip=vpn_ip, ping=not NOVPN(args), pdfjs=opt('--pdfjs'))
        if must:
            print('web-test.py - Voraussetzungen fehlen:')
            print_requirements([r_ for r_ in rows if r_[0] != 'OK'])
            return 2
        if optl:
            print('Hinweis: optionale Hilfen fehlen (die zugehoerigen Pruefungen werden uebersprungen):')
            print_requirements(optl)

    C = Ctx()
    C.url_mode = bool(url)
    C.vpn_ip = vpn_ip
    C.no_vpn = NOVPN(args)
    C.insecure = '--insecure' in args
    C.keep = opt('--keep')
    C.pdfjs = opt('--pdfjs')
    if C.keep:
        os.makedirs(C.keep, exist_ok=True)
    C.tmpdir = tempfile.mkdtemp(prefix='web-test-')

    srv = None
    if url:
        C.base = url if url.endswith('/') else url + '/'
        local_for_cgi = False
        webroot_for_files = WEBROOT   # Texte/Listen aus der Repo-Kopie
    else:
        if not os.path.exists(os.path.join(WEBROOT, 'index.html')):
            print(f'FEHLER: {WEBROOT}/index.html nicht gefunden (aus dem Repo starten).')
            return 2
        srv, C.base = start_static(WEBROOT)
        local_for_cgi = True
        webroot_for_files = WEBROOT

    html = open(os.path.join(webroot_for_files, 'index.html'), encoding='utf-8').read()
    C.texts = load_texts(webroot_for_files)
    C.lists, C.cfg = load_lists(html)
    C.mock = Mock(C.base, local_for_cgi, C.keep)
    print(f'web-test.py - Ziel: {C.base} ({"Server" if url else "lokale Repo-Kopie"}), '
          f'Texte: {len(C.texts["en"])} je Sprache')

    with sync_playwright() as pw:
        C.browser = pw.chromium.launch(headless='--headed' not in args,
                                       args=['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'])
        for group, fn in TESTS:
            if only and group not in only:
                continue
            try:
                fn(C)
            except Exception as e:
                add(group, fn.__name__, False, f'Testabbruch: {type(e).__name__}: {str(e)[:160]}')
        C.browser.close()
    if srv:
        srv.shutdown()
    shutil.rmtree(C.tmpdir, ignore_errors=True)

    n = {s: sum(1 for r in RESULTS if r[2] == s) for s in ('PASS', 'FAIL', 'SKIP')}
    print(f"\n=== ZUSAMMENFASSUNG: {n['PASS']} PASS, {n['FAIL']} FAIL, {n['SKIP']} SKIP ===")
    for r in RESULTS:
        if r[2] == 'FAIL':
            print(f'  FAIL {r[0]} [{r[1]}] {r[3]}')
    return 1 if n['FAIL'] else 0


if __name__ == '__main__':
    sys.exit(main())
