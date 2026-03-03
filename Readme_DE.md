# DeepSeek Chat – Ein privater, sicherer Chat-Client für die DeepSeek API

**DeepSeek Chat** ist ein vollständig eigenständiger, lokal gehosteter Chat-Client für die DeepSeek API. Er wurde mit Fokus auf **Sicherheit, Einfachheit und professionelle Benutzerfreundlichkeit** entwickelt. Die Architektur erfordert keine exotischen Frameworks und verwendet ausschließlich bewährte Technologien: Apache als Webserver, Python CGI für die serverseitige Logik und reines HTML/JavaScript/CSS auf der Client-Seite.

Wesentliche Merkmale:
- **Einzigartiges Kontext-Management** – Einzelne Nachrichten und alle nachfolgenden löschen. Der Chat bleibt konsistent und die Token-Nutzung wird dynamisch aktualisiert.
- **Maximale Sicherheit** – Der API-Key ist auf der Client-Seite niemals sichtbar, Uploads sind durch Magic-Byte-Prüfung gegen ausführbare Dateien geschützt, und Sessions werden mit restriktiven Dateiberechtigungen gespeichert.
- **Keine exotischen Frameworks** – Alles basiert auf Apache, Python, Bash und reinem HTML/JS.
- **Professionelle Exportfunktionen** – PDF, Markdown, TXT, RTF für den gesamten Chat oder einzelne Nachrichten.
- **Mehrsprachige Unterstützung** – Vollständige UI-Übersetzung über externe `language.xml` (Englisch, Deutsch, Spanisch, erweiterbar mit benutzerdefinierten Sprachen).
- **Zwischenablage-Integration** – Ctrl+V-Handler mit Dialog für Text, Bilder und Schutz vor versehentlichem Einfügen von Dateipfaden.
- **Streaming-Antworten** – KI-Antworten erscheinen Token für Token, genau wie bei ChatGPT oder Claude.
- **Enthaltenes Werkzeug** – Das Skript `repo2text.sh` exportiert das gesamte Repository als Textdatei, ideal für die Arbeit mit KI-Assistenten (wie diesem hier).

---

## Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Architektur](#architektur)
- [Einzigartiges Kontext-Management](#einzigartiges-kontext-management)
- [Features im Detail](#features-im-detail)
  - [Chat-Interface](#chat-interface)
  - [Streaming-Antworten](#streaming-antworten)
  - [Zwischenablage-Handler (Ctrl+V)](#zwischenablage-handler-ctrlv)
  - [Datei-Upload mit Sicherheitsprüfung](#datei-upload-mit-sicherheitsprüfung)
  - [Umlaut-Platzhalter-System](#umlaut-platzhalter-system)
  - [DeepThink-Modus](#deepthink-modus)
  - [Modell-Erkennung & Fähigkeiten](#modell-erkennung--fähigkeiten)
  - [Mehrsprachiges System](#mehrsprachiges-system)
  - [Einstellungen (Toggles statt Radio-Buttons)](#einstellungen-toggles-statt-radio-buttons)
  - [Session-Management](#session-management)
  - [Exportfunktionen](#exportfunktionen)
  - [Feedback-Buttons & Logging](#feedback-buttons--logging)
  - [Dynamische Kontextanzeige](#dynamische-kontextanzeige)
  - [Datei-Karten-Anzeige](#datei-karten-anzeige)
- [Das Hilfsskript `repo2text.sh`](#das-hilfsskript-repo2textsh)
- [Sicherheitsarchitektur im Detail](#sicherheitsarchitektur-im-detail)
- [Deployment & Nutzung](#deployment--nutzung)
  - [Voraussetzungen](#voraussetzungen)
  - [Installation](#installation)
  - [Konfiguration](#konfiguration)
  - [Deploy-Skripte](#deploy-skripte)
- [Projektstruktur](#projektstruktur)
- [Modell-Konfiguration](#modell-konfiguration)
- [Design-Manifest](#design-manifest)
- [Bekannte Einschränkungen & technische Hinweise](#bekannte-einschränkungen--technische-hinweise)
- [Abhängigkeiten](#abhängigkeiten)
- [Fazit / Was dieses Projekt auszeichnet](#fazit--was-dieses-projekt-auszeichnet)

---

## Übersicht

DeepSeek Chat ist eine **lokale Webanwendung**, die über die DeepSeek API kommuniziert (Modelle `deepseek-chat` und `deepseek-reasoner`). Entwickelt für eine private Serverumgebung (Debian), kann sie auf jedem System mit Apache und Python 3 betrieben werden. Ziel war es, einen **sicheren, erweiterbaren und benutzerfreundlichen** Chat-Client zu schaffen, der ohne Cloud-Abhängigkeiten auskommt und volle Kontrolle über die Daten bietet.

Das Projekt ist über mehrere Wochen aktiver Entwicklung kontinuierlich gewachsen und hat Features wie Streaming, Session-Management, Exportfunktionen, mehrsprachige Unterstützung, Zwischenablage-Integration und robuste Sicherheitsmaßnahmen hinzugewonnen — alles ohne externe JavaScript-Frameworks einzuführen.

---

## Architektur

Die Architektur ist bewusst einfach, aber durchdacht:

### 1. Client
- Reines HTML/JavaScript/CSS, bereitgestellt über Apache.
- Keine Build-Tools, kein Node.js, keine externen Bibliotheken (außer PDF.js zur PDF-Textextraktion im Browser).
- Die gesamte Client-Logik (Nachrichtenverarbeitung, UI-Aktualisierungen, Streaming-Empfang, Sprachwechsel, Zwischenablage-Handling) ist in einer einzigen `index.html` gekapselt.
- Alle UI-Texte werden beim Start aus einer externen `language.xml` geladen — keine fest codierten Strings im HTML.

### 2. Server
- **Apache** mit CGI-Unterstützung (`mod_cgi`).
- **Python-CGI-Skripte** unter `/cgi-bin/` verwalten:
  - Kommunikation mit der DeepSeek API (`deepseek-api.py`) — mit Streaming (Server-Sent Events)
  - Modell-Erkennung (`deepseek-models.py`) — fragt `/v1/models` beim Start ab
  - Session-Speicherung und -Abruf (`save-session.py`, `load-session.py`, `delete-session.py`)
  - Exporte in verschiedenen Formaten (`export-pdf.py`, `export-markdown.py`, `export-txt.py`, `export-rtf.py`)
  - Feedback-Logging (`feedback-log.py`)
  - Log-Anzeige (`get-log.py`)
- Der **API-Key** wird ausschließlich über eine Apache-Umgebungsvariable (`DEEPSEEK_API_KEY` in `/etc/apache2/envvars`) bereitgestellt — **niemals im Client-Code**.
- Ein einziger `ScriptAlias /cgi-bin/ /var/www/deepseek-chat/cgi-bin/` deckt alle Skripte ab — beim Hinzufügen neuer Skripte sind keine Apache-Änderungen erforderlich.

### 3. Datenspeicherung
- **Sessions** werden als JSON-Dateien in `/var/www/deepseek-chat/sessions/` mit `chmod 700` gespeichert.
- **Logs** werden in `/var/www/deepseek-chat/cgi-bin/deepseek-chat.log` geschrieben (ohne API-Key oder Session-Inhalte).
- **Einstellungen** verbleiben lokal im Browser (`localStorage`) mit Versionskontrolle.
- **Sprachdaten** werden beim Seitenaufruf aus `language.xml` via `fetch()` geladen.

### 4. Hilfsskripte
- `deploy.sh`, `sync-back.sh`, `install.sh`, `tag-release.sh` erleichtern das Deployment zwischen Entwicklungs- und Produktionsverzeichnissen.
- `repo2text.sh` exportiert das gesamte Repository als Textdatei für KI-Assistenten.

---

## Einzigartiges Kontext-Management

Eines der herausragenden Features ist die Möglichkeit, **einzelne Nachrichten zusammen mit allen nachfolgenden zu löschen**. Das geht weit über das typische "letzte Nachricht löschen" hinaus und ermöglicht eine flexible Korrektur des Gesprächsverlaufs.

**Implementierung**:
- Jede Nachricht (Benutzer & KI) erhält eine eindeutige `id` (Format: `msg_N`) und wird in einem Array `contextHistory.messages` gespeichert.
- Die Funktion `deleteMessage(msgId)` ermittelt den Index der Nachricht, kürzt das Array ab `index` und entfernt alle nachfolgenden Elemente aus dem DOM (einschließlich Trennlinien).
- Die Token-Schätzung (`updateContextEstimation()`) wird sofort neu berechnet, ebenso die prozentuale Kontextauslastung in der Kopfzeile.
- Die geänderte Session wird anschließend automatisch gespeichert (`saveSession()`).

**Warum ist das einzigartig?**
Viele Chat-Clients erlauben nur das Löschen der letzten Nachricht oder gar keine Verlaufsmanipulation. Hier kann der Benutzer **jeden beliebigen Punkt im Gespräch als neuen Ausgangspunkt definieren** — ideal zum Testen, Korrigieren oder zum Bereinigen des Kontextfensters ohne den gesamten Chat zu verlieren.

**Regenerieren-Funktion**: Zusätzlich zum Löschen hat jede KI-Antwort einen "Regenerieren"-Button, der die alte Antwort löscht und automatisch eine neue auf Basis derselben Benutzernachricht generiert — unter Verwendung des vollständigen Gesprächskontexts bis zu diesem Punkt.

---

## Features im Detail

### Chat-Interface

- **Dark Mode** (fest, keine Option) — augenschonend, professionelles Erscheinungsbild.
  - Hintergrund: `#121212`, Text: `#f0f0f0`, Akzent: `#0056b3`
- **Server-Kopfzeile** zeigt Servername, interne IP-Adresse, dynamische Kontextauslastung und erkannte Modellnamen.
- **Nachrichten-Container** mit Hover-Buttons (Feedback, Export, Löschen).
- **Textarea** expandiert beim Fokus von 40px auf 120px mit weicher CSS-Animation — Enter sendet, Shift+Enter erzeugt eine neue Zeile.
- Alle Buttons folgen einem strengen **Pill-Style**-Design (border-radius: 20px, height: 36px) — keine eckigen Buttons.
- Benutzernachrichten erscheinen in Blau (`#4dabf7`), KI-Antworten in Weiß auf dunklem Hintergrund.
- Automatische Zeilenumbruch-Beibehaltung (`white-space: pre-wrap`) für alle Nachrichteninhalte.
- Automatisches Scrollen zur neuesten Nachricht während und nach dem Streaming.

### Streaming-Antworten

KI-Antworten werden **Token für Token** über Server-Sent Events (SSE) empfangen und angezeigt:

- `deepseek-api.py` sendet Anfragen an DeepSeek mit `stream: True` und leitet den Event-Stream direkt weiter.
- `index.html` liest den Stream über die `ReadableStream`-API und `TextDecoder`.
- Jedes empfangene Token wird in Echtzeit an das Nachrichten-Element angehängt.
- Der psychologische Effekt ist erheblich: Die ersten Token erscheinen innerhalb von ~0,3 Sekunden statt nach 8+ Sekunden Warten auf eine vollständige Antwort.
- Sowohl `sendMessage()` als auch `handleRegenerate()` verwenden identische Streaming-Logik.
- Auto-Scroll bleibt während des Streamings aktiv.

**Technische Header**, die von `deepseek-api.py` für korrektes Streaming gesetzt werden:
```
Content-Type: text/event-stream
X-Accel-Buffering: no
Cache-Control: no-cache
```

### Zwischenablage-Handler (Ctrl+V)

Ein ausgefeilter Zwischenablage-Handler fängt Einfüge-Ereignisse ab und reagiert intelligent je nach Inhaltstyp:

**Textinhalt** → Ein Einfüge-Dialog erscheint mit zwei Optionen:
- "An Cursor-Position einfügen" — fügt den Text direkt an der Cursor-Position ins Eingabefeld ein
- "Als Datei anhängen" — behandelt den Zwischenablage-Text als `clipboard.txt` und hängt ihn als Datei an die nächste Nachricht an

**Bildinhalt** → Eine Thumbnail-Vorschau-Box erscheint über dem Eingabefeld mit dem Bild, seiner Größe in KB und einem Entfernen-Button. Das Bild ist bereit, mit der nächsten Nachricht gesendet zu werden (sofern das Modell Bilder unterstützt).

**Dateipfade aus dem Dateimanager (XFCE/Thunar, KDE/Dolphin)** → Diese werden blockiert und ein Alert wird angezeigt:
> "Im Dateimanager kopierte Dateien können vom Browser nicht gelesen werden. Bitte verwende stattdessen den Button 'Datei hochladen'."

**Technischer Hintergrund**: Unter Linux/X11/Firefox blockiert `e.preventDefault()` Paste-Ereignisse nicht zuverlässig. Die Lösung besteht darin, das Einfügen zuzulassen, dann den Inhalt des Eingabefelds sofort via `setTimeout(0)` zu prüfen und ihn zu löschen, wenn Dateipfade erkannt werden. Erkennungslogik: 2 oder mehr Zeilen, bei denen jede Zeile mit `/` oder `file://` beginnt. Ein `requestAnimationFrame`-Aufruf stellt sicher, dass das Eingabefeld visuell geleert wird, bevor der Alert-Dialog erscheint.

### Datei-Upload mit Sicherheitsprüfung

- Akzeptierte Formate: `.txt`, `.pdf`, `.doc`, `.docx`, `.jpg`, `.jpeg`, `.png`, `.csv`, `.xlsx`, `.pptx`
- Verarbeitbare Formate (Inhaltsextraktion): `.txt`, `.pdf`
- Andere akzeptierte Formate: als binärer Kontext angehängt (ohne Textextraktion)
- Maximale Dateigröße: **10 MB**
- Maximaler extrahierter Inhalt: **250.000 Zeichen** (ausreichend für große Textdateien und Repository-Exporte)

**Magic-Byte-Prüfung** (erste 20 Bytes) erkennt und blockiert ausführbare Dateien unabhängig von der Dateinamenerweiterung:

| Plattform | Format | Signatur |
|----------|--------|-----------|
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
| Linux/macOS | Shell Script | `23 21` (#!) |
| Python | Bytecode (.pyc) | `55 0D 0D 0A` |

**PDF-Extraktion**: Verwendet PDF.js 3.11.174, das vom CDN geladen wird, mit automatischem Fallback auf ein sekundäres CDN. Der Fortschritt wird seitenweise angezeigt. Extraktions-Timeout: 30 Sekunden.

**Hochgeladene Dateien werden als Datei-Karten** in der Benutzernachricht angezeigt (siehe [Datei-Karten-Anzeige](#datei-karten-anzeige)).

### Umlaut-Platzhalter-System

Eine einzigartige Lösung für ein grundlegendes Problem mit der DeepSeek API und deutschem Text:

**Problem**: DeepSeek ersetzt intern deutsche Umlaute in Dateiinhalten durch ASCII-Äquivalente (z.B. `Ä → AeNDERUNG`, `Ü → MUeSSEN`). Dieses Verhalten kann nicht durch System-Prompts oder API-Parameter unterdrückt werden.

**Lösung**: Vor dem Senden von Dateiinhalten an DeepSeek werden Umlaute durch eindeutige Platzhalter ersetzt. DeepSeek gibt diese Platzhalter unverändert zurück. JavaScript ersetzt sie nach dem Empfang wieder durch echte Umlaute.

| Original | Platzhalter |
|----------|------------|
| `ä` | `[[AE]]` |
| `ö` | `[[OE]]` |
| `ü` | `[[UE]]` |
| `ß` | `[[SS]]` |
| `Ä` | `[[CAE]]` |
| `Ö` | `[[COE]]` |
| `Ü` | `[[CUE]]` |

**Wichtiges Implementierungsdetail**: Die Funktionen `encodeUmlautsForAI()` und `decodeUmlautsFromAI()` verwenden **ausschließlich Unicode-Escape-Sequenzen** (`\u00e4` statt `ä`) und `split/join` statt Regex — dies ist entscheidend, um Korruption beim Transfer über Git zu vermeiden.

Das Decode läuft **sowohl während des Streamings** (Token für Token) als auch nach der vollständigen Antwort.

Dieses System wird **nur auf Dateiinhalte** angewendet, nicht auf reguläre Benutzernachrichten oder System-Prompts.

### DeepThink-Modus

- Umschaltbar über einen dedizierten Button (Pill-Mode-Style) in der zweiten Button-Zeile.
- Im DeepThink-Modus wird das Modell `deepseek-reasoner` verwendet (echtes Chain-of-Thought-Reasoning).
- Der Button ändert sich visuell: dunkel/inaktiv (`#2d2d2d`) → aktiv blau (`#1e3a5f` Hintergrund, `#4dabf7` Rand und Text).
- Eine Indikatorleiste erscheint unter den Buttons: "DeepThink-Modus aktiv: Tiefgehende Analyse läuft".
- Kontextlimits und Output-Token-Limits werden automatisch angepasst (siehe [Modell-Konfiguration](#modell-konfiguration)).
- Der Modus wird bei jeder Nachricht aufgezeichnet und in Exporten angezeigt.
- Der Standard-Modus (Chat oder DeepThink) kann in den Einstellungen festgelegt und in `localStorage` gespeichert werden.

### Modell-Erkennung & Fähigkeiten

Beim Start fragt der Client `/cgi-bin/deepseek-models.py` ab, das seinerseits den DeepSeek `/v1/models`-Endpunkt aufruft:

- Erkannte Modell-IDs werden in der Server-Kopfzeile angezeigt: `Modell: deepseek-chat, deepseek-reasoner`
- Eine `MODEL_CAPABILITIES`-Map definiert, welche Modelle Bilder unterstützen:
  ```javascript
  const MODEL_CAPABILITIES = {
      'deepseek-chat':     { images: false, text: true },
      'deepseek-reasoner': { images: false, text: true },
      'deepseek-v4':       { images: true,  text: true },  // bereit für zukünftige Modelle
      'default':           { images: false, text: true },
  };
  ```
- Wenn ein Bild über die Zwischenablage eingefügt oder eine `.jpg`/`.png`-Datei hochgeladen wird und das aktuelle Modell keine Bilder unterstützt, blockiert ein Alert die Operation.
- Diese Architektur ist **zukunftskompatibel**: Wenn DeepSeek V4 mit Bildunterstützung veröffentlicht wird, funktioniert es automatisch ohne Code-Änderungen.

### Mehrsprachiges System

Die Benutzeroberfläche unterstützt mehrere Sprachen, die aus einer externen `language.xml`-Datei geladen werden:

**Aktuell enthaltene Sprachen**:
- Englisch (`en`) — Standard
- Deutsch (`de`) — mit formeller/informeller Anredeform (Sie/Du)
- Spanisch (`es`) — mit formeller/informeller Anredeform (Usted/Tú)
- Custom-Slot (`custom`) — kann über `visible="true"` in `language.xml` aktiviert werden

**Funktionsweise**:
- Alle UI-Texte werden über numerische IDs referenziert (z.B. `t(205)` = Beschriftung des Senden-Buttons).
- `loadLanguage()` lädt und parst `language.xml` beim Seitenaufruf.
- `t(id)` gibt den Text für die aktuelle Sprache zurück, mit Fallback auf Englisch wenn nicht gefunden.
- `tf(id, ...args)` unterstützt Platzhalter-Substitution (`{0}`, `{1}`, ...).
- `tform(idFormal, idInformal)` gibt den passenden Text basierend auf der gewählten Anredeform zurück.
- Sprachwechsel erfolgt sofort ohne Seitenneuladen.
- Die gewählte Sprache wird in `localStorage` gespeichert.

**Anredeform-System (Deutsch/Spanisch)**:
- Sprachen können `has_address_form="true"` in `language.xml` deklarieren.
- Für solche Sprachen zeigt das Einstellungs-Panel eine "Anredeform"-Gruppe (Formell/Informell).
- Die gewählte Form beeinflusst: System-Prompt (erzwingt konsistente KI-Antworten), Eingabe-Platzhalter, alle Einstellungsbeschreibungen.
- Englisch hat keine Anredeform-Unterscheidung.

**System-Prompt** wird dynamisch aufgebaut basierend auf Sprache, Anredeform und Modus:
- Basis-Prompt (Text-IDs 29/30 für formell/informell)
- DeepThink-Ergänzung (Text-IDs 31/32)
- Eine strikte Anweisung zur Dateidarstellung wird immer auf Englisch angehängt — um konsistentes Verhalten unabhängig von der UI-Sprache sicherzustellen.

### Einstellungen (Toggles statt Radio-Buttons)

Alle Einstellungen verwenden **Toggle-Schalter** (links-nach-rechts schiebend), niemals Radio-Buttons oder Checkboxen:

| Gruppe | Einstellung | Toggle-Farbe |
|-------|---------|-------------|
| Sprache | EN / DE / ES / Custom | Grün (persönliche Präferenz) |
| Anredeform | Formell / Informell | Grün (persönliche Präferenz) |
| Standard-Modus | Normaler Chat / DeepThink | Blau (technischer Modus) |
| Datenschutz | Daten nicht für Training verwenden | Grün |

**Toggle-Verhalten**:
- Innerhalb einer Gruppe verhalten sich Toggles wie Radio-Buttons: Das Aktivieren eines Toggles deaktiviert die anderen.
- Ein Klick auf eine beliebige Stelle der `setting-item`-Zeile aktiviert den zugehörigen Toggle.
- Visuelles Feedback: Aktive Elemente erhalten einen farbigen Hintergrund (`#1a2e1a` grün oder `#1e3a5f` blau).

**Datenschutz-Toggle**: Setzt den Header `X-No-Training: true` in API-Anfragen (unterstützt durch DeepSeeks Opt-out-Mechanismus).

**Einstellungs-Persistenz**: Alle Einstellungen werden in `localStorage` unter dem Schlüssel `deepseekSettings` gespeichert. Aktuelle `SETTINGS_VERSION: 1.3`. Die Funktion `migrateSettings()` bietet Rückwärtskompatibilität mit älteren gespeicherten Einstellungen.

### Session-Management

Jedes Gespräch wird automatisch als benannte Session verwaltet:

- **Session-ID-Format**: `YYYY-MM-DD_HHMMSS_random` (z.B. `2026-02-16_143045_abc123`) — clientseitig generiert, serverseitig validiert.
- **Automatisches Speichern**: Nach jedem Nachrichtenpaar (Benutzer + KI) wird das vollständige `contextHistory.messages`-Array als JSON-Datei auf dem Server gespeichert.
- **Session-Dateiformat**: `{sessionId}.json` in `/var/www/deepseek-chat/sessions/`, `chmod 600`.
- **Chat-Verlauf laden-Modal**: Zeigt alle gespeicherten Sessions mit ID, Datum, Nachrichten-Vorschau und Nachrichtenanzahl. Jede Session hat [Laden]- (grün) und [Löschen]- (rot) Buttons.
- **Lade-Verhalten**: Beim Laden einer Session wird der aktuelle Chat zuerst automatisch gespeichert, dann wird die gewählte Session mit vollständigem Nachrichtenverlauf und UI-Rekonstruktion wiederhergestellt.
- **Session-Löschung**: Die JSON-Datei wird sofort vom Server gelöscht.

**CGI-Skripte**:
- `save-session.py` — POST: empfängt `{sessionId, messages}`, validiert ID-Format, schreibt JSON
- `load-session.py` — GET: gibt Liste mit Vorschauen zurück; GET mit `?id=`: gibt vollständige Session-Daten zurück
- `delete-session.py` — DELETE: entfernt Session-Datei

### Exportfunktionen

**Globaler Export** (Dropdown-Button in der Hauptzeile):

| Format | Erzeugung | Enthält |
|--------|-----------|---------|
| PDF | Serverseitig (ReportLab) | Kopfzeile, Statistiken, Inhaltsverzeichnis, vollständiger Chat |
| Markdown | Serverseitig | Identische Struktur wie PDF, mit Markdown-Ankern |
| TXT | Serverseitig | Klartext mit Trennzeichen |
| RTF | Serverseitig | RTF-Format, Umlaute als RTF-Codes (keine externe Bibliothek) |

**Einzel-Nachrichten-Export** (Hover-Button bei jeder Nachricht):

| Format | Erzeugung |
|--------|-----------|
| TXT | Clientseitig (JavaScript Blob, kein Server-Roundtrip) |
| Markdown | Clientseitig |
| RTF | Clientseitig |
| PDF | Serverseitig (einzelne Nachricht an `export-pdf.py` gesendet) |

**Export-Inhalt** (PDF/Markdown):
- Kopfzeile mit Servername, IP, Exportdatum, Sprach-/Anredeform-Einstellungen
- Statistik-Bereich: Nachrichtenanzahl, verwendete Modi, angehängte Dateien, geschätzte Tokens, Dauer
- Inhaltsverzeichnis mit allen Nachrichten
- Vollständiger Chat-Verlauf mit Zeitstempeln und Modus-Indikatoren
- Farbkodierung nach Nachrichten-Rolle und Modus

**Technischer Hinweis PDF**: Binäre PDF-Daten werden ausschließlich über `sys.stdout.buffer` mit als Bytes codierten HTTP-Headern geschrieben — dies vermeidet den „Bad header"-Fehler, der auftritt, wenn `print()` (Text-Modus) mit binärer Ausgabe gemischt wird.

### Feedback-Buttons & Logging

Vier Buttons erscheinen beim Hover für jede KI-Antwort (linke Seite, unten):

- **Kopieren** — Kopiert Nachrichtentext in die Zwischenablage; zeigt "Kopiert!" für 2 Sekunden, dann Reset.
- **Mag ich** — Markiert die Antwort positiv (blau hervorgehoben); sendet einen LIKE-Eintrag in das Server-Log. Erneutes Klicken entfernt das Like.
- **Mag ich gar nicht** — Markiert die Antwort negativ (rot hervorgehoben); sendet einen DISLIKE-Eintrag. Like und Dislike schließen sich gegenseitig aus.
- **Regenerieren** — Entfernt die aktuelle KI-Antwort aus Kontext und DOM, ruft dann die API erneut mit derselben Benutzernachricht und dem vollständigen vorherigen Verlauf auf.

**Serverseitiges Log-Format** (`deepseek-chat.log`):
```
2026-02-17 17:30:00 | 192.168.1.x | FEEDBACK | LIKE | msg_5 | "Erste 60 Zeichen der Nachricht..."
2026-02-17 17:30:00 | 192.168.1.x | POST | /cgi-bin/deepseek-api.py | 200
```
**Niemals geloggt**: API-Keys, Session-Inhalte oder Nachrichtentext über die 60-Zeichen-Feedback-Vorschau hinaus.

### Dynamische Kontextanzeige

Die Server-Kopfzeile zeigt vier Informationszeilen:
1. Servername (in Blau, `#4dabf7`)
2. `IP: xxx.xxx.xxx.xxx`
3. `Kontext: XX% (Modellname)`
4. `Modell: deepseek-chat, deepseek-reasoner`

**Berechnung der Kontextauslastung**:
- Geschätzte Tokens = Gesamtzeichen in aktuellen Nachrichten × `TOKENS_PER_CHAR` (0,25)
- Es werden nur die letzten N Nachrichten gezählt (N = `maxContextMessages` aus `MODEL_CONFIG`)
- System-Prompt-Tokens werden separat addiert
- Prozentsatz = geschätzte Tokens / `maxContextTokens` × 100

**Warnsystem**: Ab 90% wird die Kontextzeile rot und blinkt (CSS-Animation, Deckkraft 0 → 1, 1-Sekunden-Zyklus) — eine gut sichtbare Warnung, dass das Kontextfenster fast voll ist.

Die Anzeige aktualisiert sich automatisch bei: jeder gesendeten Nachricht, jeder gelöschten Nachricht, jedem Modellwechsel.

### Datei-Karten-Anzeige

Wenn eine Datei hochgeladen oder Zwischenablage-Text angehängt wird, zeigt die Benutzernachricht eine **Datei-Karte** — ein kompaktes visuelles Element ähnlich wie bei Claude oder ChatGPT:

```
┌─────────────────────────────────────┐
│  [PDF]  │  dateiname.pdf            │
│  Icon   │  PDF-Dokument             │
└─────────────────────────────────────┘
```

- Zeigt Dateityp-Badge (PDF, TXT, XLSX usw.) abgeleitet aus der Dateiendung
- Zeigt gekürzten Dateinamen (max. 30 Zeichen mit `...`)
- Gilt für: echte Datei-Uploads über den Upload-Button, als Datei angehängten Zwischenablage-Text (`clipboard.txt`) und alle anderen akzeptierten Formate

---

## Das Hilfsskript `repo2text.sh`

Dieses Bash-Skript wurde speziell entwickelt, um **den gesamten Quellcode eines GitHub-Repositories als einzelne Textdatei zu exportieren** — ideal für die Übergabe des vollständigen Projektkontexts an einen KI-Assistenten.

**Funktionsweise**:
- Klont das Repository mit `git clone --depth 1`.
- Analysiert alle Textdateien (MIME-Typ + `grep -Iq .`) und schreibt sie mit Trennzeichen in eine Ausgabedatei.
- Respektiert explizit `.gitignore` und `.gitattributes`.
- Unterstützt TXT-, JSON- und Markdown-Ausgabeformate.
- Erstellt ein ZIP-Archiv der Exportdatei.
- Enthält Metadaten: Commit-Hash, Branch, Zeitstempel.

**Spezielle Optionen**:
- `--flat`: Nur Dateinamen ohne Pfade verwenden.
- `-o, --only PATH`: Nur ein bestimmtes Unterverzeichnis exportieren.
- `-md5, --md5`: MD5-Prüfsumme für jede Datei berechnen und einschließen.
- Intelligente Erkennung der Remote-URL, wenn das Skript innerhalb eines Git-Repositories ausgeführt wird.
- Sowohl `md5sum` (Linux) als auch `md5` (macOS) werden unterstützt.

**Beispiele**:

```bash
# Einfacher Export (interaktive URL-Abfrage)
./repo2text.sh

# Export mit URL als Markdown
./repo2text.sh -f md https://github.com/debian-professional/private-chatboot.git

# Nur das Verzeichnis 'shell-scipts' mit flacher Struktur exportieren
./repo2text.sh --flat -o shell-scipts https://github.com/debian-professional/private-chatboot.git

# Export mit MD5-Prüfsummen
./repo2text.sh -md5 https://github.com/debian-professional/private-chatboot.git
```

**Warum ist das nützlich?**
- Ermöglicht vollständige Projektdokumentation in einer einzigen Datei.
- Ideal zum Einfügen ganzer Codebasen in KI-Chats.
- Die MD5-Option hilft bei der Überprüfung der Dateiintegrität nach dem Export.

> `repo2text` ist auch als eigenständiges Projekt verfügbar: [github.com/debian-professional/repo2text](https://github.com/debian-professional/repo2text)

---

## Sicherheitsarchitektur im Detail

Sicherheit hatte in diesem Projekt höchste Priorität. Hier sind alle wesentlichen Maßnahmen:

### 1. API-Key — Niemals dem Client zugänglich
- Der Key wird **ausschließlich** in der Apache-Umgebungsvariable `DEEPSEEK_API_KEY` gehalten (gesetzt in `/etc/apache2/envvars`).
- `deepseek-api.py` ruft ihn über `os.environ.get('DEEPSEEK_API_KEY')` ab.
- Der Client kommuniziert nur mit `/cgi-bin/deepseek-api.py` (lokaler Proxy) — niemals direkt mit der DeepSeek API.
- Selbst bei einem XSS-Angriff könnte der Key nicht von der Seite gelesen werden.

### 2. Magic-Byte-Prüfung gegen ausführbare Dateien
- Vor dem Lesen einer hochgeladenen Datei werden die ersten 20 Bytes gegen eine umfassende Signaturdatenbank geprüft (siehe [Datei-Upload mit Sicherheitsprüfung](#datei-upload-mit-sicherheitsprüfung)).
- Bei Übereinstimmung wird der Upload mit einer detaillierten Fehlermeldung blockiert, die die erkannte Plattform und das Format anzeigt.
- Dieser Schutz funktioniert auch wenn bösartige Dateien umbenannt werden (z.B. `virus.exe` → `rechnung.pdf`).

### 3. Sichere Session-Speicherung
- Sessions-Verzeichnis: `/var/www/deepseek-chat/sessions/` — `chmod 700`
- Jede Session-Datei: `chmod 600`
- Das Session-ID-Format wird serverseitig validiert — kein Path-Traversal möglich.

### 4. Logging ohne sensible Daten
- Log enthält: Zeitstempel, IP-Adressen, HTTP-Methoden, Pfade, Status-Codes, Fehlermeldungen.
- **Niemals geloggt**: API-Keys, Session-Inhalte, Nachrichtentext (außer 60-Zeichen-Feedback-Vorschauen).
- OPTIONS-Anfragen werden herausgefiltert, um Log-Überflutung zu verhindern.

### 5. Keine direkte Client-API-Kommunikation
- Alle sicherheitskritischen Operationen erfolgen serverseitig über Python CGI.
- Der Client hat keine Kenntnis von API-Zugangsdaten, Server-Pfaden oder Session-Speicherorten.

### 6. Eingabe-Validierung
- Datei-Formate werden sowohl nach Erweiterung als auch nach Magic Bytes validiert.
- Session-IDs werden serverseitig gegen Regex des erwarteten Formats validiert.
- Zwischenablage-Einfügen wird gefiltert, um Dateipfade zu blockieren, bevor sie die API erreichen.

### 7. Transport-Sicherheit
- HTTPS über Apache SSL-Konfiguration (`deepseek-chat-ssl.conf`) erzwungen.
- HTTP-Konfiguration (`deepseek-chat.conf`) über `a2dissite` deaktiviert.

---

## Deployment & Nutzung

### Voraussetzungen

- Debian-basiertes System (oder beliebiges Linux mit Apache, Python 3, Bash)
- Apache mit CGI-Modul (`a2enmod cgi`) und SSL (`a2enmod ssl`)
- Python 3 mit Paketen: `reportlab`
- Für `repo2text.sh`: `jq`, `pv`, `zip`, `git`
- Ein gültiger DeepSeek API-Key von [platform.deepseek.com](https://platform.deepseek.com)

### Installation

**1. Repository klonen** (als Benutzer `source`):
```bash
git clone https://github.com/debian-professional/private-chatboot.git /home/source/private-chatboot
```

**2. API-Key konfigurieren**:
```bash
# In /etc/apache2/envvars eintragen:
export DEEPSEEK_API_KEY="ihr-deepseek-api-key-hier"
```

**3. Apache-Konfiguration aktivieren**:
```bash
a2ensite deepseek-chat-ssl.conf
a2dissite deepseek-chat.conf   # einfache HTTP-Konfiguration deaktivieren
systemctl restart apache2
```

**4. Erforderliche Verzeichnisse erstellen**:
```bash
mkdir -p /var/www/deepseek-chat/sessions
chown www-data:www-data /var/www/deepseek-chat/sessions
chmod 700 /var/www/deepseek-chat/sessions
```

**5. Deploy-Skript ausführen** (als root):
```bash
./deploy.sh source
```

**6. Hilfsskripte installieren**:
```bash
./install.sh   # als root — kopiert deploy.sh und sync-back.sh ins Produktionsverzeichnis
```

### Konfiguration

**Modell-Konfiguration** (`MODEL_CONFIG` in `index.html`):
```javascript
const MODEL_CONFIG = {
    'deepseek-chat': {
        maxContextTokens:   100000,
        maxOutputTokens:    8192,
        maxContextMessages: 50
    },
    'deepseek-reasoner': {
        maxContextTokens:   65000,
        maxOutputTokens:    32768,
        maxContextMessages: 30
    }
};
```
Um diese Werte zu aktualisieren, wenn DeepSeek neue Modellversionen veröffentlicht, muss nur dieser Block angepasst werden.

**Sprach-Konfiguration** (`language.xml`):
- Einen neuen `<language id="custom" name="..." visible="true">`-Block hinzufügen, um den Custom-Language-Slot zu aktivieren.
- `has_address_form="true"` für Sprachen mit formell/informell-Unterscheidung setzen.

### Deploy-Skripte

| Skript | Funktion |
|--------|----------|
| `deploy.sh <user>` | Kopiert Dateien von `/home/<user>/private-chatboot/var/www/deepseek-chat/` nach `/var/www/deepseek-chat/`, setzt Eigentümerschaft/Berechtigungen, lädt Apache neu |
| `sync-back.sh <user>` | Kopiert geänderte Dateien aus der Produktion zurück ins Source-Repo |
| `install.sh` | Installiert `deploy.sh` und `sync-back.sh` im Produktionsverzeichnis |
| `tag-release.sh` | Erstellt einen neuen Git-Tag mit auto-inkrementierter Versionsnummer (z.B. v0.80 → v0.81) und pusht ihn |

---

## Projektstruktur

```
/
├── etc/apache2/sites-available/
│   ├── deepseek-chat.conf              (deaktiviert — nur HTTP, Redirect auf HTTPS)
│   └── deepseek-chat-ssl.conf          (aktiv — SSL, CGI, API-Key via envvars)
├── shell-scipts/
│   ├── repo2text.sh                    Gesamtes Repo als einzelne Textdatei exportieren
│   ├── deploy.sh                       Kopiert Source-Repo → Produktion
│   ├── sync-back.sh                    Kopiert Produktion → Source-Repo
│   ├── install.sh                      Installiert deploy/sync-back Skripte
│   └── tag-release.sh                  Erstellt und pusht Git-Versions-Tags
├── var/www/deepseek-chat/
│   ├── index.html                      Hauptanwendung (alle JS/CSS/HTML)
│   ├── language.xml                    Alle UI-Texte in allen Sprachen (EN, DE, ES, Custom)
│   ├── manifest                        Design-Manifest (alle Konventionen, ~20KB)
│   ├── changelog                       Vollständige Entwicklungsgeschichte (68+ Einträge, ~44KB)
│   ├── files-directorys                Dateiübersicht / Verzeichnisliste
│   ├── cgi-bin/
│   │   ├── deepseek-api.py            Streaming-Proxy zur DeepSeek API
│   │   ├── deepseek-models.py         Fragt /v1/models Endpunkt ab
│   │   ├── save-session.py            Speichert Chat-Sessions (POST)
│   │   ├── load-session.py            Lädt Session-Liste (GET) oder Session (GET ?id=)
│   │   ├── delete-session.py          Löscht Session (DELETE)
│   │   ├── export-pdf.py              PDF-Export mit ReportLab
│   │   ├── export-markdown.py         Markdown-Export
│   │   ├── export-txt.py              TXT-Export
│   │   ├── export-rtf.py              RTF-Export (keine externe Bibliothek)
│   │   ├── feedback-log.py            Like/Dislike Logging
│   │   ├── get-log.py                 Liest und gibt Log-Datei zurück
│   │   └── deepseek-chat.log          Server-Log-Datei (auto-erstellt)
│   └── sessions/                      Chat-Session JSON-Dateien (auto-erstellt)
```

---

## Modell-Konfiguration

Das `MODEL_CONFIG`-Objekt in `index.html` ist die einzige Wahrheitsquelle für alle modellspezifischen Limits:

```javascript
const MODEL_CONFIG = {
    'deepseek-chat': {
        maxContextTokens:   100000,   // DeepSeek V3 Kontextfenster
        maxOutputTokens:    8192,     // Maximale Tokens pro Antwort
        maxContextMessages: 50        // Maximale Nachrichten als Kontext
    },
    'deepseek-reasoner': {
        maxContextTokens:   65000,    // DeepSeek R1 Kontextfenster
        maxOutputTokens:    32768,    // R1 unterstützt längere Reasoning-Ketten
        maxContextMessages: 30        // Weniger Nachrichten wegen Reasoning-Overhead
    }
};
```

Quelle: [DeepSeek API-Dokumentation](https://api-docs.deepseek.com) (Stand 19.02.2026).

**Token-Schätzung**: `TOKENS_PER_CHAR = 0,25` (4 Zeichen ≈ 1 Token — konservative Schätzung für gemischten Englisch/Deutsch-Text).

Wenn ein neues DeepSeek-Modell veröffentlicht wird, **muss nur dieser `MODEL_CONFIG`-Block aktualisiert werden**. Alle abhängigen Funktionen (`updateContextDisplay()`, `sendMessage()`, `handleRegenerate()`) verwenden automatisch die neuen Werte.

---

## Design-Manifest

Das Projekt enthält eine **`manifest`-Datei**, die alle Design-Entscheidungen und Konventionen dokumentiert. Jede Änderung am Projekt wird dort dokumentiert. Wesentliche Regeln:

- **Alle Buttons**: Nur Pill-Style (border-radius: 20px, height: 36px) — eckige Buttons sind verboten.
- **Button-Farben**: Blau (`#0056b3`) für Aktionen, dunkel/blau Toggle für Modi, Rot (`#dc3545`) für destruktive, Grün (`#28a745`) für konstruktive Aktionen.
- **Einstellungen**: Nur Toggle-Schalter — keine Radio-Buttons, keine Checkboxen.
- **Keine Emojis** in Buttons oder Labels (Ausnahme: das DeepThink-Icon ✦).
- **Kein PHP** — ausschließlich JavaScript und Python.
- **Keine externen JS-Frameworks** — kein Node, kein React, kein Vue.
- **Format-Beibehaltung**: Bestehende Einrückung und Formatierung in `index.html` darf niemals geändert werden.
- Das Manifest ist eine **separate Datei** und darf niemals in `index.html` eingebettet werden.

---

## Bekannte Einschränkungen & technische Hinweise

### "Lost in the Middle" — Eine bekannte KI-Einschränkung
Alle aktuellen Sprachmodelle (einschließlich DeepSeek) neigen dazu, Inhalte am **Anfang und Ende** eines langen Kontexts zuverlässig zu erinnern, aber Inhalte **in der Mitte** werden manchmal übersehen oder halluziniert. (Liu et al., 2023: "Lost in the Middle: How Language Models Use Long Contexts")

**Praktische Auswirkung auf dieses Projekt**:
- Ein Repository-Export von ~270.000 Zeichen ≈ ~67.500 Tokens.
- DeepSeek-Kontextfenster: 100.000 Tokens → ~67% Auslastung → Inhalte in der Mitte können unzuverlässig sein.
- **Empfehlung**: Für spezifische Aufgaben nur die relevanten Dateien einzeln hochladen statt den gesamten Repository-Export.

### GitHub Raw-URL-Caching
Nach einem `git push` ist die neue Version **nicht sofort verfügbar** über `raw.githubusercontent.com`-URLs — GitHub cached diese bis zu 10 Minuten. Das ist normal und kann nicht umgangen werden. Die Dateien sind korrekt auf GitHub gespeichert, sobald `git push` erfolgreich war.

### Nano und Unicode — Kritische Warnung
**Niemals** Dateien mit Unicode-Escape-Sequenzen (wie die Umlaut-Funktionen) mit `nano` oder durch Kopieren/Einfügen in ein Terminal bearbeiten. Nano korrumpiert `\u00e4` zu `M-CM-$`, was für JavaScript unlesbarer Datenmüll ist.

**Der einzig sichere Workflow**:
1. Dateien lokal bearbeiten (VS Code, gedit, kate oder einen anderen geeigneten Editor).
2. `git add` / `git commit` / `git push` vom lokalen Rechner.
3. Auf dem Server: `git pull` (im Source-Repo als Benutzer `source`).
4. Als root: `./deploy.sh source`.

### Linux/X11/Firefox Einfüge-Verhalten
Unter Linux mit X11 und Firefox blockiert `e.preventDefault()` in Paste-Event-Handlern das browser-native Einfügeverhalten für Inhalte aus Dateimanagern nicht zuverlässig. Die hier implementierte Lösung (Einfügen zulassen, Inhalt in `setTimeout(0)` prüfen, löschen wenn Dateipfade erkannt) ist der zuverlässige Workaround für diese plattformspezifische Einschränkung.

---

## Abhängigkeiten

| Komponente | Zweck | Installation |
|-----------|---------|-------------|
| Apache2 | Webserver, CGI-Unterstützung | `apt install apache2` |
| Python 3 | Serverseitige CGI-Skripte | `apt install python3` |
| reportlab | PDF-Export | `pip3 install reportlab` |
| pdf.js 3.11.174 | Clientseitige PDF-Extraktion | Über CDN geladen (automatischer Fallback) |
| jq | JSON-Verarbeitung in `repo2text.sh` | `apt install jq` |
| pv | Fortschrittsanzeige in `repo2text.sh` | `apt install pv` |
| git | Versionsverwaltung | `apt install git` |
| zip | Archiv-Erstellung in `repo2text.sh` | `apt install zip` |

**Keine exotischen Frameworks** — alle Abhängigkeiten sind Standard-Pakete in einer Debian-Umgebung oder werden von etablierten CDNs geladen.

---

## Fazit / Was dieses Projekt auszeichnet

Dieses Projekt demonstriert professionelle Webentwicklung in einem minimalistischen, sicherheitsfokussierten Ansatz:

**Architektur**:
- Saubere Trennung von Client (reines HTML/JS) und Server (Python CGI) ohne Verwischung der Verantwortlichkeiten.
- API-Key niemals exponiert — selbst ein vollständiger XSS-Angriff kann ihn nicht durchsickern lassen.
- Single-File-Client (`index.html`), der vollständig eigenständig und intern hochmodular ist.

**Benutzererfahrung**:
- Streaming-Antworten mit Token-Latenz unter einer Sekunde.
- Einzigartiges flexibles Kontext-Management (beliebige Nachricht + alle nachfolgenden löschen).
- Intelligentes Zwischenablage-Handling für Text, Bilder und Dateipfad-Schutz.
- Mehrsprachige Unterstützung mit Anredeform-Unterscheidung, geladen aus externer XML.

**Engineering**:
- Magic-Byte-Prüfung, die Malware unabhängig von der Dateinamenerweiterung erkennt.
- Umlaut-Platzhalter-System, das eine grundlegende DeepSeek API-Einschränkung löst.
- Zukunftskompatible Modell-Fähigkeiten-Map, bereit für bildunterstützende Modelle.
- Vollständiger Audit-Trail über Git und detaillierten Changelog.

**Werkzeuge**:
- `repo2text.sh` als praktisches Werkzeug für KI-gestützte Entwicklung.
- Deployment-Skripte, die konsistente, berechtigungskorrekte Deployments sicherstellen.
- Versions-Tagging für sauberes Release-Management.

**Für einen professionellen Entwickler** demonstriert dieses Projekt:
- **Sicherheitsbewusstsein** — API-Key-Schutz, Malware-Erkennung, sichere Session-Speicherung.
- **Strukturierte Disziplin** — Manifest, Versions-Tags, strikte Design-Konventionen, dokumentierter Changelog.
- **Problemlösungstiefe** — X11-Einfügeverhalten, Umlaut-Korrumpierung, PDF-Binärausgabe, "Lost in the Middle".
- **Vollständige Dokumentation** — sowohl inline als auch in dedizierten Dateien.

DeepSeek Chat ist ein **Aushängeschild für professionelle Webentwicklung** — ohne unnötigen Overhead, aber mit höchsten Ansprüchen an Sicherheit, Korrektheit und Benutzerfreundlichkeit.

---

*Zuletzt aktualisiert: 28.02.2026*
