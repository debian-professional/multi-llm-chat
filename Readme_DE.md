# Multi-LLM Chat Client – OpenAI, DeepSeek, Google Gemini, Hugging Face & GroqCloud

**Multi-LLM Chat Client** ist ein vollständig eigenständiger, lokal gehosteter Chat-Client mit Unterstützung für fünf KI-Anbieter: OpenAI, DeepSeek, Google Gemini, Hugging Face und GroqCloud. Entwickelt mit Fokus auf **Sicherheit, Einfachheit und professionelle Nutzbarkeit**, benötigt die Architektur keine exotischen Frameworks und setzt ausschliesslich auf bewährte Technologien: Apache als Webserver, Python CGI für serverseitige Logik und reines HTML/JavaScript/CSS auf der Client-Seite.

Wichtigste Highlights:
- **Multi-LLM-Unterstützung** – Wechsel zwischen OpenAI, DeepSeek, Google Gemini, Hugging Face und GroqCloud über einen Anbieter-Toggle im LLM-Einstellungs-Panel. Jeder Anbieter hat eine eigene Modellliste, Tier-Auswahl und Konfigurationsoptionen.
- **DeepSeek V4** – Vollständig migriert auf `deepseek-v4-flash` und `deepseek-v4-pro` mit 1M-Token-Kontextfenstern. Die veralteten Modellnamen `deepseek-chat` und `deepseek-reasoner` werden am 24. Juli 2026 abgeschaltet.
- **GPT-5.6-bereit** – OpenAI-Modell-Lineup aktualisiert auf die GPT-5.6-Familie (Sol, Terra, Luna) plus GPT-5.5, neben GPT-4o und GPT-4.1. Anfragen nutzen jetzt `max_completion_tokens`, den Parameter, den alle aktuellen OpenAI-Modelle verlangen.
- **Funktionierende Bild-Pipeline** – Bild-Upload und Zwischenablage-Einfügen sind für Google Gemini und OpenAI durchgängig verdrahtet: Bilder werden clientseitig base64-kodiert und als native `inline_data`-Blöcke (Gemini) bzw. `image_url`-Blöcke (OpenAI) übermittelt. Die Modell-Fähigkeits-Erkennung (`MODEL_CAPABILITIES`) ist jetzt pro Anbieter korrekt befüllt, statt für alles außer DeepSeek standardmäßig „kein Bild-Support" anzunehmen.
- **Multi-Datei-Upload** – Mehrere Dateien gleichzeitig auswählen und senden. Inhalte werden kombiniert und mit Datei-Headern und Trennzeichen als Kontext gesendet.
- **Audio-Aufnahme via Mikrofon** – Audio direkt im Browser aufnehmen und an die KI senden. Native Unterstützung durch Google Gemini (`gemini-2.5-flash`, `gemini-2.5-pro`) und OpenAI (`gpt-4o`, `gpt-4.1`). Der Aufnahme-Button erscheint automatisch nur bei audio-fähigen Modellen.
- **Einzigartiges Kontextmanagement** – Einzelne Nachrichten zusammen mit allen nachfolgenden löschen. Der Chat bleibt konsistent und die Token-Nutzung wird dynamisch neu berechnet.
- **Maximale Sicherheit** – API-Keys sind clientseitig nie sichtbar, Uploads werden via Magic-Byte-Prüfung gegen ausführbare Dateien geschützt, und Sessions werden mit restriktiven Dateiberechtigungen gespeichert.
- **Keine exotischen Frameworks** – Alles basiert auf Apache, Python 3, Bash und reinem HTML/JavaScript/CSS. Kein Node.js, kein React, keine Build-Pipeline.
- **Professionelle Exportfunktionen** – PDF, Markdown, TXT und RTF für den gesamten Chat oder einzelne Nachrichten, plus direktes Kopieren in die Zwischenablage (clientseitig, kein Server-Roundtrip).
- **Mehrsprachige Unterstützung** – Vollständige UI-Übersetzung via externer `language.xml` (Englisch, Deutsch, Spanisch, erweiterbar mit einem Custom-Sprach-Slot).
- **Kompressor (Kontext-Komprimierung)** – Automatische intelligente Komprimierung des Chat-Verlaufs wenn das Kontextfenster sich füllt. Ein zweiter LLM-Call fasst die ältesten 50% der Nachrichten zusammen und injiziert die Zusammenfassung in den System-Prompt — unbegrenzt lange Gespräche ohne Kontextverlust.
- **Guthaben- und Tageslimit-Banner** – Dauerhafte visuelle Banner bei erschöpftem Guthaben (rot, bezahlte Anbieter) und Tageslimits (blau, Free-Tier-Anbieter), jeweils mit Schliessen-Button.
- **Kontextfenster-Überschreitung** – Wenn die maximale Kontextgrösse erreicht wird, erscheint eine interaktive Box direkt im Chat mit zwei Optionen: Gespräch mit komprimiertem Kontext fortsetzen oder sauberen neuen Chat starten. Die aktuelle Session wird in beiden Fällen automatisch gespeichert.
- **Zwischenablage-Integration** – Ctrl+V-Handler mit Dialog für Text, Bilder und Schutz gegen versehentliches Einfügen von Dateipfaden.
- **Streaming-Antworten** – KI-Antworten erscheinen Token für Token, genau wie bei ChatGPT oder Claude.
- **429-Rate-Limit-Handling** – Automatischer Wiederholungsversuch mit Countdown-Anzeige für Google Gemini Free-Tier-Limits.
- **Transparente Fehlerdiagnose** – API-Fehlerantworten zeigen jetzt die tatsächliche Fehlermeldung des Anbieters (statt eines leeren Strings), sofern der Fehler keinem bekannten Guthaben-/Kontext-Muster entspricht.
- **Deploy-Verifikation** – `deploy.sh` gibt MD5-Prüfsummen jeder in die Produktion kopierten Datei aus und ermöglicht so den sofortigen Abgleich mit dem Source-Repo ohne separaten manuellen Schritt.
- **Enthaltenes Tool** – Das Skript `repo2text.sh` exportiert das gesamte Repository als einzelne Textdatei, ideal für die Arbeit mit KI-Assistenten.

---

## Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Architektur](#architektur)
- [Einzigartiges Kontextmanagement](#einzigartiges-kontextmanagement)
- [Features im Detail](#features-im-detail)
  - [Chat-Interface](#chat-interface)
  - [Streaming-Antworten](#streaming-antworten)
  - [Zwischenablage-Handler (Ctrl+V)](#zwischenablage-handler-ctrlv)
  - [Datei-Upload mit Sicherheitsprüfung](#datei-upload-mit-sicherheitsprüfung)
  - [Umlaut-Platzhalter-System](#umlaut-platzhalter-system)
  - [DeepThink-Modus](#deepthink-modus)
  - [Modellerkennung & Fähigkeiten](#modellerkennung--fähigkeiten)
  - [Bild-Unterstützung (Vision)](#bild-unterstützung-vision)
  - [Mehrsprachiges System](#mehrsprachiges-system)
  - [Einstellungen (Toggles statt Radio-Buttons)](#einstellungen-toggles-statt-radio-buttons)
  - [Session-Management](#session-management)
  - [Exportfunktionen](#exportfunktionen)
  - [Feedback-Buttons & Logging](#feedback-buttons--logging)
  - [Dynamische Kontext-Anzeige](#dynamische-kontext-anzeige)
  - [Datei-Card-Anzeige](#datei-card-anzeige)
  - [Audio-Aufnahme](#audio-aufnahme)
  - [Kompressor — Intelligente Kontext-Komprimierung](#kompressor--intelligente-kontext-komprimierung)
  - [Guthaben- und Tageslimit-Banner](#guthaben--und-tageslimit-banner)
  - [Kontextfenster-Überschreitung](#kontextfenster-überschreitung)
- [DeepSeek V4 Migration](#deepseek-v4-migration)
- [Wartung & Feature-Update vom 19. Juli 2026](#wartung--feature-update-vom-19-juli-2026)
- [Das Hilfsskript `repo2text.sh`](#das-hilfsskript-repo2textsh)
- [Sicherheitsarchitektur im Detail](#sicherheitsarchitektur-im-detail)
- [Deployment & Verwendung](#deployment--verwendung)
  - [Voraussetzungen](#voraussetzungen)
  - [Installation](#installation)
  - [Konfiguration](#konfiguration)
  - [Deploy-Skripte](#deploy-skripte)
- [Projektstruktur](#projektstruktur)
- [Modell-Konfiguration](#modell-konfiguration)
- [Design-Manifest](#design-manifest)
- [Bekannte Einschränkungen & technische Hinweise](#bekannte-einschränkungen--technische-hinweise)
- [Abhängigkeiten](#abhängigkeiten)
- [Fazit / Warum dieses Projekt heraussticht](#fazit--warum-dieses-projekt-heraussticht)

---

## Übersicht

Multi-LLM Chat Client ist eine **lokale Webanwendung**, die mit externen KI-APIs ausschliesslich über serverseitige Python-CGI-Proxy-Skripte kommuniziert. Entwickelt für eine private Debian-Serverumgebung, kann er auf jedem Linux-System mit Apache 2.4 und Python 3 laufen. Ziel war ein **sicherer, erweiterbarer und benutzerfreundlicher** Chat-Client ohne Cloud-Abhängigkeiten und mit voller Kontrolle über Daten und API-Credentials.

Das Projekt ist über mehrere Wochen aktiver Entwicklung kontinuierlich gewachsen und hat Features wie Streaming-Antworten, Session-Management, Exportfunktionen, Mehrsprachigkeit, Zwischenablage-Integration, intelligente Kontext-Komprimierung, Audio-Aufnahme und robuste Sicherheitsmassnahmen hinzugewonnen — ohne jemals externe JavaScript-Frameworks oder eine Build-Toolchain einzuführen.

Die gesamte Client-Logik befindet sich in einer einzigen `index.html`-Datei (~5.000 Zeilen). Alle UI-Texte sind in `language.xml` ausgelagert. Alle serverseitigen Operationen werden von 15 Python-CGI-Skripten in `/cgi-bin/` übernommen.

---

## Architektur

Die Architektur ist bewusst einfach, aber gut durchdacht:

### 1. Client-Schicht

- Reines HTML5/JavaScript/CSS3, via Apache ausgeliefert.
- Keine Build-Tools, kein Node.js, keine externen JavaScript-Bibliotheken (Ausnahme: PDF.js 3.11.174, via CDN geladen, für In-Browser-PDF-Textextraktion).
- Die gesamte Client-Logik — Nachrichtenverarbeitung, UI-Updates, Stream-Empfang, Sprachwechsel, Zwischenablage-Handling, Session-Management, Kontext-Schätzung — ist in einer einzigen `index.html` gekapselt.
- Alle UI-Texte werden beim Start via `fetch()` aus einer externen `language.xml` geladen. Im HTML existieren keine hardcodierten UI-Strings.
- Einstellungen werden in `localStorage` mit versionierter Schema-Migration gespeichert.

### 2. Server-Schicht

- **Apache 2.4** mit aktiviertem `mod_cgi`. HTTPS via SSL-Konfiguration erzwungen.
- **Python-3-CGI-Skripte** unter `/cgi-bin/` übernehmen alle serverseitigen Operationen:

| Skript | Funktion |
|--------|----------|
| `openai-api.py` | Streaming-Proxy zum OpenAI Chat Completions Endpoint (natives Format) |
| `deepseek-api.py` | Streaming-Proxy zum DeepSeek Chat Completions Endpoint (OpenAI-kompatibel) |
| `google-api.py` | Proxy zur Google Gemini API mit Formatkonvertierung (OpenAI ↔ Gemini) |
| `hugging-api.py` | Streaming-Proxy zum Hugging Face Inference Router (OpenAI-kompatibel) |
| `groq-api.py` | Streaming-Proxy zur GroqCloud API (OpenAI-kompatibel, LPU-Hardware) |
| `compress-context.py` | Kontext-Komprimierung — fasst älteste 50% der Nachrichten via zweitem LLM-Call zusammen |
| `deepseek-models.py` | Fragt den DeepSeek `/v1/models`-Endpoint beim Start live ab |
| `save-session.py` | POST: empfängt `{sessionId, messages}`, validiert ID, schreibt JSON auf Disk |
| `load-session.py` | GET: gibt Session-Liste mit Previews zurück; GET `?id=`: gibt vollständige Session zurück |
| `delete-session.py` | DELETE: entfernt die Session-JSON-Datei |
| `export-pdf.py` | Serverseitiger PDF-Export via ReportLab |
| `export-markdown.py` | Serverseitiger Markdown-Export |
| `export-txt.py` | Serverseitiger TXT-Export |
| `export-rtf.py` | Serverseitiger RTF-Export (keine externe Bibliothek, manuelle RTF-Kodierung) |
| `feedback-log.py` | Schreibt Like/Dislike-Feedback-Einträge ins Server-Log |
| `get-log.py` | Liest und gibt den Inhalt der Server-Log-Datei zurück |

- **API-Keys** werden ausschliesslich via Apache-Umgebungsvariablen in `/etc/apache2/envvars` bereitgestellt — `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `GOOGLE_API_KEY`, `HF_API_KEY`, `GRQ_API_KEY`. Sie sind **niemals** im Client-Code oder in HTTP-Antworten vorhanden.
- Ein einziger `ScriptAlias /cgi-bin/ /var/www/deepseek-chat/cgi-bin/` deckt alle Skripte ab — beim Hinzufügen neuer Skripte sind keine Apache-Konfigurationsänderungen nötig.

### 3. Datenspeicherung

| Pfad | Inhalt | Berechtigungen |
|------|--------|----------------|
| `/var/www/deepseek-chat/sessions/` | Chat-Session-JSON-Dateien | `chmod 700` (Verz.), `chmod 600` (Dateien) |
| `/var/www/deepseek-chat/logs/multi-llm-chat.log` | Server-Aktivitätslog (ohne API-Keys, ohne Session-Inhalte) | `www-data`-Eigentümer |
| `/var/www/deepseek-chat/kompressor/` | Komprimierungs-Ergebnisdateien (eine pro Komprimierungsrunde) | `www-data`-Eigentümer |
| Browser `localStorage` | Benutzereinstellungen (mit Versions-Migration), Sprache, Modell-Präferenzen | Nur clientseitig |
| `language.xml` | Alle UI-Texte für alle Sprachen | Via `fetch()` beim Seitenstart geladen |

### 4. Hilfsskripte

- `deploy.sh` — kopiert das Quell-Repo ins Produktionsverzeichnis, setzt korrekte Eigentümerschaft/Berechtigungen, lädt Apache neu.
- `sync-back.sh` — kopiert geänderte Dateien aus der Produktion zurück ins Quell-Repo.
- `install.sh` — installiert `deploy.sh` und `sync-back.sh` im Produktionsverzeichnis.
- `tag-release.sh` — erstellt einen Git-Tag mit automatisch inkrementierter Versionsnummer (z.B. `v0.94 → v0.95`) und pusht ihn. Führt `git fetch --tags` automatisch aus, um Konflikte mit bestehenden Remote-Tags zu vermeiden.
- `repo2text.sh` — exportiert das gesamte Repository als einzelne begrenzte Textdatei für KI-Assistenten.

---

## Einzigartiges Kontextmanagement

Eines der herausragenden Features ist die Möglichkeit, **einzelne Nachrichten zusammen mit allen nachfolgenden zu löschen**. Das geht weit über das typische "letzte Nachricht löschen" hinaus und ermöglicht die flexible Korrektur des Gesprächsverlaufs an jedem beliebigen Punkt.

**Implementierung**:
- Jede Nachricht (Benutzer & KI) erhält eine eindeutige ID (Format: `msg_N`) und wird im Array `contextHistory.messages[]` gespeichert.
- `deleteMessage(msgId)` bestimmt den Index der Zielnachricht, kürzt das Array ab diesem Index und entfernt alle folgenden DOM-Elemente (Nachrichten + Trennlinien).
- `updateContextEstimation()` berechnet sofort die geschätzte Token-Anzahl und den prozentualen Kontext-Nutzungsgrad im Header neu.
- Wenn der Kontext nach der Löschung unter den zuletzt ausgelösten Kompressor-Schwellwert fällt, wird die Kompressions-Zusammenfassung automatisch verworfen und das Schwellwert-Tracking zurückgesetzt — der Komprimierungszustand spiegelt stets den tatsächlichen Gesprächsinhalt wider.
- Die geänderte Session wird sofort via `saveSession()` automatisch gespeichert.

**Warum das einzigartig ist**: Die meisten Chat-Clients erlauben nur das Löschen der letzten Nachricht oder gar keine Verlaufsmanipulation. Hier kann der Benutzer **jeden beliebigen Punkt im Gespräch als neuen Ausgangspunkt definieren** — ideal zum Testen von Prompt-Varianten, Korrigieren von Fehlern mitten im Gespräch oder Bereinigen des Kontextfensters ohne den gesamten Chat zu verlieren.

**Regenerieren-Funktion**: Jede KI-Antwort enthält einen "Regenerieren"-Button, der die aktuelle Antwort aus Kontext und DOM entfernt und dann einen neuen API-Call auf Basis derselben Benutzernachricht und des vollständigen vorherigen Verlaufs absetzt.

---

## Features im Detail

### Chat-Interface

- **Festes Dark-Mode** — Hintergrund `#121212`, Text `#f0f0f0`, Akzent `#0056b3`. Keine Light-Mode-Option by Design.
- **Server-Header** (4 Zeilen): Server-Name (blau `#4dabf7`), interne IP-Adresse, dynamischer Kontext-Nutzungsgrad mit aktivem Modellnamen, erkannte Modell-IDs von der DeepSeek API.
- **Nachrichten-Container**: Hover-ausgelöste Aktions-Buttons (Feedback, Einzelnachrichten-Export, Löschen). Benutzernachrichten erscheinen in Blau (`#4dabf7`), KI-Antworten in Weiss auf dunklem Hintergrund.
- **Textarea**: Erweitert sich beim Fokus via CSS-Transition von 40px auf 120px. Enter sendet die Nachricht; Shift+Enter fügt einen Zeilenumbruch ein.
- **Striktes Pill-Style-Design**: border-radius 20px, Höhe 36px für alle Buttons — keine eckigen Buttons irgendwo in der UI.
- `white-space: pre-wrap` auf allen Nachrichteninhalten bewahrt die Formatierung aus KI-Antworten.
- Auto-Scroll zur neuesten Nachricht ist während und nach dem Streaming aktiv.

### Streaming-Antworten

Alle KI-Antworten werden via Server-Sent Events (SSE) **Token für Token** empfangen und angezeigt:

- Alle fünf CGI-Proxy-Skripte senden ihre jeweiligen API-Anfragen mit `stream: True` (oder äquivalent) und leiten den rohen SSE-Event-Stream direkt ohne Pufferung an den Client weiter.
- `index.html` liest den Stream via `ReadableStream`-API mit `TextDecoder`.
- Jeder empfangene Chunk wird in Echtzeit an das aktive Nachrichten-DOM-Element angehängt.
- **Technische SSE-Header** die alle CGI-Proxy-Skripte setzen:
  ```
  Content-Type: text/event-stream
  X-Accel-Buffering: no
  Cache-Control: no-cache
  ```
- Der psychologische Effekt ist erheblich: Erste Tokens erscheinen innerhalb von ~300ms statt 5–10 Sekunden auf eine vollständige Antwort zu warten.
- Sowohl `sendMessage()` als auch `handleRegenerate()` verwenden identische Streaming-Logik.

### OpenAI-Integration

- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Architektur**: Natives OpenAI Chat Completions Format — keine Formatkonvertierung nötig. SSE-Stream wird direkt von `openai-api.py` weitergeleitet.
- **API-Key**: `OPENAI_API_KEY` via Apache-Umgebungsvariablen.
- **Free-Tier-Modelle**: `gpt-4o-mini`, `gpt-5.6-luna`
- **Paid-Tier-Modelle**: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`, `gpt-5.4`, `gpt-4o`, `gpt-4.1`, `gpt-4o-mini`
- **Output-Token-Parameter**: `max_completion_tokens` — von allen aktuellen OpenAI-Modellen verlangt (GPT-4o/4.1 akzeptieren ihn ebenfalls, sodass ein einziger Parameter über das gesamte Lineup hinweg funktioniert). Der ältere Parameter `max_tokens` wird von GPT-5.x-Modellen mit HTTP 400 abgelehnt (`Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.`).
- **Bild-Eingabe**: `gpt-4o-mini`, `gpt-4o`, `gpt-4.1`, `gpt-5.4`, `gpt-5.5` und die gesamte GPT-5.6-Familie akzeptieren Bild-Input. Bilder werden als `image_url`-Content-Blöcke mit einer base64-Daten-URL (`data:{mime};base64,{data}`) gesendet.
- **Audio-Eingabe**: `gpt-4o` und `gpt-4.1` unterstützen Mikrofon-Aufnahmen. Audio wird als `input_audio`-Blöcke im nativen OpenAI-Format gesendet. Der Aufnahme-Button wird automatisch angezeigt/ausgeblendet basierend auf dem aktiven Modell.
- **Kein kostenloser API-Tier für GPT-5.x**: OpenAI bietet für GPT-5.4/5.5/5.6 in der API keinen wirklich kostenlosen Tier an — die „Free"-Gruppierung in diesem Client bezeichnet die günstigsten verfügbaren Modelle (`gpt-4o-mini`, `gpt-5.6-luna`), nicht ein $0-Kontingent.
- **Geplante Abschaltung**: `gpt-4o` und `gpt-4o-mini` (zusammen mit GPT-4, GPT-4 Turbo, GPT-3.5 Turbo und der o-Serie) sind für eine API-weite Abschaltung am **23. Oktober 2026** vorgesehen.
- DeepThink-Button und -Indikator werden ausgeblendet wenn OpenAI der aktive Anbieter ist.
- Der System-Prompt identifiziert das aktive Modell: *„You are [model], an AI assistant made by OpenAI."*

### Google-Gemini-Integration

- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent`
- **Architektur**: `google-api.py` konvertiert das intern verwendete OpenAI-kompatible Nachrichtenformat in Geminis `contents`-Format, sendet die Anfrage und konvertiert die Gemini-SSE-Antwort zurück in das vom Client erwartete OpenAI-SSE-Format.
- **API-Key**: `GOOGLE_API_KEY` via Apache-Umgebungsvariablen.
- **Free-Tier-Modelle**: `gemini-2.5-flash` (5 RPM, 20 RPD)
- **Paid-Tier-Modelle**: `gemini-2.5-flash`, `gemini-2.5-pro`
- **Bild-Eingabe**: Beide Modelle akzeptieren Bild-Input, gesendet als `inline_data`-Blöcke im nativen Gemini-Format (derselbe Mechanismus, der auch für Audio genutzt wird).
- **Audio-Eingabe**: Beide Gemini-Modelle unterstützen Audio nativ. Audio wird als `inline_data`-Blöcke im Gemini-Format gesendet. Der Aufnahme-Button ist immer sichtbar wenn Google Gemini aktiv ist.
- **Abgeschaltete Modelle**: `gemini-2.0-flash` (abgeschaltet am 1. Juni 2026) und `gemini-1.5-pro` (bereits früher abgeschaltet) wurden aus allen Modelllisten, `MODEL_CONFIG` und `AUDIO_CAPABLE_MODELS` entfernt. Das Standard-Fallback-Modell wurde von `gemini-2.0-flash` auf `gemini-2.5-flash` geändert.
- **Bevorstehende Abschaltung**: `gemini-2.5-flash` selbst ist für eine Abschaltung am **16. Oktober 2026** vorgesehen (Nachfolger: `gemini-3.5-flash`, noch nicht integriert).
- DeepThink-Button und -Indikator werden ausgeblendet wenn Google Gemini der aktive Anbieter ist.

### Hugging-Face-Integration

- **Endpoint**: `https://router.huggingface.co/v1/chat/completions` — der Hugging Face Inference Router wählt automatisch den schnellsten verfügbaren Provider.
- **Architektur**: OpenAI-kompatibles Format — keine Konvertierung nötig. SSE wird direkt von `hugging-api.py` weitergeleitet.
- **API-Key**: `HF_API_KEY` — ein Write-Token von `huggingface.co/settings/tokens` mit der Berechtigung „Make calls to Inference Providers".
- **Free-Tier-Modelle**: `Qwen/Qwen2.5-72B-Instruct`, `mistralai/Mistral-7B-Instruct-v0.3`, `microsoft/Phi-3.5-mini-instruct`
- **Paid-Tier-Modelle**: `meta-llama/Meta-Llama-3.1-70B-Instruct`, `meta-llama/Meta-Llama-3.1-405B-Instruct`, `Qwen/Qwen2.5-72B-Instruct`
- **Entfernt**: `mistralai/Mixtral-8x7B-Instruct-v0.1` — wird seit 19. Juli 2026 von keinem Inference Provider mehr auf dem Hugging-Face-Router gehostet.
- DeepThink-Button und -Indikator werden ausgeblendet wenn Hugging Face aktiv ist.

### GroqCloud-Integration

- **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Architektur**: OpenAI-kompatibles Format — keine Konvertierung nötig. SSE wird direkt von `groq-api.py` weitergeleitet.
- **API-Key**: `GRQ_API_KEY` via Apache-Umgebungsvariablen.
- **Wichtig**: Ein `User-Agent`-Header ist in allen Anfragen erforderlich — ohne ihn gibt Cloudflare den Fehlercode 1010 zurück und blockiert die Anfrage.
- **Free- und Paid-Tier-Modelle**: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `meta-llama/llama-4-scout-17b-16e-instruct`, `qwen/qwen3-32b`. Nur Paid: `moonshotai/kimi-k2-instruct-0905`.
- Alle Modelle laufen auf GroqClouds LPU (Language Processing Unit)-Hardware mit sehr niedriger Inferenz-Latenz.
- **Dokumentationsbereinigung**: Der Header von `groq-api.py` dokumentierte bisher `mixtral-8x7b-32768` (von Groq seit 20. März 2025 deprecated) und `gemma2-9b-it` (seit 8. Oktober 2025 deprecated) als unterstützte Modelle — beide waren bereits unerreichbar und wurden aus dem Header entfernt. Die tatsächlichen Modell-Arrays in `index.html` waren bereits korrekt; nur die Dokumentation war veraltet.
- DeepThink-Button und -Indikator werden ausgeblendet wenn GroqCloud der aktive Anbieter ist.

### LLM-Einstellungs-Panel

Ein dediziertes **LLM-Einstellungs**-Panel (getrennt vom Haupt-Einstellungs-Panel) hält alle anbieterspezifischen Konfigurationen aus dem Haupt-Interface heraus:

- **Anbieter-Auswahl**: Toggle zwischen OpenAI, DeepSeek, Google Gemini, Hugging Face und GroqCloud — genau ein Anbieter gleichzeitig aktiv.
- **OpenAI-Optionen**: Free/Paid-Plan-Toggle mit automatischer Modelllisten-Aktualisierung.
- **DeepSeek-Optionen**: Standard-Modus (Normal Chat / DeepThink), Datenschutz-Toggle (`X-No-Training`-Header).
- **Google-Optionen**: Free/Paid-Plan-Toggle mit automatischer Modelllisten-Aktualisierung.
- **Hugging-Face-Optionen**: Free/Paid-Plan-Toggle mit automatischer Modelllisten-Aktualisierung.
- **GroqCloud-Optionen**: Free/Paid-Plan-Toggle mit automatischer Modelllisten-Aktualisierung.
- **Kompressor-Optionen**: Aktivierungs-Toggle, Komprimierungs-Anbieter-Auswahl (nur bezahlte Anbieter), Komprimierungs-Modell-Auswahl. Standard: aktiviert, DeepSeek / `deepseek-v4-flash`.
- **Modell-Dropdown**: Immer sichtbar, Inhalt aktualisiert sich automatisch basierend auf aktivem Anbieter und gewähltem Plan.
- Alle LLM-Einstellungen werden in `localStorage` gespeichert und überleben Seitenneuladen.

### 429-Rate-Limit-Handling

Der Google Gemini Free Tier erzwingt strikte Rate Limits (5 RPM, 20 RPD). Der Client behandelt diese ohne Anzeige eines rohen Fehlers:

- Bei HTTP 429 wiederholt der Client automatisch bis zu **3 Mal** mit **15-Sekunden-Intervallen**.
- Während des Wartens wird ein Countdown direkt im Chat angezeigt: *„Rate limit reached – waiting 15 seconds and retrying... (Attempt 1/3)"*.
- Nach 3 fehlgeschlagenen Versuchen löst die Tageslimit-Prüfung den blauen Limit-Banner aus wenn zutreffend.
- Die Retry-Logik unterscheidet zwischen temporären RPM-Limits (wiederholbar) und erschöpftem Tageskontingent (nicht wiederholbar).
- Ausführliche Fehlerdetails werden für die Diagnose ins Server-Log geschrieben.

### Zwischenablage-Handler (Ctrl+V)

Ein ausgeklügelter Zwischenablage-Handler fängt alle Einfüge-Events ab und reagiert intelligent basierend auf dem Inhaltstyp:

**Textinhalt** → Ein Einfüge-Dialog erscheint mit zwei Optionen:
- *„An Cursor-Position einfügen"* — fügt den Text direkt an der aktuellen Cursor-Position ins Eingabefeld ein.
- *„Als Datei anhängen"* — behandelt den Zwischenablage-Text als `clipboard.txt` und hängt ihn als Datei-Card an die nächste Nachricht an.

**Bildinhalt** → Eine Vorschau-Box erscheint oberhalb des Eingabefelds mit dem Bild, seinen Abmessungen in KB und einem Entfernen-Button. Das Bild ist bereit zum Senden mit der nächsten Nachricht wenn das aktive Modell Bilder unterstützt.

**Dateipfade aus Datei-Managern (XFCE/Thunar, KDE/Dolphin, etc.)** → Blockiert mit einem Alert:
> *„Dateien, die im Datei-Manager kopiert wurden, können vom Browser nicht gelesen werden. Bitte verwende stattdessen den Upload-Button."*

**Technischer Hintergrund**: Unter Linux/X11/Firefox blockiert `e.preventDefault()` in Paste-Event-Handlern Einfüge-Events aus Datei-Managern nicht zuverlässig. Die implementierte Lösung erlaubt das Einfügen, prüft dann sofort den Inhalt des Eingabefelds via `setTimeout(0)` und leert es wenn Dateipfade erkannt werden. Erkennungslogik: 2 oder mehr Zeilen, bei denen jede nicht-leere Zeile mit `/` oder `file://` beginnt. Ein `requestAnimationFrame`-Call stellt sicher, dass das Eingabefeld visuell geleert wird bevor der Alert-Dialog erscheint.

### Datei-Upload mit Sicherheitsprüfung

- **Akzeptierte Formate**: `.txt`, `.pdf`, `.doc`, `.docx`, `.jpg`, `.jpeg`, `.png`, `.csv`, `.xlsx`, `.pptx`
- **Inhalts-extrahierbare Formate** (Text wird an die KI gesendet): `.txt`, `.pdf`
- **Andere akzeptierte Formate**: als binärer Kontext angehängt (ohne Textextraktion)
- **Maximale Dateigrösse**: 10 MB pro Datei
- **Maximaler extrahierter Inhalt**: dynamisch — berechnet als 75% des Kontextfensters des aktiven Modells in Zeichen: `getDynamicMaxFileChars() = Math.floor(config.maxContextTokens × 4 × 0.75)`

**Dynamisches Upload-Limit — Beispiele**:

| Modell | maxContextTokens | Max. Dateiinhalt |
|--------|-----------------|------------------|
| `deepseek-v4-flash` | 1.048.576 | ~3.145.000 Zeichen |
| `deepseek-v4-pro` | 1.048.576 | ~3.145.000 Zeichen |
| `gemini-2.5-flash` | 1.048.576 | ~3.145.000 Zeichen |
| `gpt-5.6-sol` / `-terra` / `-luna` | 1.048.576 | ~3.145.000 Zeichen |
| `gpt-4o` / `gpt-4o-mini` | 128.000 | ~384.000 Zeichen |

**Magic-Byte-Prüfung** (erste 20 Bytes) erkennt und blockiert ausführbare Dateien unabhängig von der Dateinamens-Erweiterung:

| Plattform | Format | Hex-Signatur |
|-----------|--------|--------------|
| Windows 32/64 Bit | PE/MZ Executable | `4D 5A` |
| Linux 32 Bit | ELF32 | `7F 45 4C 46 01` |
| Linux 64 Bit | ELF64 | `7F 45 4C 46 02` |
| ARM 32 Bit | ELF32 ARM | `7F 45 4C 46 01 01 01 00 ... 02 00 28 00` |
| ARM 64 Bit | ELF64 AArch64 | `7F 45 4C 46 02 01 01 00 ... 02 00 B7 00` |
| macOS 32 Bit | Mach-O | `CE FA ED FE` |
| macOS 64 Bit | Mach-O | `CF FA ED FE` |
| macOS Universal | Fat Binary | `CA FE BA BE` |
| macOS/iOS ARM 32 | Big Endian | `FE ED FA CE` |
| macOS/iOS ARM 64 | Big Endian | `FE ED FA CF` |
| Linux/macOS | Shell-Skript | `23 21` (`#!`) |
| Python | Bytecode (.pyc) | `55 0D 0D 0A` |

**PDF-Extraktion**: Verwendet PDF.js 3.11.174 via CDN mit automatischem Fallback auf ein sekundäres CDN. Extraktions-Fortschritt wird seitenweise angezeigt. Extraktions-Timeout: 30 Sekunden.

**Vorab-Kontext-Prüfung**: Vor der Inhaltsextraktion schätzt der Client, ob das Hinzufügen der Datei das dynamische Upload-Limit überschreiten würde. Wenn ja, wird der Upload mit einer klaren Fehlermeldung blockiert bevor Inhalte extrahiert werden.

### Umlaut-Platzhalter-System

Eine einzigartige Lösung für ein fundamentales Problem mit der DeepSeek API und deutschem Text:

**Problem**: DeepSeek ersetzt intern deutsche Umlaute in Dateiinhalten durch ASCII-Äquivalente (z.B. `Ä → AeNDERUNG`, `Ü → MUeSSEN`). Dieses Verhalten kann nicht via System-Prompts oder API-Parameter unterdrückt werden.

**Lösung**: Vor dem Senden von Dateiinhalten an DeepSeek werden Umlaute durch eindeutige Klammer-Platzhalter ersetzt. DeepSeek gibt diese Platzhalter unverändert zurück. JavaScript ersetzt sie nach dem Empfang der Antwort wieder durch echte Umlaute.

| Original | Platzhalter |
|----------|-------------|
| `ä` | `[[AE]]` |
| `ö` | `[[OE]]` |
| `ü` | `[[UE]]` |
| `ß` | `[[SS]]` |
| `Ä` | `[[CAE]]` |
| `Ö` | `[[COE]]` |
| `Ü` | `[[CUE]]` |

**Kritisches Implementierungsdetail**: Sowohl `encodeUmlautsForAI()` als auch `decodeUmlautsFromAI()` verwenden ausschliesslich **Unicode-Escape-Sequenzen** (`\u00e4` statt `ä`) und `split()/join()` statt Regex — unerlässlich um Korrumpierung beim Transfer via Git oder bei der Bearbeitung in Texteditoren zu verhindern.

Das Decode läuft **sowohl während des Streamings** (Token für Token) als auch nach dem Empfang der vollständigen Antwort, um sicherzustellen dass keine Platzhalter sichtbar bleiben, selbst bei partieller Chunk-Lieferung.

Dieses System wird **nur auf Dateiinhalte** angewendet, nie auf reguläre Benutzernachrichten oder System-Prompts.

### DeepThink-Modus

DeepThink ist ein dedizierter Modus für tiefes analytisches Denken, exklusiv verfügbar wenn DeepSeek der aktive Anbieter ist:

- Aktivierbar über einen dedizierten Pill-Style-Button in der zweiten Button-Zeile unterhalb des Eingabefelds.
- Im aktiven Zustand wird `deepseek-v4-flash` (bzw. `deepseek-v4-pro`, falls im Modell-Dropdown gewählt) verwendet — der Modus ändert nur den System-Prompt, nicht das Modell. Das leistungsfähigere `deepseek-v4-pro` wird über das Modell-Dropdown manuell für maximale Reasoning-Tiefe in beiden Modi gewählt. **Hinweis**: Vor dem 19. Juli 2026 sorgte ein Copy-Paste-Fehler in der Modellauswahl-Logik dafür, dass `deepseek-v4-pro` unabhängig von der Dropdown-Auswahl nie tatsächlich angefragt wurde — dies wurde behoben, siehe [Wartung & Feature-Update vom 19. Juli 2026](#wartung--feature-update-vom-19-juli-2026).
- Der Button verändert sich visuell: inaktiv (dunkel `#2d2d2d`) → aktiv blau (`#1e3a5f` Hintergrund, `#4dabf7` Rahmen und Text).
- Eine Indikatorleiste erscheint unterhalb der Button-Zeile: *„DeepThink-Modus aktiv: Tiefgehende Analyse läuft"*.
- Kontext-Limits und Output-Token-Limits werden automatisch basierend auf dem `MODEL_CONFIG`-Eintrag des aktiven Modells angepasst.
- Der Modus wird mit jeder Nachricht aufgezeichnet (Feld `mode: 'deepthink'`) und in allen Export-Formaten angezeigt.
- Der Standard-Modus (Chat oder DeepThink) kann in den Einstellungen konfiguriert und in `localStorage` gespeichert werden.
- DeepThink-Button und -Indikator werden automatisch ausgeblendet wenn ein Nicht-DeepSeek-Anbieter aktiv ist.

### Modellerkennung & Fähigkeiten

Beim Start fragt `index.html` `/cgi-bin/deepseek-models.py` ab, das den DeepSeek `/v1/models`-Endpoint live aufruft:

- Die zurückgegebenen Modell-IDs werden in `detectedModels[]` gespeichert und intern für Fähigkeits-Prüfungen genutzt (siehe unten). Sie werden **nicht** zur Darstellung des Headers verwendet — der Server-Header (`Modell: ...`) zeigt immer das aktuell **ausgewählte** Modell (`settings.selectedModel`), konsistent zum Verhalten aller fünf Anbieter. Frühere Versionen zeigten für DeepSeek fälschlicherweise die komplette `detectedModels`-Liste unabhängig von der aktiven Auswahl an; dies wurde am 19. Juli 2026 korrigiert.
- Eine `MODEL_CAPABILITIES`-Map definiert welche Modelle welche Eingabetypen unterstützen, pro Anbieter befüllt basierend auf den dokumentierten Fähigkeiten des jeweiligen Backends:
  ```javascript
  const MODEL_CAPABILITIES = {
      // DeepSeek: nur Text
      'deepseek-v4-flash': { images: false, text: true },
      'deepseek-v4-pro':   { images: false, text: true },
      // Google Gemini: multimodal
      'gemini-2.5-flash':  { images: true,  text: true },
      'gemini-2.5-pro':    { images: true,  text: true },
      // OpenAI: multimodal über das gesamte aktuelle Lineup
      'gpt-4o-mini': { images: true, text: true },
      'gpt-4o':      { images: true, text: true },
      'gpt-4.1':     { images: true, text: true },
      'gpt-5.4':     { images: true, text: true },
      'gpt-5.5':     { images: true, text: true },
      'gpt-5.6-sol':   { images: true, text: true },
      'gpt-5.6-terra': { images: true, text: true },
      'gpt-5.6-luna':  { images: true, text: true },
      // GroqCloud / Hugging Face: nur Text (aktuelles Modell-Lineup)
      // ... (siehe index.html für die vollständige Liste)
      'default': { images: false, text: true },
  };
  ```
- `currentModelSupportsImages()` prüft `settings.selectedModel` (mit Fallback auf den aktuellen `modelSelect`-Dropdown-Wert) gegen `MODEL_CAPABILITIES`. Frühere Versionen prüften stattdessen `detectedModels` — ein nur für DeepSeek relevantes Array, das für andere Anbieter nie befüllt wurde — wodurch Bild-Upload und -Paste stillschweigend für **jeden** Anbieter und jedes Modell blockiert waren, einschliesslich tatsächlich bildfähiger. Dies wurde am 19. Juli 2026 korrigiert.
- Wenn ein Bild via Zwischenablage eingefügt oder eine `.jpg`/`.png`-Datei hochgeladen wird und das aktuelle Modell keine Bilder unterstützt, wird die Operation mit einem Alert blockiert bevor ein Upload stattfindet.
- Diese Architektur ist **vorwärtskompatibel**: Bild-Unterstützung für ein Modell hinzuzufügen erfordert nur das Hinzufügen oder Aktualisieren seines Eintrags in `MODEL_CAPABILITIES` — zu beachten ist jedoch, dass `MODEL_CONFIG` (siehe [Modell-Konfiguration](#modell-konfiguration)) ebenfalls einen passenden Eintrag benötigt, damit das Modell korrekte Kontext-/Output-Limits erhält, statt stillschweigend auf die DeepSeek-Standardwerte zurückzufallen.

### Bild-Unterstützung (Vision)

Bild-Upload und Zwischenablage-Einfügen sind für Google Gemini und OpenAI durchgängig end-to-end verdrahtet. Dies war eine bedeutende Lücke, die am 19. Juli 2026 geschlossen wurde — zuvor wurden Bilder zwar von der UI entgegengenommen, erreichten aber nie tatsächlich ein Modell.

**Client-Seite (`index.html`)**:
- **Datei-Upload**: Wenn eine Bilddatei (`.jpg`, `.jpeg`, `.png` etc.) ausgewählt wird und das aktive Modell Bilder unterstützt (laut `currentModelSupportsImages()`), wird die Datei via `FileReader.readAsDataURL()` eingelesen und die base64-Nutzlast (ohne `data:...;base64,`-Präfix) in `imageData` gespeichert, mit dem MIME-Typ in `imageMimeType`.
- **Zwischenablage-Paste**: Das Einfügen eines Bildes (Strg+V) führt dieselbe base64-Lesung durch, genutzt sowohl für die Thumbnail-Vorschau über dem Eingabefeld als auch für das tatsächliche `imageData`, das mit der nächsten Nachricht gesendet wird.
- **Request-Payload**: `sendMessage()` fügt `image_data` und `image_mime_type` in den JSON-Body ein, sobald `imageData` gesetzt ist — neben dem bestehenden `audio_data`/`audio_mime_type`-Mechanismus. Beide können gleichzeitig vorhanden sein.
- **State-Reset**: `imageData`/`imageMimeType` werden zurückgesetzt nach dem Senden einer Nachricht, beim Entfernen einer Datei über den „X"-Button und beim Beginn einer neuen Dateiauswahl — insgesamt sechs Reset-Stellen, analog zur bestehenden Audio-Reset-Logik.
- **Bekannte kosmetische Einschränkung**: Ein Bild-Anhang, der *ohne* begleitende Text-Datei gesendet wird, erzeugt aktuell keine eigene Datei-Card in der Chat-Blase (identisch zum bereits bestehenden Verhalten bei reinen Audio-Nachrichten). Die Übertragung an das Modell funktioniert unabhängig davon korrekt; nur die visuelle Card fehlt in diesem speziellen Fall.

**Server-Seite**:
- **`google-api.py`**: `convert_messages_to_gemini()` akzeptiert `image_data`/`image_mime_type` und hängt das Bild als `inline_data`-Part an die letzte User-Message an — derselbe Mechanismus, der bereits für Audio verwendet wird.
- **`openai-api.py`**: Der `content` der letzten User-Message wird als Liste aus dem Text-Teil plus optionalem `input_audio`-Block und optionalem `image_url`-Block (`{'type': 'image_url', 'image_url': {'url': 'data:{mime};base64,{data}'}}`) zusammengebaut. Der frühere Code überschrieb `content` beim Verarbeiten von Audio bedingungslos, was ein gleichzeitig gesendetes Bild (oder umgekehrt) stillschweigend verworfen hätte — die überarbeitete Logik baut die Content-Liste inkrementell auf, sodass beides koexistieren kann.
- **GroqCloud und Hugging Face** erhalten aktuell keine Bilddaten — deren Modell-Lineups sind laut eigener Dokumentation reine Text-Modelle, und `MODEL_CAPABILITIES` spiegelt dies wider (`images: false`), sodass der Client Bild-Anhänge für diese Anbieter blockiert, bevor überhaupt eine Anfrage gesendet wird.

**Verifiziert**: Live getestet mit `gemini-2.5-flash` und `gpt-4o-mini` — beide beschrieben den Inhalt eines hochgeladenen Screenshots korrekt und detailliert.

### Mehrsprachiges System

Die UI unterstützt mehrere Sprachen die aus einer externen `language.xml`-Datei geladen werden. Im `index.html` existieren keine hardcodierten UI-Strings.

**Aktuell enthaltene Sprachen**:
- Englisch (`en`) — Standard, kein Anredeform-Unterschied
- Deutsch (`de`) — mit formeller/informeller Anredeform (Sie/Du)
- Spanisch (`es`) — mit formeller/informeller Anredeform (Usted/Tú)
- Custom-Slot (`custom`) — aktiviert durch Setzen von `visible="true"` in `language.xml`

**Technische Implementierung**:
- Alle UI-Texte werden durch numerische IDs referenziert: `t(205)` gibt die Senden-Button-Beschriftung in der aktuellen Sprache zurück.
- `loadLanguage()` lädt und parst `language.xml` via `fetch()` beim Seitenstart.
- `t(id)` — gibt Text für die aktuelle Sprache zurück, fällt auf Englisch zurück wenn die ID nicht gefunden wird.
- `tf(id, ...args)` — unterstützt `{0}`, `{1}`, ...-Platzhalter-Substitution.
- `tform(idFormal, idInformal)` — gibt den entsprechenden Text basierend auf der gewählten Anredeform zurück.
- Sprachwechsel erfolgt sofort, kein Seitenneuladen erforderlich.
- Die gewählte Sprache wird in `localStorage` gespeichert.

**Anredeform-System** (Deutsch/Spanisch):
- Sprachen deklarieren `has_address_form="true"` in `language.xml`.
- Für solche Sprachen zeigt das Einstellungs-Panel eine „Anredeform"-Gruppe (Formell/Informell).
- Die gewählte Form beeinflusst: System-Prompt (erzwingt konsistenten KI-Antwort-Stil), Eingabefeld-Placeholder-Text, alle Einstellungs-Beschreibungstexte.

**System-Prompt** wird pro Anfrage dynamisch aufgebaut aus:
1. Basis-Prompt (Text-IDs 29/30 für formell/informell)
2. DeepThink-Zusatz (Text-IDs 31/32)
3. Eine strikte Dateiverarbeitungs-Anweisung immer auf Englisch angehängt unabhängig von der UI-Sprache — für konsistentes KI-Verhalten bei der Verarbeitung von Dateiinhalten.

### Einstellungen (Toggles statt Radio-Buttons)

Alle Einstellungen verwenden **Toggle-Schalter** (von links nach rechts schiebend), niemals Radio-Buttons oder Checkboxen:

| Gruppe | Einstellung | Toggle-Farbe |
|--------|-------------|-------------|
| Sprache | EN / DE / ES / Custom | Grün |
| Anredeform | Formell / Informell | Grün |
| Standard-Modus | Normal Chat / DeepThink | Blau |
| Datenschutz | Daten nicht für Training verwenden | Grün |

**Toggle-Verhalten**:
- Innerhalb einer Gruppe verhalten sich Toggles wie Radio-Buttons: einen aktivieren deaktiviert alle anderen in der Gruppe.
- Klick irgendwo auf die `setting-item`-Zeile aktiviert diesen Toggle — nicht nur das Toggle-Element selbst.
- Aktive Einträge erhalten einen farbigen Hintergrund: `#1a2e1a` (Grün-Gruppen) oder `#1e3a5f` (Blau-Gruppen).

**Datenschutz-Toggle**: Setzt den HTTP-Header `X-No-Training: true` in allen API-Anfragen an DeepSeek und nutzt DeepSeeks Opt-out-Mechanismus für Trainingsdaten.

**Einstellungs-Persistenz**: Alle Einstellungen werden in `localStorage` unter dem Key `deepseekSettings` gespeichert. Aktuelle Schema-Version: `SETTINGS_VERSION: 1.7`. Die Funktion `migrateSettings()` gewährleistet Rückwärtskompatibilität — fehlende Felder werden mit Standardwerten gefüllt, unbekannte Modi werden normalisiert.

### Session-Management

Jedes Gespräch wird automatisch als serverseitige Session verwaltet:

- **Session-ID-Format**: `YYYY-MM-DD_HHMMSS_random6chars` (z.B. `2026-05-11_143045_abc123`) — clientseitig generiert, serverseitig via Regex validiert bevor Datei-I/O stattfindet.
- **Auto-Speichern**: Nach jedem gesendeten Nachrichten-Paar (Benutzer + KI) wird das vollständige `contextHistory.messages[]`-Array serialisiert und als JSON-Datei auf dem Server gespeichert.
- **Session-Datei**: `{sessionId}.json` in `/var/www/deepseek-chat/sessions/`, `chmod 600`, `www-data`-Eigentümer.
- **Chat-Verlauf laden Modal**: Listet alle gespeicherten Sessions mit ID, Datum, Nachrichten-Preview (erste 80 Zeichen) und Nachrichten-Anzahl auf. Jede Session hat [Laden]-Buttons (grün) und [Löschen]-Buttons (rot).
- **Ladeverhalten**: Der aktuelle Chat wird zuerst auto-gespeichert, dann wird die gewählte Session wiederhergestellt — vollständiger Nachrichtenverlauf, UI-Rekonstruktion, Kontext-Schätzung neu berechnet.
- **Löschen**: Die JSON-Datei wird sofort ohne Bestätigungsdialog vom Server entfernt.

**CGI-Endpoint-Details**:
- `save-session.py` — `POST`: empfängt `{sessionId, messages}`, validiert ID-Format (Regex), schreibt `sessions/{sessionId}.json`
- `load-session.py` — `GET`: gibt `[{id, preview, count, date}]` zurück; `GET ?id=X`: gibt vollständige `{messages: [...]}` zurück
- `delete-session.py` — `DELETE ?id=X`: entfernt `sessions/{sessionId}.json`

### Exportfunktionen

**Globaler Export** (Dropdown-Button in der Haupt-Button-Zeile):

| Format | Generierung | Hinweise |
|--------|------------|---------|
| PDF | Serverseitig (`export-pdf.py`, ReportLab) | Header, Statistiken, Inhaltsverzeichnis, vollständiger Chat |
| Markdown | Serverseitig (`export-markdown.py`) | Identische Struktur wie PDF, mit Anchors |
| TXT | Serverseitig (`export-txt.py`) | Klartext mit Trennzeichen |
| RTF | Serverseitig (`export-rtf.py`) | Manuelle RTF-Kodierung, Umlaute als RTF-Escape-Codes |
| **In Zwischenablage kopieren** | **Nur clientseitig (kein Server-Roundtrip)** | Klartext in JavaScript zusammengestellt, via `navigator.clipboard.writeText()` geschrieben |

**Einzelnachrichten-Export** (Hover-Button auf jeder Nachricht):

| Format | Generierung |
|--------|------------|
| TXT | Clientseitig (JavaScript Blob, `URL.createObjectURL()`) |
| Markdown | Clientseitig |
| RTF | Clientseitig |
| PDF | Serverseitig (einzelne Nachricht an `export-pdf.py` gesendet) |

**Export-Inhalt** (PDF/Markdown globaler Export):
- Header: Server-Name, IP, Export-Datum, aktive Sprache, Anredeform
- Statistiken: Gesamt-Nachrichten-Anzahl, verwendete Modi (Chat/DeepThink), angehängte Dateien, geschätzte Token-Anzahl, Session-Dauer
- Inhaltsverzeichnis mit allen Nachrichten-Zeitstempeln
- Vollständiger Chat-Verlauf mit Zeitstempeln und Modus-Indikatoren pro Nachricht

**In Zwischenablage kopieren**: Im TXT-Format clientseitig zusammengestellt und via `navigator.clipboard.writeText()` geschrieben. Eine 2-sekündige *„Kopiert!"*-Bestätigung ersetzt die Export-Button-Beschriftung, setzt sich dann automatisch zurück.

**PDF-Technische Anmerkung**: Binäre PDF-Daten werden ausschliesslich via `sys.stdout.buffer` mit als Bytes kodierten HTTP-Headern geschrieben — vermeidet den `„Bad header"`-Fehler der auftritt wenn `print()` (Text-Mode-Stdout) mit binären Inhalten gemischt wird.

### Feedback-Buttons & Logging

Vier Buttons erscheinen beim Hover für jede KI-Antwort (linke Seite, untere Zeile):

- **Kopieren** — Kopiert Nachrichtentext in die Zwischenablage; zeigt *„Kopiert!"* für 2 Sekunden, setzt sich dann zurück.
- **Like** — Markiert die Antwort positiv (blaue Hervorhebung); sendet einen `LIKE`-Eintrag ins Server-Log. Nochmaliges Klicken entfernt das Like.
- **Dislike** — Markiert die Antwort negativ (rote Hervorhebung); sendet einen `DISLIKE`-Eintrag. Like und Dislike schliessen sich gegenseitig aus.
- **Regenerieren** — Entfernt die aktuelle KI-Antwort aus Kontext-Array und DOM, ruft dann die API erneut mit derselben Benutzernachricht und dem vollständigen vorherigen Verlauf auf.

**Server-Log-Format** (`/var/www/deepseek-chat/logs/multi-llm-chat.log`):
```
2026-05-11T12:30:00.000 | IP: 194.182.64.122 | POST /cgi-bin/deepseek-api.py | Status: 200
2026-05-11T12:30:00.000 | IP: 194.182.64.122 | FEEDBACK | LIKE | msg_5 | "Erste 60 Zeichen der Antwort..."
```

**Niemals geloggt**: API-Keys, vollständige Session-Inhalte oder Nachrichtentext über die 60-Zeichen-Feedback-Preview hinaus.

### Dynamische Kontext-Anzeige

Der Server-Header zeigt vier Zeilen Echtzeit-Informationen:
1. Server-Name (blau `#4dabf7`)
2. `IP: xxx.xxx.xxx.xxx`
3. `Kontext: XX% (aktiver-modell-name)`
4. `Modell: deepseek-v4-flash, deepseek-v4-pro` (live von `/v1/models`)

**Kontext-Nutzungsgrad-Berechnung**:
- Geschätzte Tokens = Summe der Zeichenanzahl der letzten `maxContextMessages` Nachrichten × `TOKENS_PER_CHAR` (0,25)
- System-Prompt-Tokens werden als fixer Overhead addiert
- Prozentsatz = geschätzte Tokens / `maxContextTokens` × 100

**Warnsystem**: Oberhalb von 90% Kontext-Nutzung wird die Kontext-Zeile rot und blinkt (CSS-Keyframe-Animation, Opazität 0 → 1, 1-Sekunden-Zyklus). Das liefert eine gut sichtbare Frühwarnung.

Die Anzeige aktualisiert sich automatisch nach jeder gesendeten Nachricht, jeder gelöschten Nachricht und jedem Modellwechsel.

### Datei-Card-Anzeige

Wenn eine Datei hochgeladen oder Zwischenablage-Text angehängt wird, zeigt die Benutzernachricht eine kompakte **Datei-Card**:

```
┌──────────────────────────────────────┐
│  [PDF]  │  dateiname.pdf             │
│  Icon   │  PDF-Dokument              │
└──────────────────────────────────────┘
```

- Datei-Typ-Badge abgeleitet aus der Dateiendung (PDF, TXT, XLSX, DOCX, etc.)
- Dateiname auf 30 Zeichen gekürzt mit `...` wenn länger
- Audio-Aufnahmen zeigen ein `AUDIO`-Badge mit der lokalisierten Beschriftung
- Multi-Datei-Uploads generieren eine Card pro Datei; alle Dateinamen erscheinen in der Info-Leiste getrennt durch ` | `

### Audio-Aufnahme

Der Client enthält einen eingebauten **Mikrofon-Aufnahme-Button** der direkte Spracheingabe an audio-fähige Modelle ermöglicht:

- **Sichtbarkeit**: Gesteuert von `updateAudioButtonVisibility()`, aufgerufen bei jedem Modellwechsel. Sichtbar nur wenn das aktive Modell in `AUDIO_CAPABLE_MODELS` aufgeführt ist.
- **Audio-fähige Modelle** (Konstante `AUDIO_CAPABLE_MODELS`):
  - Google Gemini: `gemini-2.5-flash`, `gemini-2.5-pro`
  - OpenAI: `gpt-4o`, `gpt-4.1`
- **Aufnahme-Ablauf**: `getUserMedia()` → `MediaRecorder`-API → Chunk-Aufnahme (10ms-Intervalle) → `Blob` bei Stop zusammengesetzt → base64-kodiert.
- **MIME-Typ-Auto-Erkennung**: `audio/webm` (Chrome/Firefox) oder `audio/mp4` (Safari) — zur Laufzeit via `MediaRecorder.isTypeSupported()` ermittelt.
- **Nach der Aufnahme**: Audio-Daten werden in der `fileInfo`-Box als AUDIO-Badge-Card angezeigt.
- **Request-Payload**: `audio_data` (base64-String) und `audio_mime_type` werden neben der Textnachricht zum JSON-Body hinzugefügt. Das `hasFile`-Flag wird **nicht** gesetzt — für Audio wird kein Dateiverarbeitungs-System-Prompt injiziert.
- **Gegenseitige Exklusivität**: Datei-Upload und Audio-Aufnahme schliessen sich gegenseitig aus. Eine Aufnahme starten löscht anhängende Datei-Attachments und umgekehrt.
- **Backend — Google (`google-api.py`)**: Audio wird als `inline_data`-Block im nativen Gemini-Format an die letzte Benutzernachricht angehängt.
- **Backend — OpenAI (`openai-api.py`)**: Audio wird als `input_audio`-Block mit `format: webm` oder `mp4` angehängt.
- **Wartungsregel** (Manifest-Regel E.1): Wenn ein integrierter Anbieter Audio-Unterstützung für ein Modell hinzufügt oder entfernt, muss `AUDIO_CAPABLE_MODELS` in `index.html` **sofort** aktualisiert werden.

### Kompressor — Intelligente Kontext-Komprimierung

Jedes Sprachmodell hat ein endliches Kontextfenster. In langen Sessions — besonders bei grossen Datei-Uploads, mehrstündigen Gesprächen oder umfangreichen Analyse-Workflows — füllt sich das Kontextfenster schliesslich und verursacht API-Fehler (HTTP 400/413), die den Benutzer zwingen neu anzufangen und den gesamten Gesprächsfaden zu verlieren.

Der **Kompressor** löst dieses Problem automatisch und transparent, ohne Benutzer-Aktion.

#### Kernkonzept

Statt alte Nachrichten abzuschneiden oder einen manuellen Neustart zu erzwingen, **fasst** der Kompressor die ältere Hälfte des Gesprächs via dediziertem zweitem LLM-Call zusammen. Diese Zusammenfassung wird in den System-Prompt aller nachfolgenden Anfragen injiziert. Das aktive Modell „erinnert" sich effektiv an die zusammengefasste Vergangenheit — das Gespräch kann unbegrenzt fortgeführt werden.

#### Aktivierungs-Schwellwerte

| Schwellwert | Aktion |
|-------------|--------|
| **70%** Kontext-Nutzung | Erste Komprimierungsrunde |
| **85%** Kontext-Nutzung | Zweite Komprimierungsrunde |
| **95%** Kontext-Nutzung | Dritte Komprimierungsrunde |

Jeder Schwellwert löst maximal einmal pro Session-Zyklus aus. Nach manueller Nachrichten-Löschung wird das gesamte Schwellwert-Tracking zurückgesetzt wenn der Kontext-Prozentsatz unter den zuletzt ausgelösten Schwellwert fällt.

#### Komprimierungs-Prozess (Schritt für Schritt)

1. Nach jeder gesendeten Nachricht berechnet `updateContextEstimation()` den Kontext-Nutzungsgrad neu.
2. Wenn ein Schwellwert überschritten wird, wird `compress-context.py` **vor** dem Haupt-API-Call aufgerufen.
3. Die ältesten 50% der Nachrichten werden extrahiert. Der Schnitt rückt zur nächsten Benutzernachricht vor — API-Kompatibilität sichergestellt (Kontext muss immer mit einer Benutzer-Turn beginnen).
4. Base64-Daten, Bilder und Multimedia-Inhalte werden herausgefiltert — nur Klartext wird an das Komprimierungs-LLM gesendet.
5. Das Komprimierungs-LLM (konfigurierbarer Anbieter und Modell) gibt eine strukturierte Zusammenfassung zurück.
6. Die alten Nachrichten werden durch einen einzigen komprimierten Eintrag ersetzt (Flag `compressed: true`).
7. Der Zusammenfassungstext wird dem System-Prompt aller nachfolgenden API-Calls vorangestellt — nie als eigenständige `assistant`-Nachricht gesendet (was 400-Fehler verursachen würde).
8. Der komprimierte Kontext wird auf Disk gespeichert. Der Haupt-API-Call wird mit dem reduzierten Kontext fortgesetzt.

#### Intelligentes Zusammenfassungs-Verwerfen

Wenn der Benutzer Nachrichten manuell löscht und der Kontext-Prozentsatz unter den **zuletzt ausgelösten Schwellwert** fällt (nicht einfach unter 70%), wird die Kompressions-Zusammenfassung automatisch aus dem System-Prompt entfernt und alle Schwellwert-Zähler werden zurückgesetzt. Der Komprimierungszustand spiegelt stets den tatsächlichen Gesprächsinhalt wider.

#### Anbieter-Einschränkung (nur bezahlte Anbieter)

Der Kompressor macht einen separaten LLM-Call der grosse Token-Mengen umfassen kann. Free-Tier-Rate-Limits (Groq: 6.000–12.000 TPM; Hugging Face: variabel) sind für zuverlässige Komprimierung realer Gespräche unzureichend. Nur bezahlte Anbieter werden angeboten:

| Anbieter | Verfügbare Komprimierungs-Modelle |
|----------|----------------------------------|
| DeepSeek | `deepseek-v4-flash`, `deepseek-v4-pro` |
| OpenAI | `gpt-4o-mini`, `gpt-5.6-luna`, `gpt-4o`, `gpt-4.1` |
| Google | `gemini-2.5-flash`, `gemini-2.5-pro` |

**Empfohlener Standard**: DeepSeek + `deepseek-v4-flash` — keine Rate Limits, niedrigste Kosten pro Token, zuverlässigste Ergebnisse.

#### Ergebnisdateien

Jede Komprimierungsrunde wird zur Überprüfung auf Disk gespeichert:
```
/var/www/deepseek-chat/kompressor/kompressor_JJJJMMTT_HHMMSS.txt
```

### Guthaben- und Tageslimit-Banner

**Roter Banner — „Guthaben muss erneuert werden!"** (bezahlte Anbieter):
- Ausgelöst durch erschöpftes Guthaben bei einer bezahlten API.
- **DeepSeek**: HTTP-402-Antwort.
- **OpenAI**: HTTP 429 + `insufficient_quota` im JSON-Response-Body.
- Als fest positioniertes Element oben im Viewport angezeigt bis manuell geschlossen (×-Button).

**Blauer Banner — „Tageslimit erreicht!"** (Free-Tier-Anbieter):
- Ausgelöst durch erschöpftes Tageskontingent bei einer kostenlosen API.
- **Google Gemini**: HTTP 429 + Tageskontingent-Keywords im Response-Body.
- **GroqCloud**: HTTP 429.
- **Hugging Face**: HTTP 429.
- Gleiche fest positionierte Anzeige mit ×-Schliessen-Button.

### Kontextfenster-Überschreitung

Wenn die API HTTP 400 mit kontextbezogenen Keywords im Response-Body zurückgibt, erscheint eine **interaktive Box** direkt im Chat statt einer generischen Fehlermeldung:

- **Blau umrandete Box**: *„Die maximale Chat-Grösse des aktuellen LLM wurde erreicht."*
- **Grüner Button — „Neuen Chat mit aktuellem Kontext starten"** (Option C):
  1. Aktuelle Session wird auto-gespeichert.
  2. Die letzte Kompressions-Zusammenfassung (falls vorhanden) wird mit allen nachfolgenden nicht-komprimierten Nachrichten als Klartext kombiniert.
  3. Eine neue Session startet mit diesem kombinierten Kontext als vorgeladener Datei-Anhang — das Gespräch wird nahtlos mit vollem Kontext-Carry-Over fortgesetzt.
- **Blauer Button — „Neuen Chat ohne Kontext starten"** (sauberer Neustart):
  1. Aktuelle Session wird auto-gespeichert.
  2. Neue Session startet mit leerem Kontext.

Das ermöglicht **verkettete Gespräche** über mehrere Sessions — theoretisch unbegrenzt in der Gesamtlänge.

Alle fünf CGI-Proxy-Skripte erkennen Kontext-Overflow durch Prüfung des HTTP-Status-Codes und Keyword-Matching im API-Fehler-Body und geben `error_type: 'context_exceeded'` an den Client zurück.

### API-Proxy-Dokumentations-Header

Jedes der fünf CGI-Proxy-Skripte (`openai-api.py`, `deepseek-api.py`, `google-api.py`, `hugging-api.py`, `groq-api.py`) enthält einen strukturierten Dokumentations-Block direkt nach der Encoding-Deklaration:

- **Import-/Aktualisierungsdatum** — wann die Datei zuletzt aktualisiert wurde
- **Unterstützte Modelle** — Version, Kontext-/Output-Token-Limits, Fähigkeiten (Text/Bilder/Audio/Video), Free/Paid-Zuordnung
- **Quell-Link** — offizielle API-Dokumentations-URL mit Datum

Das stellt sicher, dass alle Modell-Spezifikationen direkt im Quellcode nachvollziehbar sind ohne externe Dokumentation konsultieren zu müssen.

---

## DeepSeek V4 Migration

### Hintergrund

Am **24. April 2026** veröffentlichte DeepSeek den **DeepSeek V4 Preview** — eine neue Generation von MoE (Mixture-of-Experts) Sprachmodellen mit dramatisch erweiterten Fähigkeiten. Die zwei neuen Modelle ersetzen `deepseek-chat` (V3) und `deepseek-reasoner` (R1).

### Neue Modelle

| Modell | Parameter | Aktiv | Kontext | Max. Output | Thinking-Mode |
|--------|-----------|-------|---------|------------|--------------|
| `deepseek-v4-flash` | 284B gesamt | 13B | 1.048.576 Token | 8.192 Token | Ja (Thinking + Non-Thinking) |
| `deepseek-v4-pro` | 1,6T gesamt | 49B | 1.048.576 Token | 32.768 Token | Ja (Thinking + Non-Thinking) |

### Architektur-Verbesserungen (V4 vs. V3)

- **Hybrid Attention**: V4 kombiniert Compressed Sparse Attention (CSA) und Heavily Compressed Attention (HCA) — ermöglicht 1M-Token-Kontext mit nur 27% der Single-Token-Inferenz-FLOPs von V3.2 und nur 10% des KV-Cache.
- **Manifold-Constrained Hyper-Connections (mHC)**: Stärkt Residual-Connections für stabilere Signalausbreitung über Layer hinweg.
- **Drei Reasoning-Effort-Modi**: Non-think (schnell), Think High (logische Analyse), Think Max (vollständiger Reasoning-Umfang) — via API-Parameter zugänglich.

### Deprecation-Zeitplan

| Datum | Ereignis |
|-------|---------|
| 24. April 2026 | V4 Preview veröffentlicht. `deepseek-chat` und `deepseek-reasoner` beginnen auf `deepseek-v4-flash` zu routen. |
| **24. Juli 2026** | **`deepseek-chat` und `deepseek-reasoner` vollständig abgeschaltet und nicht mehr zugänglich.** |

### Änderungen in diesem Projekt (11. Mai 2026)

**`index.html`**:
- `MODEL_CONFIG`: `deepseek-chat` (100k Token) → `deepseek-v4-flash` (1.048.576 Token); `deepseek-reasoner` (65k Token) → `deepseek-v4-pro` (1.048.576 Token)
- `MODEL_CAPABILITIES`: aktualisiert auf `deepseek-v4-flash` und `deepseek-v4-pro`
- `DEEPSEEK_MODELS`, `COMPRESSOR_MODELS.deepseek`: auf V4-Namen aktualisiert
- Modell-Dropdowns (Modell-Auswahl + Kompressor-Modell-Auswahl): V4-Optionen
- DeepThink-Logik (8 Stellen): beide Modi lesen `settings.selectedModel` (mit Fallback auf `deepseek-v4-flash`) — siehe das Update vom 19. Juli 2026 weiter unten zu einem inzwischen behobenen Bug in dieser Logik
- Standard-Einstellungen: `selectedModel` und `compressorModel` standardmässig auf `deepseek-v4-flash`
- Frontend-Error-Handler behoben: `response.json()`-Body-Verbrauch verursacht nicht länger leere Fehlermeldungen

**`deepseek-api.py`**:
- Header-Kommentar auf V4-Modelle mit korrekten Kontext-/Output-Grössen aktualisiert
- Standard-Modell-Fallback: `'deepseek-chat'` → `'deepseek-v4-flash'`
- Deprecation-Hinweis zum Header hinzugefügt

**`deepseek-models.py`**: Keine Änderungen nötig — holt die Modellliste live von der DeepSeek API. Gibt bereits korrekt `deepseek-v4-flash` und `deepseek-v4-pro` zurück.

### API-Kompatibilität

Die DeepSeek V4 API verwendet dieselbe Base-URL und dasselbe OpenAI-kompatible Format wie V3. Keine strukturellen Änderungen an `deepseek-api.py` waren nötig — nur die Modellnamen mussten aktualisiert werden.

---

## Wartung & Feature-Update vom 19. Juli 2026

Eine ganztägige Wartungs- und Feature-Session, die einen kritischen Modellauswahl-Bug, mehrere über die Zeit angesammelte Dokumentations-/Modelllisten-Inkonsistenzen über alle fünf Anbieter hinweg sowie die Fertigstellung einer bis dahin nicht funktionierenden Bild-Pipeline (Vision) abdeckte. Dokumentiert in den Changelog-Einträgen 87–89.

### 1. Kritischer Bug: `deepseek-v4-pro` war nie erreichbar

**Symptom**: Die Auswahl von `deepseek-v4-pro` im Modell-Dropdown hatte keine Wirkung — jede Anfrage wurde unabhängig von Dropdown-Auswahl oder DeepThink-Modus mit `deepseek-v4-flash` gesendet.

**Ursache**: Acht Vorkommen desselben Copy-Paste-Fehlers über `index.html` verteilt, die jeweils zu Folgendem auflösten:
```javascript
(currentMode === 'deepthink') ? 'deepseek-v4-flash' : 'deepseek-v4-flash'
```
Beide Zweige des Ternary-Operators lieferten denselben String zurück, wodurch `settings.selectedModel` für den DeepSeek-Anbieter nie ausgelesen wurde — anders als bei jedem anderen Anbieter (Google, OpenAI, Groq, Hugging Face), die korrekt `settings.selectedModel || <Fallback>` verwendeten.

**Fix**: Alle acht Vorkommen (verteilt über `sendMessage()`, `handleRegenerate()`, die Kontext-/Token-Schätzfunktionen und UI-Indikator-Updates) lesen jetzt `settings.selectedModel || 'deepseek-v4-flash'`, konsistent zum an anderer Stelle verwendeten Muster.

**Zugehöriger Fix — veralteter Kontext-Header**: `llmSaveHandler` (der „Apply Settings"-Button im LLM-Einstellungs-Panel) ruft jetzt als letzte Aktion explizit `updateContextDisplay()` auf und garantiert damit, dass der Header `Context: X% (Modell)` die gerade gespeicherte Modellauswahl sofort widerspiegelt statt erst bei der nächsten Kontext-Neuberechnung.

**Zugehöriger Fix — irreführender Modell-Header**: Der Header `Modell: ...` zeigte bisher, nur für DeepSeek, die *komplette* von `deepseek-models.py` gemeldete Modellliste (z. B. `Modell: deepseek-v4-flash, deepseek-v4-pro`) unabhängig davon, welches Modell tatsächlich ausgewählt war — inkonsistent zu jedem anderen Anbieter, der korrekt nur das aktive Modell anzeigte. `updateApiServiceUI()`, die allgemeine UI-Update-Routine und `fetchDeepSeekModels()` wurden alle korrigiert, sodass sie einheitlich über alle Anbieter hinweg `settings.selectedModel` anzeigen.

### 2. Diagnose-Logging: Modellname im Server-Log

Die Funktionen `log_to_file()` und `send_error()` in `deepseek-api.py` erhielten einen optionalen `model`-Parameter. Jede Log-Zeile enthält jetzt ab dem Zeitpunkt, an dem der Request-Body geparst wurde, zusätzlich `| Model: <Name>` — sowohl bei erfolgreichen Anfragen als auch bei Fehlerantworten. Dies ermöglicht die serverseitige Verifikation, welches Modell tatsächlich eine bestimmte Anfrage erhalten hat, unabhängig vom (und zuverlässiger als der) clientseitige(n) UI-Zustand oder der Selbstauskunft des Modells (siehe [DeepSeek Modell-Selbstauskunft](#deepseek-modell-selbstauskunft)).

### 3. Bereinigung toter Modelle

Mehrere in Code-Kommentaren und Auswahllisten referenzierte Modelle waren nicht mehr erreichbar:

| Anbieter | Entferntes Modell | Grund |
|----------|-------------------|-------|
| Google | `gemini-2.0-flash` | Am 1. Juni 2026 abgeschaltet; war zudem das Standard-Fallback-Modell des CGI-Skripts |
| Google | `gemini-1.5-pro` | Bereits vor dieser Bereinigung abgeschaltet |
| Hugging Face | `mistralai/Mixtral-8x7B-Instruct-v0.1` | Wird von keinem Inference Provider mehr auf dem HF-Router gehostet |
| GroqCloud (nur Doku) | `mixtral-8x7b-32768` | Von Groq seit 20. März 2025 deprecated (Dokumentation war veraltet; die Live-Modell-Arrays waren bereits korrekt) |
| GroqCloud (nur Doku) | `gemma2-9b-it` | Von Groq seit 8. Oktober 2025 deprecated (nur Dokumentation) |
| OpenAI | `gpt-5-mini`, `gpt-5.2-chat-latest` | Nicht mehr auf OpenAIs aktueller Modell-/Preisliste (abgelöst durch die GPT-5.4/5.5/5.6-Familie) |

Entfernt aus `GOOGLE_MODELS_PAID`, `HF_MODELS_PAID`, `OPENAI_MODELS_FREE`/`PAID`, `MODEL_CONFIG`, `MODEL_CAPABILITIES`, `AUDIO_CAPABLE_MODELS` und `COMPRESSOR_MODELS`, soweit zutreffend. Das Standard-Fallback-Modell von `google-api.py` wurde von `gemini-2.0-flash` auf `gemini-2.5-flash` geändert. Ein verwaister `MODEL_CONFIG`-Eintrag für das entfernte Mixtral-Modell (vorhanden, obwohl es bereits aus allen Auswahllisten entfernt war) wurde ebenfalls bereinigt.

Zusätzlich fehlte in `MODEL_CONFIG` ein Eintrag für `moonshotai/kimi-k2-instruct-0905`, obwohl es in `GROQ_MODELS_PAID` gelistet war — es fiel stillschweigend auf das Output-Token-Limit von DeepSeek zurück. Ein korrekter Eintrag (131.072 Kontext / 8.192 Output) wurde ergänzt.

### 4. OpenAI-Lineup auf GPT-5.5 / GPT-5.6 aktualisiert

OpenAI veröffentlichte **GPT-5.5** (23. April 2026) und die **GPT-5.6-Familie — Sol, Terra, Luna** (9. Juli 2026, die aktuelle Flaggschiff-Generation), seit die Modell-Konfiguration dieses Projekts zuletzt aktualisiert wurde (10. März 2026). Siehe [OpenAI-Integration](#openai-integration) für die aktualisierten Modelllisten.

Ein zweites, unabhängig entdecktes Problem: `MODEL_CONFIG` enthielt vor diesem Update **keinen einzigen Eintrag für irgendein OpenAI-Modell**. Jede OpenAI-Anfrage — unabhängig vom gewählten Modell — nutzte stillschweigend die Limits von DeepSeek Flash (8.192 Max-Output-Tokens), was Modelle wie `gpt-4.1` (real 32.768 Max-Output) oder die GPT-5.6-Familie (real 128.000 Max-Output) beschnitt. Acht korrekte Einträge wurden ergänzt, mit Kontext-/Output-Werten aus OpenAIs aktueller API-Dokumentation.

### 5. Transparente API-Fehlermeldungen

**Symptom**: API-Fehler von DeepSeek, OpenAI, Groq und Hugging Face erschienen als nacktes `Error: API error (400):` ohne weitere Details, was eine Diagnose allein aus der UI heraus unmöglich machte.

**Ursache**: In drei separaten Fehlerbehandlungs-Zweigen innerhalb von `sendMessage()` wurde die geparste Backend-Fehlerantwort (`errData`) verworfen, sobald sie gegen die beiden bekannten Fehlertypen (`insufficient_quota`, `context_exceeded`) geprüft worden war. War der tatsächliche Fehler keiner von beiden — etwa ein nicht erkannter Parameter, wie in Punkt 6 unten angetroffen —, war die geworfene Fehlermeldung fest auf einen leeren String gesetzt.

**Fix**: Alle drei Zweige extrahieren jetzt `errData.details || errData.error || errData.message` und reichen dies an die angezeigte Fehlermeldung durch, wodurch der tatsächliche, vom Anbieter gelieferte Diagnosetext sichtbar wird.

### 6. `max_tokens` → `max_completion_tokens` für OpenAI

Entdeckt als direkte Folge von Fix 5 oben: Sobald der echte Fehlertext sichtbar wurde, lieferte der erste Live-Test mit `gpt-5.6-luna`:
```
Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.
```
OpenAIs aktuelle Modellgeneration (GPT-5.x und Reasoning-fähige Modelle allgemein) lehnt den Parameter `max_tokens` in der Chat-Completions-API ab. `openai-api.py` sendet jetzt stattdessen `max_completion_tokens` — ein Parameter, der sowohl von älteren Modellen (GPT-4o, GPT-4.1) als auch vom aktuellen GPT-5.x-Lineup akzeptiert wird, wodurch er sich unbedingt statt pro Modell verzweigt verwenden lässt. Live verifiziert gegen sowohl `gpt-5.6-luna` als auch `gpt-4o-mini`.

### 7. Bild-Pipeline fertiggestellt

Siehe den dedizierten Abschnitt [Bild-Unterstützung (Vision)](#bild-unterstützung-vision) oben für die vollständige Beschreibung. Zusammengefasst: `MODEL_CAPABILITIES` wurde pro Anbieter korrekt befüllt (zuvor hatte nur DeepSeek Einträge, alle `images: false`), `currentModelSupportsImages()` wurde korrigiert, um das tatsächlich ausgewählte Modell statt eines unabhängigen, nur-DeepSeek-relevanten Arrays zu prüfen, und die Client-/Server-Verdrahtung, um Bild-Bytes tatsächlich an Google Gemini und OpenAI zu übertragen, wurde erstmals implementiert — Bilder waren zuvor von der UI entgegengenommen worden, erreichten aber nie ein Modell.

### 8. `deploy.sh`: MD5-Prüfsummen-Verifikation

`deploy.sh` gibt jetzt die MD5-Prüfsumme jeder Datei aus, die es in das Produktionsverzeichnis kopiert — direkt nach den Kopier-/Chown-/Chmod-Schritten und vor dem Apache-Reload:
```
=== MD5-Summen der kopierten Dateien (Produktion) ===
4a08bef03d8543cc3e1cbacf1a10bc96  /var/www/deepseek-chat/index.html
42abf2af226184edf979b3721aff0e1c  /var/www/deepseek-chat/cgi-bin/openai-api.py
...
```
Dies erspart einen separaten manuellen `md5sum`-Schritt nach jedem Deploy zur Bestätigung, dass die Produktionsdatei dem beabsichtigten Commit entspricht — ein Schritt, der während derselben Session bereits ein Stale-Deploy-Problem aufgedeckt hatte (ein produktiver `deploy.sh`-Aufruf lief mit einer veralteten gecachten Kopie seiner selbst, da das Skript sich nicht selbst deployt; siehe Hinweis unter [Deploy-Skripte](#deploy-skripte)).

### Geänderte Dateien

`index.html`, `deepseek-api.py`, `google-api.py`, `groq-api.py`, `hugging-api.py`, `openai-api.py`, `shell-scripts/deploy.sh`

---

## Das Hilfsskript `repo2text.sh`

Dieses Bash-Skript wurde speziell entwickelt um den **gesamten Quellcode eines GitHub-Repositorys als einzelne Textdatei zu exportieren** — ideal um den vollständigen Projekt-Kontext in einem einzigen Upload an einen KI-Assistenten zu übergeben.

**Funktionsweise**:
- Klont das Repository mit `git clone --depth 1`.
- Analysiert alle Textdateien (MIME-Typ-Prüfung + `grep -Iq .`) und schreibt sie sequenziell mit eindeutigen Trennzeichen in eine Ausgabedatei.
- Verwendet `sort -z -u` zur Deduplizierung von Dateipfaden vor der Verarbeitung — verhindert doppelte Datei-Einträge in der Ausgabe.
- Verwendet ein eindeutiges Trennzeichen-Format (`############ FILE: pfad/zur/datei ############`) das im Quellcode nicht vorkommen kann.
- Respektiert explizit `.gitignore` und `.gitattributes`.
- Unterstützt TXT-, JSON- und Markdown-Ausgabeformate.
- Erstellt ein ZIP-Archiv der Exportdatei.
- Enthält Metadaten: Commit-Hash, Branch, Export-Zeitstempel.

**Spezielle Optionen**:
- `--flat`: Nur Dateinamen ohne Verzeichnispfade verwenden.
- `-o, --only PFAD`: Nur ein bestimmtes Unterverzeichnis exportieren.
- `-md5, --md5`: MD5-Prüfsumme für jede Datei berechnen und einschliessen.
- Intelligente Remote-URL-Erkennung wenn innerhalb eines bestehenden Git-Repositorys ausgeführt.
- Sowohl `md5sum` (Linux) als auch `md5` (macOS) werden unterstützt.

**Verwendungsbeispiele**:

```bash
# Einfacher Export (interaktiver URL-Prompt)
./repo2text.sh

# Export mit URL als Markdown-Format
./repo2text.sh -f md https://github.com/debian-professional/multi-llm-chat.git

# Nur das 'shell-scripts'-Verzeichnis mit flacher Struktur exportieren
./repo2text.sh --flat -o shell-scripts https://github.com/debian-professional/multi-llm-chat.git

# Export mit MD5-Prüfsummen
./repo2text.sh -md5 https://github.com/debian-professional/multi-llm-chat.git
```

> `repo2text` ist auch als eigenständiges Projekt verfügbar: [github.com/debian-professional/repo2text](https://github.com/debian-professional/repo2text)

---

## Sicherheitsarchitektur im Detail

Sicherheit hatte während der gesamten Entwicklung höchste Priorität. Alle wesentlichen Massnahmen:

### 1. API-Keys — Nie dem Client ausgesetzt

- Alle API-Keys werden ausschliesslich in Apache-Umgebungsvariablen (`/etc/apache2/envvars`) gehalten.
- Jedes CGI-Skript ruft seinen Key via `os.environ.get('..._API_KEY')` ab.
- Der Client kommuniziert nur mit lokalen CGI-Proxies — nie direkt mit externen APIs.
- Selbst ein vollständiger XSS-Angriff auf die Seite kann keine API-Keys leaken.

### 2. Magic-Byte-Prüfung

- Die ersten 20 Bytes jeder hochgeladenen Datei werden gegen eine umfassende Signatur-Datenbank mit 12 ausführbaren Formaten auf 4 Plattformen geprüft.
- Bei Signatur-Übereinstimmung wird der Upload blockiert bevor Inhalte gelesen werden — mit einer detaillierten Fehlermeldung die die erkannte Plattform und das Format zeigt.
- Schutz funktioniert auch wenn bösartige Dateien umbenannt werden (z.B. `malware.exe` → `dokument.pdf`).

### 3. Sichere Session-Speicherung

- Sessions-Verzeichnis: `/var/www/deepseek-chat/sessions/` — `chmod 700`, `www-data`-Eigentümer.
- Jede Session-Datei: `chmod 600`.
- Session-IDs werden serverseitig via Regex validiert bevor Datei-I/O stattfindet — kein Path-Traversal möglich.

### 4. Log ohne sensible Daten

- Geloggt: Zeitstempel, IP-Adressen, HTTP-Methoden, Endpoint-Pfade, Status-Codes, Fehlermeldungen.
- **Niemals geloggt**: API-Keys, vollständige Session-Inhalte, Nachrichtentext (nur 60-Zeichen-Feedback-Previews).
- OPTIONS-Preflight-Anfragen werden herausgefiltert um Log-Flutung zu verhindern.

### 5. Keine direkte Client-API-Kommunikation

- Alle sicherheitskritischen Operationen sind serverseitiges Python-CGI.
- Der Client hat kein Wissen über API-Credentials, Server-Pfade oder Session-Speicher-Pfade.

### 6. Eingabe-Validierung

- Dateien werden durch Erweiterungs-Allowlist UND Magic-Byte-Prüfung validiert.
- Session-IDs werden serverseitig gegen erwartetes Format-Regex validiert.
- Zwischenablage-Einfügen wird gefiltert um Dateipfade zu blockieren bevor sie die API erreichen.
- `Content-Length` wird in CGI-Skripten vor dem Lesen von POST-Bodies validiert.

### 7. Transport-Sicherheit

- HTTPS via `deepseek-chat-ssl.conf` mit Apache mod_ssl erzwungen.
- Klartext-HTTP-Konfiguration (`deepseek-chat.conf`) via `a2dissite` deaktiviert.

---

## Deployment & Verwendung

### Voraussetzungen

- Debian-basiertes Linux (oder beliebiges Linux mit Apache 2.4, Python 3.9+, Bash)
- Apache-Module: `mod_cgi`, `mod_ssl`
- Python-Pakete: `reportlab` (für PDF-Export)
- Für `repo2text.sh`: `jq`, `pv`, `zip`, `git`
- Gültiger API-Key für mindestens einen unterstützten Anbieter

### Installation

**1. Repository klonen** (als User `source`):
```bash
git clone https://github.com/debian-professional/multi-llm-chat.git /home/source/multi-llm-chat
```

**2. API-Keys konfigurieren** in `/etc/apache2/envvars`:
```bash
export DEEPSEEK_API_KEY="sk-..."
export OPENAI_API_KEY="sk-proj-..."
export GOOGLE_API_KEY="AIza..."
export HF_API_KEY="hf_..."
export GRQ_API_KEY="gsk_..."
```

**3. Apache-Konfiguration aktivieren**:
```bash
a2ensite deepseek-chat-ssl.conf
a2dissite deepseek-chat.conf
systemctl restart apache2
```

**4. Erforderliche Verzeichnisse erstellen**:
```bash
mkdir -p /var/www/deepseek-chat/sessions
chown www-data:www-data /var/www/deepseek-chat/sessions
chmod 700 /var/www/deepseek-chat/sessions
```

**5. Deployen** (als root):
```bash
./deploy.sh source
```

**6. Hilfsskripte installieren**:
```bash
./install.sh   # kopiert deploy.sh und sync-back.sh ins Produktionsverzeichnis
```

### Konfiguration

**Modell-Konfiguration** (`MODEL_CONFIG` in `index.html`) — einzige Quelle der Wahrheit für alle Modell-Limits, Stand 19.07.2026:
```javascript
const MODEL_CONFIG = {
    // DeepSeek V4
    'deepseek-v4-flash':    { maxContextTokens: 1048576, maxOutputTokens: 8192,   maxContextMessages: 50  },
    'deepseek-v4-pro':      { maxContextTokens: 1048576, maxOutputTokens: 32768,  maxContextMessages: 50  },
    // Google Gemini
    'gemini-2.5-flash':     { maxContextTokens: 1048576, maxOutputTokens: 8192,   maxContextMessages: 100 },
    'gemini-2.5-pro':       { maxContextTokens: 1048576, maxOutputTokens: 65536,  maxContextMessages: 100 },
    // Hugging Face
    'Qwen/Qwen2.5-72B-Instruct':               { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'mistralai/Mistral-7B-Instruct-v0.3':      { maxContextTokens: 32768,  maxOutputTokens: 4096, maxContextMessages: 40 },
    'microsoft/Phi-3.5-mini-instruct':         { maxContextTokens: 128000, maxOutputTokens: 4096, maxContextMessages: 60 },
    'meta-llama/Meta-Llama-3.1-70B-Instruct':  { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'meta-llama/Meta-Llama-3.1-405B-Instruct': { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    // GroqCloud
    'llama-3.3-70b-versatile':                   { maxContextTokens: 128000, maxOutputTokens: 8192,  maxContextMessages: 80 },
    'llama-3.1-8b-instant':                      { maxContextTokens: 131072, maxOutputTokens: 8192,  maxContextMessages: 80 },
    'meta-llama/llama-4-scout-17b-16e-instruct': { maxContextTokens: 131072, maxOutputTokens: 8192,  maxContextMessages: 80 },
    'qwen/qwen3-32b':                            { maxContextTokens: 131072, maxOutputTokens: 40960, maxContextMessages: 80 },
    'moonshotai/kimi-k2-instruct-0905':          { maxContextTokens: 131072, maxOutputTokens: 8192,  maxContextMessages: 80 },
    // OpenAI (ergänzt am 19.07.2026 — fehlte zuvor komplett, fiel stillschweigend auf DeepSeek-Flash-Limits zurück)
    'gpt-4o-mini':    { maxContextTokens: 128000,  maxOutputTokens: 16384,  maxContextMessages: 80  },
    'gpt-4o':         { maxContextTokens: 128000,  maxOutputTokens: 16384,  maxContextMessages: 80  },
    'gpt-4.1':        { maxContextTokens: 1048576, maxOutputTokens: 32768,  maxContextMessages: 100 },
    'gpt-5.4':        { maxContextTokens: 1048576, maxOutputTokens: 16384,  maxContextMessages: 100 },
    'gpt-5.5':        { maxContextTokens: 1048576, maxOutputTokens: 128000, maxContextMessages: 100 },
    'gpt-5.6-sol':    { maxContextTokens: 1048576, maxOutputTokens: 128000, maxContextMessages: 100 },
    'gpt-5.6-terra':  { maxContextTokens: 1048576, maxOutputTokens: 128000, maxContextMessages: 100 },
    'gpt-5.6-luna':   { maxContextTokens: 1048576, maxOutputTokens: 128000, maxContextMessages: 100 },
};
const DEEPSEEK_MODELS    = ['deepseek-v4-flash', 'deepseek-v4-pro'];
const OPENAI_MODELS_FREE = ['gpt-4o-mini', 'gpt-5.6-luna'];
const OPENAI_MODELS_PAID = ['gpt-5.6-sol', 'gpt-5.6-terra', 'gpt-5.6-luna', 'gpt-5.5', 'gpt-5.4', 'gpt-4o', 'gpt-4.1', 'gpt-4o-mini'];
const GOOGLE_MODELS_FREE = ['gemini-2.5-flash'];
const GOOGLE_MODELS_PAID = ['gemini-2.5-flash', 'gemini-2.5-pro'];
const HF_MODELS_FREE     = ['Qwen/Qwen2.5-72B-Instruct', 'mistralai/Mistral-7B-Instruct-v0.3', 'microsoft/Phi-3.5-mini-instruct'];
const HF_MODELS_PAID     = ['meta-llama/Meta-Llama-3.1-70B-Instruct', 'meta-llama/Meta-Llama-3.1-405B-Instruct', 'Qwen/Qwen2.5-72B-Instruct'];
const GROQ_MODELS_FREE   = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'meta-llama/llama-4-scout-17b-16e-instruct', 'qwen/qwen3-32b'];
const GROQ_MODELS_PAID   = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'meta-llama/llama-4-scout-17b-16e-instruct', 'qwen/qwen3-32b', 'moonshotai/kimi-k2-instruct-0905'];
const AUDIO_CAPABLE_MODELS = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gpt-4o', 'gpt-4.1'];
```

**Sprach-Konfiguration** (`language.xml`): Einen `<language id="custom" name="..." visible="true">`-Block hinzufügen um den Custom-Sprach-Slot zu aktivieren. `has_address_form="true"` für Sprachen mit formell/informell-Unterscheidung setzen.

### Deploy-Skripte

| Skript | Funktion |
|--------|----------|
| `deploy.sh <user>` | Kopiert Dateien von `/home/<user>/multi-llm-chat/var/www/deepseek-chat/` nach `/var/www/deepseek-chat/`, setzt Eigentümerschaft und Berechtigungen, gibt MD5-Prüfsummen jeder kopierten Datei aus, lädt Apache neu |
| `sync-back.sh <user>` | Kopiert geänderte Dateien aus der Produktion zurück ins Quell-Repo |
| `install.sh` | Installiert `deploy.sh` und `sync-back.sh` im Produktionsverzeichnis |
| `tag-release.sh` | Erstellt einen Git-Tag mit automatisch inkrementierter Versionsnummer und pusht ihn. Führt zuerst `git fetch --tags` aus um Konflikte mit bestehenden Remote-Tags zu vermeiden. |

**Wichtig — `deploy.sh` deployt sich nicht selbst.** Die eigene `cp`-Liste des Skripts umfasst `index.html`, `manifest`, `files-directorys`, `cgi-bin/*.py` und `language.xml` — sich selbst kopiert es nie. Nach einer Änderung an `deploy.sh` im Quell-Repo und einem `git pull` auf dem Server bleibt die Produktionskopie unter `/var/www/deepseek-chat/deploy.sh` die **alte** Version, bis sie manuell überkopiert wird:
```bash
cp ~/multi-llm-chat/shell-scripts/deploy.sh /var/www/deepseek-chat/deploy.sh
chmod +x /var/www/deepseek-chat/deploy.sh
```
Dies führte während der Session vom 19. Juli 2026 zu einem echten Stolperstein — `sudo deploy.sh` lieferte auch nach erfolgreichem `git pull` weiterhin die Ausgabe von vor der MD5-Prüfsummen-Erweiterung, weil das aufgerufene Skript noch die veraltete Produktionskopie war.

---

## Projektstruktur

```
/
├── etc/apache2/sites-available/
│   ├── deepseek-chat.conf              (deaktiviert — nur HTTP, leitet zu HTTPS weiter)
│   └── deepseek-chat-ssl.conf          (aktiv — SSL, CGI, API-Keys via envvars)
├── shell-scripts/
│   ├── repo2text.sh                    Exportiert gesamtes Repo als einzelne Textdatei
│   ├── deploy.sh                       Kopiert Quell-Repo → Produktion
│   ├── sync-back.sh                    Kopiert Produktion → Quell-Repo
│   ├── install.sh                      Installiert deploy/sync-back-Skripte
│   └── tag-release.sh                  Erstellt und pusht Git-Versions-Tags
├── var/www/deepseek-chat/
│   ├── index.html                      Hauptanwendung (~5.000 Zeilen, alles JS/CSS/HTML)
│   ├── language.xml                    Alle UI-Texte in allen Sprachen (EN, DE, ES, Custom)
│   ├── manifest                        Design-Manifest (alle Konventionen und Regeln)
│   ├── changelog                       Vollständige Entwicklungsgeschichte (89 Einträge)
│   ├── files-directorys                Dateiübersicht / Verzeichnislisting
│   ├── cgi-bin/
│   │   ├── openai-api.py              Streaming-Proxy zur OpenAI Chat Completions API
│   │   ├── deepseek-api.py            Streaming-Proxy zur DeepSeek Chat Completions API
│   │   ├── google-api.py              Streaming-Proxy zur Google Gemini API (mit Formatkonvertierung)
│   │   ├── hugging-api.py             Streaming-Proxy zum Hugging Face Inference Router
│   │   ├── groq-api.py                Streaming-Proxy zur GroqCloud API (LPU-beschleunigt)
│   │   ├── compress-context.py        Kontext-Komprimierung via zweitem LLM-Call
│   │   ├── deepseek-models.py         Live-Modellliste von DeepSeek /v1/models
│   │   ├── save-session.py            Session-Speicher-Endpoint (POST)
│   │   ├── load-session.py            Session-Liste / Laden-Endpoint (GET)
│   │   ├── delete-session.py          Session-Löschen-Endpoint (DELETE)
│   │   ├── export-pdf.py              PDF-Export via ReportLab
│   │   ├── export-markdown.py         Markdown-Export
│   │   ├── export-txt.py              Klartext-Export
│   │   ├── export-rtf.py              RTF-Export (manuelle Kodierung, keine externe Bibliothek)
│   │   ├── feedback-log.py            Like/Dislike-Feedback-Logging
│   │   └── get-log.py                 Server-Log-Reader
│   ├── logs/                          Server-Log-Dateien (automatisch von Apache/www-data erstellt)
│   ├── kompressor/                    Komprimierungs-Ergebnisdateien (automatisch erstellt)
│   └── sessions/                      Chat-Session-JSON-Dateien (automatisch erstellt, chmod 700)
```

---

## Modell-Konfiguration

Das `MODEL_CONFIG`-Objekt in `index.html` ist die **einzige Quelle der Wahrheit** für alle modellspezifischen Limits über alle fünf Anbieter hinweg. Alle Features die von Modell-Limits abhängen — Kontext-Nutzungsgrad-Anzeige, dynamisches Upload-Limit, Kontext-Overflow-Erkennung, Kompressor-Schwellwerte — lesen aus diesem einzigen Objekt. Ein in `MODEL_CONFIG` fehlendes Modell fällt stillschweigend auf die Limits von DeepSeek Flash zurück, statt laut zu scheitern — dies betraf bis zur Korrektur am 19. Juli 2026 jedes OpenAI-Modell (siehe [Wartung & Feature-Update vom 19. Juli 2026](#wartung--feature-update-vom-19-juli-2026)), weshalb ein neu hinzugefügtes Modell explizit gegen diese Tabelle geprüft werden sollte, statt als funktionierend anzunehmen.

**Modell-Konfiguration aktualisieren**: Wenn ein Anbieter seine Modelle aktualisiert (neues Modell, geänderte Kontext-Limits, veraltetes Modell), muss nur der `MODEL_CONFIG`-Block in `index.html` aktualisiert werden. Keine anderen Dateien benötigen Änderungen, ausser wenn der Modellname auch in den Anbieter-Modelllisten (`DEEPSEEK_MODELS`, `GOOGLE_MODELS_*`, etc.), in `MODEL_CAPABILITIES` oder in `AUDIO_CAPABLE_MODELS` verwendet wird.

Quellen: [OpenAI API Docs](https://platform.openai.com/docs), [DeepSeek API Docs](https://api-docs.deepseek.com), [Google Gemini Docs](https://ai.google.dev/gemini-api/docs), [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers), [GroqCloud Docs](https://console.groq.com/docs/models) *(Stand 19.07.2026)*.

---

## Design-Manifest

Das Projekt enthält eine `manifest`-Datei die alle Design-Entscheidungen, Namenskonventionen und Entwicklungsregeln dokumentiert. Wesentliche Regeln:

- **Alle Buttons**: Ausschliesslich Pill-Style (border-radius: 20px, Höhe: 36px). Eckige Buttons sind verboten.
- **Button-Farben**: Blau (`#0056b3`) für Aktionen, Dunkel-zu-Blau-Toggle für Modi, Rot (`#dc3545`) für destruktive, Grün (`#28a745`) für konstruktive Operationen.
- **Einstellungen**: Ausschliesslich Toggle-Schalter — keine Radio-Buttons, keine Checkboxen irgendwo.
- **Keine Emojis** in Buttons oder Beschriftungen (Ausnahme: das DeepThink-Icon ✦).
- **Kein PHP** — ausschliesslich JavaScript (Client) und Python 3 (Server).
- **Keine externen JavaScript-Frameworks** — kein Node.js, kein React, kein Vue, kein jQuery.
- **Formatierung erhalten**: Bestehende Einrückung und Formatierung in `index.html` darf nie durch automatisierte Tools geändert werden.
- **`AUDIO_CAPABLE_MODELS` muss aktuell gehalten werden** (Manifest-Regel E.1): Wenn ein Modell Audio-Unterstützung gewinnt oder verliert, muss die Konstante sofort aktualisiert werden.
- **Anbieter-Banner erforderlich** (Manifest-Regel E.1): Beim Hinzufügen eines neuen LLM-Anbieters müssen die entsprechenden Kontingent-/Limit-Banner sowohl im CGI-Skript als auch im Client implementiert werden.
- Das Manifest ist eine **separate Datei** und darf nie in `index.html` eingebettet werden.

---

## Bekannte Einschränkungen & technische Hinweise

### „Lost in the Middle" — Eine bekannte KI-Einschränkung

Alle aktuellen Sprachmodelle neigen dazu, Inhalte am **Anfang und Ende** eines langen Kontexts zuverlässig abzurufen, während Inhalte **in der Mitte** manchmal übersehen oder halluziniert werden. (Liu et al., 2023: *„Lost in the Middle: How Language Models Use Long Contexts"*)

**Praktische Auswirkung**:
- Ein Repository-Export dieses Projekts ist ca. 700.000 Zeichen ≈ ~175.000 Token.
- DeepSeek V4-Modelle (`deepseek-v4-flash`, `deepseek-v4-pro`) haben ein 1M-Token-Kontextfenster — der vollständige Repository-Export passt problemlos hinein.
- Google Gemini mit 1–2M-Token-Kontext verarbeitet den Export ohne Probleme.
- OpenAI-Modelle mit 128k-Kontext (z.B. `gpt-4o`) **können** den vollständigen Export **nicht** laden — der Client blockiert den Upload mit einer klaren Fehlermeldung.
- **Empfehlung**: Selbst bei Modellen die den Export technisch verarbeiten können, nur die für die aktuelle Aufgabe relevanten Dateien hochladen um die effektive Aufmerksamkeit des Modells zu maximieren.

### GitHub-Raw-URL-Caching

Nach `git push` ist die neue Version **nicht sofort** via `raw.githubusercontent.com`-URLs verfügbar — GitHub cached diese bis zu 10 Minuten lang. Das ist erwartetes Verhalten und kann nicht umgangen werden. Dateien sind korrekt auf GitHub gespeichert sobald `git push` erfolgreich meldet.

### Nano und Unicode — Kritische Warnung

Dateien mit Unicode-Escape-Sequenzen (wie die Umlaut-Platzhalter-Funktionen) **niemals** mit `nano` oder durch Kopieren und Einfügen in einen Terminal-Emulator bearbeiten.

Nano korrumpiert `\u00e4`-Sequenzen zu Mehrfach-Byte-Müll (`M-CM-$`), was JavaScript-Parsing ohne offensichtliche Fehlermeldung bricht.

**Der einzig sichere Workflow**:
1. Dateien lokal in einem echten Editor bearbeiten (VS Code, gedit, kate).
2. `git add` / `git commit` / `git push` vom lokalen Rechner.
3. Auf dem Server: `git pull` (im Quell-Repo als User `source`).
4. Als root: `./deploy.sh source`.

### Linux/X11/Firefox Paste-Verhalten

Unter Linux mit X11 und Firefox blockiert `e.preventDefault()` in Paste-Event-Handlern Einfüge-Events aus Datei-Managern nicht zuverlässig. Der implementierte Workaround (Einfügen erlauben, Inhalt in `setTimeout(0)` prüfen, leeren und Alert anzeigen wenn Dateipfade erkannt) ist die einzige zuverlässige Lösung für diese plattformspezifische Einschränkung.

### Kontext-Overflow-Erkennung Grenzfälle

Die Kontext-Overflow-Erkennung in allen fünf CGI-Skripten verwendet HTTP-Status-Code-Analyse kombiniert mit Keyword-Matching im API-Fehler-Response-Body. Der Keyword-Satz ist breit genug um Standard-API-Fehlermeldungen abzudecken. Grenzfälle mit ungewöhnlichen Fehlermeldungen durch Anbieter-Infrastruktur-Änderungen werden möglicherweise nicht erkannt und fallen auf eine generische Fehleranzeige zurück.

### DeepSeek Modell-Selbstauskunft

DeepSeek V4 Modelle können ungenaue Selbstauskunft geben wenn sie nach ihrer Kontextfenster-Grösse oder Version gefragt werden — sie antworten basierend auf ihren Trainingsdaten, nicht ihrer tatsächlichen API-Konfiguration. Das tatsächlich deployete Modell (`deepseek-v4-flash` oder `deepseek-v4-pro`) kann verifiziert werden via:
```bash
source /etc/apache2/envvars && curl -s https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

---

## Abhängigkeiten

| Komponente | Zweck | Installation |
|-----------|-------|-------------|
| Apache 2.4 | Webserver, CGI, SSL | `apt install apache2` |
| Python 3.9+ | Alle serverseitigen CGI-Skripte | `apt install python3` |
| reportlab | Serverseitiger PDF-Export | `pip3 install reportlab --break-system-packages` |
| PDF.js 3.11.174 | Clientseitige PDF-Textextraktion | CDN (automatischer Fallback auf sekundäres CDN) |
| jq | JSON-Verarbeitung in `repo2text.sh` | `apt install jq` |
| pv | Fortschrittsanzeige in `repo2text.sh` | `apt install pv` |
| git | Versions-Management | `apt install git` |
| zip | Archiv-Erstellung in `repo2text.sh` | `apt install zip` |

Keine exotischen Frameworks — alle Abhängigkeiten sind Standard-Pakete in einer Debian-Umgebung oder bewährte CDN-Bibliotheken.

---

## Fazit / Warum dieses Projekt heraussticht

Dieses Projekt demonstriert professionelles Web-Development in einem minimalistischen, Sicherheit-zuerst-Ansatz — ohne unnötigen Overhead, aber mit höchsten Standards für Sicherheit, Korrektheit und Benutzerfreundlichkeit.

**Architektur**:
- Saubere Trennung von Client (reines HTML/JS) und Server (Python CGI) ohne Vermischung der Verantwortlichkeiten.
- API-Keys nie exponiert — selbst ein vollständiger XSS-Angriff kann sie nicht leaken.
- Einzeldatei-Client (`index.html`) der vollständig eigenständig ist, aber intern hochgradig modular.
- Keine Build-Pipeline — Entwicklungsumgebung ist identisch mit Produktion.

**Benutzererfahrung**:
- Streaming-Antworten mit Sub-Sekunden-First-Token-Latenz.
- Einzigartiges flexibles Kontext-Management — beliebige Nachricht und alle folgenden löschen.
- Intelligentes Zwischenablage-Handling für Text, Bilder und Dateipfad-Schutz.
- Audio-Aufnahme direkt im Browser für Gemini (alle Modelle) und OpenAI (`gpt-4o`, `gpt-4.1`).
- Kompressor — automatische Kontext-Komprimierung ermöglicht unbegrenzt lange Gespräche.
- Kontext-Überschreitung — interaktive In-Chat-Box mit smartem Kontext-Carry-Over (Option C).
- Kontingent-Banner — klare, dauerhafte visuelle Rückmeldung für erschöpftes Guthaben oder Tageslimits.
- In Zwischenablage kopieren — gesamter Chat clientseitig mit einem Klick exportiert.
- Mehrsprachige Unterstützung mit Anredeform-Unterscheidung, aus externer XML geladen.

**Engineering**:
- Magic-Byte-Prüfung erkennt ausführbare Dateien unabhängig von der Dateiendung — 12 Signaturen auf 4 Plattformen.
- Umlaut-Platzhalter-System löst eine fundamentale DeepSeek API-Einschränkung für deutschen Text.
- Vorwärtskompatible Modell-Fähigkeiten-Map — ein neues Modell hinzufügen erfordert nur einen einzigen Config-Eintrag (wobei `MODEL_CONFIG` und `MODEL_CAPABILITIES` explizit synchron gehalten werden müssen — eine Lücke, die bis zum 19. Juli 2026 dazu führte, dass OpenAIs komplettes Modell-Lineup stillschweigend mit dem falschen Output-Token-Limit lief).
- End-to-End-Bild-Pipeline für Google Gemini und OpenAI — base64-Bilddaten fliessen vom Browser-Upload/-Paste bis hin zu nativen `inline_data`/`image_url`-API-Payloads, gesteuert über eine Pro-Modell-Fähigkeiten-Map statt einer hartcodierten Annahme.
- Präzises Kompressor-Zusammenfassungs-Verwerfen: Zusammenfassung wird ungültig wenn Kontext nach manueller Löschung unter den zuletzt ausgelösten Schwellwert fällt.
- Dynamisches Upload-Limit: 75% des Kontextfensters des aktiven Modells in Zeichen — skaliert automatisch von 384k Zeichen (`gpt-4o`) bis ~3,1M Zeichen (`deepseek-v4-flash`, `gemini-2.5-flash`, die GPT-5.6-Familie).
- Deploy-Verifikation fest in die Deployment-Pipeline eingebaut — `deploy.sh` gibt MD5-Prüfsummen jeder kopierten Datei aus und deckt veraltete/nicht übereinstimmende Deploys sofort auf, statt sie erst durch unerklärliches Laufzeitverhalten zu entdecken.
- Vollständiger Audit-Trail via Git, detaillierter 89-Einträge-Changelog und Design-Manifest.

**DeepSeek V4 bereit** — migriert auf `deepseek-v4-flash` und `deepseek-v4-pro` mit 1M-Token-Kontextfenstern, vor der Abschalt-Deadline für Legacy-Modelle am 24. Juli 2026.

**GPT-5.6 bereit** — OpenAI-Lineup aktuell bis zur Sol/Terra/Luna-Generation (9. Juli 2026), mit durchgängig verwendetem `max_completion_tokens` für Kompatibilität über das gesamte Modell-Spektrum hinweg.

**Für einen professionellen Entwickler** demonstriert dieses Projekt:
- **Sicherheitsbewusstsein** — API-Key-Schutz, Executable-Erkennung, sichere Session-Speicherung, kein Path-Traversal.
- **Strukturierte Disziplin** — Design-Manifest, Versions-Tags, strikte UI-Konventionen, 89-Einträge-Changelog.
- **Problem-Lösungstiefe** — X11-Paste-Verhalten, Umlaut-Korrumpierung, PDF-Binary-Output-Probleme, „Lost in the Middle", Kontext-Overflow-Verkettung, und eine taggleiche Ursachenkette von einer leeren Fehlermeldung bis zu einem fehlenden OpenAI-Request-Parameter.
- **Vollständige Dokumentation** — Inline-Code-Kommentare, dediziertes Manifest, Dokumentations-Header pro Skript, dreisprachiges README.

---

*Zuletzt aktualisiert: 19.07.2026*



