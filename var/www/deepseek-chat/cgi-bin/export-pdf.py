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

# Sicherheits-Fix (26.07.2026): CORS-Wildcard durch feste Origin ersetzt,
# zusaetzlich Request-Groessenlimit gegen Missbrauch/DoS.
ALLOWED_ORIGIN = 'https://172.29.255.1'
MAX_REQUEST_SIZE = 20 * 1024 * 1024  # 20 MB (Chat kann eingebettete Bilder enthalten)

def send_response(status_code, data, content_type='application/json'):
    """Sendet HTTP-Response zurück."""
    if isinstance(data, bytes):
        # Für Binärdaten: alles über stdout.buffer schreiben
        headers = f"Status: {status_code}\r\n"
        headers += f"Content-Type: {content_type}\r\n"
        headers += f"Access-Control-Allow-Origin: {ALLOWED_ORIGIN}\r\n"
        headers += "Access-Control-Allow-Methods: POST, OPTIONS\r\n"
        headers += "Access-Control-Allow-Headers: Content-Type\r\n"
        headers += f"Content-Disposition: attachment; filename=\"deepseek-chat-export.pdf\"\r\n"
        headers += f"Content-Length: {len(data)}\r\n"
        headers += "\r\n"
        sys.stdout.buffer.write(headers.encode('utf-8'))
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    else:
        # Für JSON-Daten: normale print Ausgabe
        print(f"Status: {status_code}")
        print(f"Content-Type: {content_type}")
        print(f"Access-Control-Allow-Origin: {ALLOWED_ORIGIN}")
        print("Access-Control-Allow-Methods: POST, OPTIONS")
        print("Access-Control-Allow-Headers: Content-Type")
        print()
        print(json.dumps(data, ensure_ascii=False))
        sys.stdout.flush()

# Changelog 117 (12.10.2026): Beschriftungen kommen uebersetzt vom Frontend
# (chatData.labels, aus language.xml). Fehlen sie, gelten diese deutschen
# Standardwerte - alte Frontends funktionieren also unveraendert weiter.
DEFAULT_LABELS = {
    'title': 'Multi-LLM-Chat - Export', 'server': 'Server', 'date': 'Datum',
    'time': 'Uhrzeit', 'messages': 'Nachrichten', 'user': 'Benutzer', 'ai': 'KI',
    'exported': 'Exportiert', 'export_date': 'Export-Datum',
    'settings': 'Einstellungen', 'form_mode': '{0}-Form, Modus: {1}',
    'stats': 'Statistiken', 'total': 'Nachrichten gesamt',
    'modes': 'Verwendete Modi', 'files': 'Hochgeladene Dateien',
    'tokens': 'Geschaetzte Token-Nutzung', 'duration': 'Chat-Dauer',
    'none': 'Keine Nachrichten', 'to': 'bis', 'toc': 'Inhaltsverzeichnis',
    'history': 'Chat-Verlauf', 'message': 'Nachricht', 'unknown': 'Unbekannt',
    'footer': 'Exportiert mit Multi-LLM-Chat',
}

def get_labels(chat_data):
    """Liefert die Beschriftungen (Frontend-Labels ueberschreiben die Standardwerte)."""
    labels = dict(DEFAULT_LABELS)
    custom = chat_data.get('labels')
    if isinstance(custom, dict):
        for key, value in custom.items():
            if key in labels and isinstance(value, str) and value.strip() and len(value) <= 200:
                labels[key] = value
    return labels

def winansi_safe(value):
    """Ersetzt Zeichen, die die PDF-Standardschrift (Helvetica/WinAnsi) nicht
    darstellen kann (Emoji, CJK usw.), durch '?' statt eines schwarzen Kastens."""
    out = []
    for ch in str(value):
        try:
            ch.encode('cp1252')
            out.append(ch)
        except UnicodeEncodeError:
            out.append('?')
    return ''.join(out)

def pdf_text(value):
    """Maskiert Text fuer reportlab-Paragraph (Mini-HTML)."""
    return winansi_safe(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def calculate_statistics(messages, L=None):
    """Berechnet Statistiken aus den Nachrichten."""
    L = L or DEFAULT_LABELS
    total_messages = len(messages)
    user_messages = len([m for m in messages if m['role'] == 'user'])
    ai_messages = len([m for m in messages if m['role'] == 'assistant'])
    
    modes = {}
    files_count = 0
    total_tokens = 0
    
    for msg in messages:
        mode = msg.get('mode', 'chat')
        modes[mode] = modes.get(mode, 0) + 1
        if msg.get('hasFile', False):
            files_count += 1
        total_tokens += msg.get('estimatedTokens', 0)
    
    # Chat-Dauer
    if messages:
        first_time = messages[0].get('timestamp', '')
        last_time = messages[-1].get('timestamp', '')
        duration = f"{first_time} {L['to']} {last_time}"
    else:
        duration = L['none']
    
    return {
        'total': total_messages,
        'user': user_messages,
        'ai': ai_messages,
        'modes': modes,
        'files': files_count,
        'tokens': total_tokens,
        'duration': duration
    }

def create_pdf(chat_data):
    """Erstellt PDF aus Chat-Daten."""
    L = get_labels(chat_data)
    P = {k: pdf_text(v) for k, v in L.items()}
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#4dabf7'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#0056b3'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    user_style = ParagraphStyle(
        'UserMessage',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#4dabf7'),
        leftIndent=20,
        spaceAfter=6
    )
    
    ai_style = ParagraphStyle(
        'AIMessage',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#000000'),
        leftIndent=40,
        spaceAfter=12
    )
    
    stats_style = ParagraphStyle(
        'Stats',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=6
    )
    
    # Content aufbauen
    story = []
    
    # Titel
    story.append(Paragraph(P['title'], title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Server-Info
    server_info = chat_data.get('serverInfo', {})
    story.append(Paragraph(f"<b>{P['server']}:</b> {pdf_text(server_info.get('name', L['unknown']))} (IP: {pdf_text(server_info.get('ip', L['unknown']))})", styles['Normal']))
    story.append(Paragraph(f"<b>{P['export_date']}:</b> {pdf_text(chat_data.get('timestamp', L['unknown']))}", styles['Normal']))
    
    settings = chat_data.get('settings', {})
    story.append(Paragraph(f"<b>{P['settings']}:</b> " + P['form_mode'].replace('{0}', pdf_text(settings.get('addressForm', 'sie'))).replace('{1}', pdf_text(settings.get('defaultMode', 'chat'))), styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Statistiken
    messages = chat_data.get('messages', [])
    stats = calculate_statistics(messages, L)
    
    story.append(Paragraph(P['stats'], heading_style))
    story.append(Paragraph(f"<b>{P['total']}:</b> {stats['total']} ({P['user']}: {stats['user']}, {P['ai']}: {stats['ai']})", stats_style))
    
    modes_text = ", ".join([f"{mode}: {count}x" for mode, count in stats['modes'].items()])
    story.append(Paragraph(f"<b>{P['modes']}:</b> {pdf_text(modes_text)}", stats_style))
    story.append(Paragraph(f"<b>{P['files']}:</b> {stats['files']}", stats_style))
    story.append(Paragraph(f"<b>{P['tokens']}:</b> {stats['tokens']}", stats_style))
    story.append(Paragraph(f"<b>{P['duration']}:</b> {pdf_text(stats['duration'])}", stats_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Inhaltsverzeichnis
    story.append(Paragraph(P['toc'], heading_style))
    for idx, msg in enumerate(messages, 1):
        role = P['user'] if msg['role'] == 'user' else P['ai']
        preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
        preview = winansi_safe(preview).replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(f"{P['message']} {idx} ({role}): {preview}", stats_style))
    
    story.append(PageBreak())
    
    # Nachrichten
    story.append(Paragraph(P['history'], heading_style))
    
    for idx, msg in enumerate(messages, 1):
        role = P['user'] if msg['role'] == 'user' else P['ai']
        timestamp = msg.get('timestamp', '')
        mode = msg.get('mode', 'chat')
        content = winansi_safe(msg['content']).replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
        
        # Mode-Badge
        mode_color = '#28a745' if mode == 'deepthink' else '#17a2b8' if mode == 'search' else '#6c757d'
        mode_badge = f'<font color="{mode_color}">[{mode.upper()}]</font>'
        
        # Nachricht
        style = user_style if msg['role'] == 'user' else ai_style
        story.append(Paragraph(f"<b>{P['message']} {idx} - {role}</b> {mode_badge} <i>({pdf_text(timestamp)})</i>", heading_style))
        story.append(Paragraph(content, style))
        story.append(Spacer(1, 0.3*cm))
    
    # PDF erstellen
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def main():
    try:
        request_method = os.environ.get('REQUEST_METHOD', '')

        # OPTIONS Request
        if request_method == 'OPTIONS':
            send_response(200, {'status': 'ok'})
            return

        # Nur POST erlaubt
        if request_method != 'POST':
            send_response(405, {'error': f'Methode nicht erlaubt: {request_method}'})
            return

        # Content-Length lesen
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        if content_length == 0:
            send_response(400, {'error': 'Leere Anfrage'})
            return

        # Sicherheits-Fix (26.07.2026): Request-Groessenlimit gegen Missbrauch/DoS
        if content_length > MAX_REQUEST_SIZE:
            send_response(413, {'error': f'Anfrage zu gross (max. {MAX_REQUEST_SIZE // (1024*1024)} MB)'})
            return

        # POST-Daten lesen
        # Fix (29.08.2026): sys.stdin.read() im Textmodus kann je nach
        # CGI-Locale Mehrbyte-UTF-8-Zeichen (z.B. Emojis) fehlerhaft dekodieren
        # und dabei ungueltige Steuerzeichen einstreuen, was json.loads() mit
        # "Invalid control character" zum Absturz bringt. Rohe Bytes lesen und
        # explizit als UTF-8 dekodieren umgeht das CGI-Locale-Problem komplett.
        post_data = sys.stdin.buffer.read(content_length).decode('utf-8')
        request_data = json.loads(post_data)
        
        chat_data = request_data.get('chatData')
        if not chat_data:
            send_response(400, {'error': 'Keine Chat-Daten'})
            return

        # PDF erstellen
        pdf_data = create_pdf(chat_data)
        
        # PDF zurückschicken
        send_response(200, pdf_data, content_type='application/pdf')

    except json.JSONDecodeError as e:
        send_response(400, {'error': 'Ungültiges JSON', 'details': str(e)})
    except Exception as e:
        send_response(500, {'error': 'Interner Serverfehler', 'details': str(e)})

if __name__ == '__main__':
    main()



