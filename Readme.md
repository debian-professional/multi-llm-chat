# DeepSeek Chat – Lokaler, sicherer Chat-Client für die DeepSeek-API

**DeepSeek Chat** ist ein vollständig eigenständiger, lokal gehosteter Chat-Client für die DeepSeek-API. Er wurde mit dem Fokus auf **Sicherheit, Einfachheit und professionelle Bedienbarkeit** entwickelt. Die Architektur kommt ohne exotische Frameworks aus und verwendet nur bewährte Technologien: Apache als Webserver, Python-CGI für die serverseitige Logik, reines HTML/JavaScript/CSS auf der Client-Seite.

Das Besondere:  
- **Einzigartiges Kontextmanagement** – Sie können einzelne Nachrichten mitsamt aller nachfolgenden löschen. Der Chat bleibt konsistent, die Token-Nutzung wird dynamisch aktualisiert.  
- **Maximale Sicherheit** – Der API-Key ist niemals im Client sichtbar, Uploads werden per Magic-Byte-Prüfung gegen ausführbare Dateien abgesichert, Sessions werden mit restriktiven Dateirechten gespeichert.  
- **Keine exotischen Frameworks** – Alles basiert auf Apache, Python, Bash und plain HTML/JS.  
- **Professionelle Export-Funktionen** – PDF, Markdown, TXT, RTF für den gesamten Chat oder einzelne Nachrichten.  
- **Inklusive Werkzeug** – Das Skript `repo2text.sh` exportiert das gesamte Repository als Textdatei, ideal für die Arbeit mit KI-Assistenten (wie diesem hier).

---

## Inhaltsverzeichnis

- [Überblick](#überblick)
- [Architektur](#architektur)
- [Einzigartiges Kontextmanagement](#einzigartiges-kontextmanagement)
- [Features im Detail](#features-im-detail)
  - [Chat-Oberfläche](#chat-oberfläche)
  - [Datei-Upload mit Sicherheitsprüfung](#datei-upload-mit-sicherheitsprüfung)
  - [DeepThink-Modus](#deepthink-modus)
  - [Einstellungen (Toggles statt Radio-Buttons)](#einstellungen-toggles-statt-radio-buttons)
  - [Session-Management](#session-management)
  - [Export-Funktionen](#export-funktionen)
  - [Feedback-Buttons & Logging](#feedback-buttons--logging)
  - [Dynamische Kontext-Anzeige](#dynamische-kontext-anzeige)
- [Das Hilfsskript `repo2text.sh`](#das-hilfsskript-repo2textsh)
- [Sicherheitsarchitektur im Detail](#sicherheitsarchitektur-im-detail)
- [Deployment & Nutzung](#deployment--nutzung)
  - [Voraussetzungen](#voraussetzungen)
  - [Installation](#installation)
  - [Konfiguration](#konfiguration)
  - [Deploy-Scripte](#deploy-scripte)
- [Projektstruktur](#projektstruktur)
- [Abhängigkeiten](#abhängigkeiten)
- [Fazit / Warum dieses Projekt überzeugt](#fazit--warum-dieses-projekt-überzeugt)

---

## Überblick

DeepSeek Chat ist eine **lokale Web-Anwendung**, die über die DeepSeek-API (Modelle `deepseek-chat` und `deepseek-reasoner`) kommuniziert. Entwickelt für eine private Server-Umgebung (Debian), kann sie aber auf jedem System mit Apache und Python 3 betrieben werden.  
Ziel war es, einen **sicheren, erweiterbaren und benutzerfreundlichen** Chat-Client zu schaffen, der ohne Cloud-Abhängigkeiten auskommt und volle Kontrolle über die Daten bietet.

---

## Architektur

Die Architektur ist bewusst einfach gehalten, aber durchdacht:

1. **Client**  
   - Reines HTML/JavaScript/CSS, serviert über Apache.  
   - Keine Build-Tools, kein Node.js, keine externen Bibliotheken (außer PDF.js für die PDF-Extraktion).  
   - Die gesamte Logik (Nachrichtenaufbereitung, UI-Updates, Streaming-Empfang) ist in einer einzigen `index.html` gekapselt.

2. **Server**  
   - **Apache** mit CGI-Unterstützung.  
   - **Python-CGI-Skripte** unter `/cgi-bin/` übernehmen:
     - Kommunikation mit der DeepSeek-API (`deepseek-api.py`)
     - Session-Speicherung und -Abruf (`save-session.py`, `load-session.py`, `delete-session.py`)
     - Exporte in verschiedene Formate (`export-*.py`)
     - Feedback-Logging (`feedback-log.py`)
     - Log-Anzeige (`get-log.py`)
   - Der **API-Key** wird ausschließlich über eine Apache-Umgebungsvariable (`DEEPSEEK_API_KEY` in `/etc/apache2/envvars`) bereitgestellt – **niemals im Client-Code**.

3. **Datenhaltung**  
   - **Sessions** werden als JSON-Dateien in `/var/www/deepseek-chat/sessions/` mit `chmod 700` gespeichert.  
   - **Logs** werden in `/var/www/deepseek-chat/cgi-bin/deepseek-chat.log` geschrieben (ohne API-Key).  
   - **Einstellungen** verbleiben lokal im Browser (`localStorage`).

4. **Hilfsskripte**  
   - `deploy.sh`, `sync-back.sh`, `install.sh`, `tag-release.sh` erleichtern das Deployment zwischen Entwicklungs- und Produktionsverzeichnis.  
   - `repo2text.sh` exportiert das gesamte Repository als Textdatei für KI-Assistenten.

---

## Einzigartiges Kontextmanagement

Eine der herausragenden Funktionen ist die Möglichkeit, **einzelne Nachrichten mitsamt aller nachfolgenden zu löschen**. Dies geht weit über das übliche "Letzte Nachricht löschen" hinaus und erlaubt eine flexible Korrektur des Gesprächsverlaufs.

**Implementierung**:
- Jede Nachricht (User & AI) erhält eine eindeutige `id` und wird in einem Array `contextHistory.messages` gespeichert.
- Die Funktion `deleteMessage(msgId)` ermittelt den Index der Nachricht, schneidet das Array ab `index` ab und löscht im DOM alle folgenden Elemente.
- Die Token-Schätzung (`updateContextEstimation()`) wird sofort aktualisiert, ebenso die prozentuale Kontextauslastung.
- Anschließend wird die geänderte Session automatisch gespeichert (`saveSession()`).

**Warum einzigartig?**  
Viele Chat-Clients erlauben nur das Löschen der letzten Nachricht oder gar keine Manipulation des Verlaufs. Hier kann der Benutzer **jede beliebige Stelle im Gespräch als neuen Ausgangspunkt** definieren – perfekt für Testzwecke, Korrekturen oder um das Kontextfenster zu bereinigen, ohne den gesamten Chat zu verlieren.

---

## Features im Detail

### Chat-Oberfläche

- **Dark Mode** (fest, keine Option) – augenschonend, professionell.
- **Server-Header** zeigt Server-Name, IP und dynamische Kontextauslastung (mit Warnung ab 90%).
- **Nachrichtencontainer** mit Hover-Buttons (siehe unten).
- **Textarea** wächst bei Fokus von 40px auf 120px – Enter sendet, Shift+Enter erzeugt neue Zeile.

### Datei-Upload mit Sicherheitsprüfung

- Unterstützte Formate: `.txt`, `.pdf`, `.doc`, `.docx`, `.jpg`, `.png`, `.csv`, `.xlsx`, `.pptx`.  
- **Magic-Byte-Prüfung** (erste 20 Bytes) erkennt ausführbare Dateien (EXE, ELF, Mach-O, Shell-Skripte, Python-Bytecode) und blockiert den Upload – auch wenn die Datei umbenannt wurde.
- PDF-Extraktion mit PDF.js (Fallback über mehrere CDNs), Zeichenbegrenzung auf 50.000 Zeichen, Fortschrittsanzeige.
- Textdateien werden direkt gelesen und ebenfalls auf 50k Zeichen gekürzt.

### DeepThink-Modus

- Umschaltbar über einen dedizierten Button (Pill-Style).  
- Im DeepThink-Modus wird das Modell `deepseek-reasoner` verwendet (echtes Reasoning).  
- Die Konfiguration für Token-Limits (`MODEL_CONFIG`) ist zentral hinterlegt und kann leicht erweitert werden.

### Einstellungen (Toggles statt Radio-Buttons)

- **Anredeform** (Sie/Du) und **Standard-Modus** (Chat/DeepThink) werden über **Toggle-Switches** gesteuert.  
- Die Toggles verhalten sich wie Radio-Buttons: Aktivieren eines deaktiviert automatisch das andere.  
- **Datenschutz-Toggle** "Daten nicht für Training verwenden" setzt den Header `X-No-Training: true`.  
- Alle Einstellungen werden in `localStorage` mit Versionskontrolle (`SETTINGS_VERSION`) gespeichert.

### Session-Management

- Jede Chat-Session erhält eine eindeutige ID im Format `YYYY-MM-DD_HHMMSS_zufall`.  
- **Automatisches Speichern** nach jeder Nachricht (User + AI).  
- **Modal "Chat-Verlauf laden"** zeigt alle gespeicherten Sessions mit Vorschau und Nachrichtenanzahl.  
- Sessions können einzeln geladen oder gelöscht werden. Beim Laden wird der aktuelle Chat automatisch gespeichert.

### Export-Funktionen

- **Globales Export-Dropdown** (neben Senden): PDF, Markdown, TXT, RTF, Chat-Verlauf laden.  
- **Einzelexport** pro Nachricht: Hover-Button "Exportieren" öffnet ein Dropdown mit TXT, Markdown, RTF, PDF.  
  - TXT, Markdown, RTF werden **clientseitig** als Blob generiert (kein Server-Roundtrip).  
  - PDF wird serverseitig mit ReportLab erstellt (professionelles Layout mit Statistiken, Inhaltsverzeichnis, farbigen Nachrichten).  
- Die Exporte enthalten Metadaten (Server, Datum, Einstellungen) und Statistiken (Nachrichtenzahl, Modi, Token, Dateien).

### Feedback-Buttons & Logging

- Bei jeder KI-Antwort erscheinen beim Hover vier Buttons:  
  - **Kopieren** (mit "Kopiert!"-Rückmeldung)  
  - **Mag ich** / **Mag ich gar nicht** (loggen LIKE/DISLIKE in `deepseek-chat.log`, exklusiv)  
  - **Regenerieren** (löscht die alte Antwort und generiert eine neue)  
- Das serverseitige Logging erfasst neben Feedback auch alle API-Zugriffe (IP, Methode, Pfad, Status) – **ohne API-Key**.

### Dynamische Kontext-Anzeige

- Unter der Server-IP wird die aktuelle Kontextauslastung in Prozent angezeigt, z.B. `Kontext: 45% (deepseek-chat)`.  
- Ab 90% wird der Text rot und blinkt – so wird der Benutzer rechtzeitig gewarnt, bevor das Token-Limit erreicht wird.  
- Die Anzeige aktualisiert sich bei jeder Nachricht, jedem Löschvorgang und jedem Modellwechsel.

---

## Das Hilfsskript `repo2text.sh`

Dieses Bash-Skript wurde speziell entwickelt, um **den gesamten Quelltext eines GitHub-Repositories als eine einzige Textdatei zu exportieren** – ideal, um einer KI (wie ChatGPT) den kompletten Projektkontext zu übergeben.

**Funktionsweise**:
- Klont das Repository mit `git clone --depth 1`.  
- Analysiert alle Textdateien (MIME-Typ + `grep -Iq .`) und schreibt sie mit Trennern in eine Ausgabedatei (TXT, JSON oder Markdown).  
- Beachtet `.gitignore`- und `.gitattributes`-Dateien explizit.  
- Erstellt zusätzlich ein ZIP-Archiv der Exportdatei.

**Besondere Optionen**:
- `--flat`: Nur Dateinamen ohne Pfad im Export verwenden.  
- `-o, --only PATH`: Nur einen bestimmten Unterpfad exportieren.  
- `-md5, --md5`: Für jede Datei die MD5-Prüfsumme berechnen und ausgeben.  
- Intelligente Erkennung der Remote-URL, wenn das Skript in einem Git-Repo ausgeführt wird.

**Beispiele**:

```bash
# Einfacher Export des Repos (interaktive URL-Abfrage)
./repo2text.sh

# Export mit Angabe der URL und als Markdown
./repo2text.sh -f md https://github.com/debian-professional/private-chatboot.git

# Nur das Verzeichnis 'shell-scipts' exportieren, mit flacher Struktur
./repo2text.sh --flat -o shell-scipts https://github.com/debian-professional/private-chatboot.git

# Export mit MD5-Prüfsummen für jede Datei
./repo2text.sh -md5 https://github.com/debian-professional/private-chatboot.git
```

**Warum ist das nützlich?**  
- Ermöglicht die vollständige Dokumentation des Projekts in einer einzigen Datei.  
- Perfekt, um den gesamten Code in KI-Chats einzufügen oder für Archivierungszwecke.  
- Die MD5-Option hilft, die Integrität der Dateien nach einem Export zu prüfen.

---

## Sicherheitsarchitektur im Detail

Sicherheit stand bei diesem Projekt an erster Stelle. Hier die wichtigsten Maßnahmen:

1. **API-Key unsichtbar**  
   - Der Key wird **ausschließlich** in der Apache-Umgebungsvariable `DEEPSEEK_API_KEY` (in `/etc/apache2/envvars`) gehalten.  
   - Das CGI-Skript `deepseek-api.py` holt ihn über `os.environ.get('DEEPSEEK_API_KEY')`.  
   - **Der Client hat niemals Zugriff** – selbst bei einem XSS-Angriff könnte der Key nicht ausgelesen werden.

2. **Magic-Byte-Prüfung gegen ausführbare Dateien**  
   - Vor dem Einlesen einer hochgeladenen Datei werden die ersten 20 Bytes auf typische Signaturen ausführbarer Formate geprüft (PE, ELF, Mach-O, Shebang, Python-Bytecode).  
   - Wird eine solche Signatur entdeckt, wird der Upload **blockiert** – auch wenn die Datei z.B. `bild.jpg` heißt, aber tatsächlich eine EXE ist.  
   - Die Signaturliste ist erweiterbar und deckt Windows, Linux, macOS, ARM und Skripte ab.

3. **Sichere Session-Speicherung**  
   - Sessions liegen in `/var/www/deepseek-chat/sessions/`.  
   - Das Verzeichnis wird mit `chmod 700` angelegt (nur der Webserver-Benutzer hat Zugriff).  
   - Jede Session-Datei erhält `chmod 600`.  
   - Die Session-ID wird clientseitig generiert, aber vom Server validiert (Format `YYYY-MM-DD_HHMMSS_zufall`).

4. **Logging ohne sensitive Daten**  
   - Das Log enthält Zeitstempel, IP, Methode, Pfad, HTTP-Status und ggf. Fehlermeldungen – **niemals API-Keys oder Session-Inhalte**.  
   - OPTIONS-Requests werden ignoriert, um das Log nicht zu überfluten.

5. **Trennung von Client und Server**  
   - Alle sicherheitskritischen Operationen (API-Aufruf, Session-Schreibzugriffe) finden serverseitig statt.  
   - Der Client kommuniziert ausschließlich über wohldefinierte CGI-Endpunkte.

6. **Keine externen Abhängigkeiten mit Sicherheitslücken**  
   - Bis auf PDF.js (CDN) und ReportLab (serverseitig) werden keine fremden Bibliotheken eingebunden.  
   - PDF.js hat Fallback-Mechanismen; ReportLab wird nur für den PDF-Export genutzt und ist gut gewartet.

---

## Deployment & Nutzung

### Voraussetzungen

- Debian-basiertes System (oder ein anderes Linux mit Apache, Python 3, Bash)  
- Apache mit CGI-Modul (`a2enmod cgi`)  
- Python 3 und benötigte Pakete: `reportlab`, `jq`, `pv` (für repo2text.sh)  
- Git (für das Klonen und die Hilfsskripte)

### Installation

1. **Repository klonen** (z.B. als Benutzer `source`):

   ```bash
   git clone https://github.com/debian-professional/private-chatboot.git /home/source/private-chatboot
   ```

2. **Apache konfigurieren**  
   - Aktivieren Sie die SSL-Konfiguration (Beispiel in `etc/apache2/sites-available/deepseek-chat-ssl.conf`).  
   - Tragen Sie den API-Key in `/etc/apache2/envvars` ein:  
     `export DEEPSEEK_API_KEY="Ihr-DeepSeek-API-Key"`  
   - Aktivieren Sie die Seite und starten Sie Apache neu.

3. **Verzeichnisse anlegen**  
   ```bash
   mkdir -p /var/www/deepseek-chat/sessions
   chown www-data:www-data /var/www/deepseek-chat/sessions
   chmod 700 /var/www/deepseek-chat/sessions
   ```

4. **Deploy-Skript ausführen**  
   Als `root` (oder mit sudo) führen Sie `deploy.sh <benutzername>` aus, um die aktuellen Dateien aus dem Quell-Repo ins Produktionsverzeichnis zu kopieren und Apache neu zu laden.  
   Beispiel:  
   ```bash
   sudo /var/www/deepseek-chat/deploy.sh source
   ```

5. **Hilfsskripte installieren**  
   `install.sh` (als root) kopiert `deploy.sh` und `sync-back.sh` ins Produktionsverzeichnis.

### Konfiguration

- Die Datei `manifest` enthält **alle Design-Entscheidungen und Konventionen**. Jede Änderung am Projekt muss dort dokumentiert werden – das gewährleistet Konsistenz und Nachvollziehbarkeit.  
- Die Apache-Konfiguration ist bereits optimiert (keine einzelnen ScriptAlias-Einträge nötig, nur ein generischer `/cgi-bin/`-Alias).  
- Die Model-Konfiguration (`MODEL_CONFIG` in `index.html`) kann leicht erweitert werden, wenn neue Modelle hinzukommen.

### Deploy-Scripte

- **`deploy.sh <user>`** – Kopiert Dateien aus `/home/<user>/private-chatboot/var/www/deepseek-chat/` nach `/var/www/deepseek-chat/`, setzt Besitzer und Rechte und lädt Apache neu.  
- **`sync-back.sh <user>`** – Kopiert geänderte Dateien aus der Produktion zurück ins Quell-Repo (z.B. nach manuellen Änderungen).  
- **`install.sh`** – Installiert die beiden Scripte im Produktionsverzeichnis.  
- **`tag-release.sh`** – Erstellt einen neuen Git-Tag mit automatisch inkrementierter Versionsnummer (z.B. v0.80 → v0.81) und pusht ihn.

---

## Projektstruktur (Auszug)

```
/
├── etc/apache2/sites-available/
│   ├── deepseek-chat.conf              (deaktiviert, nur HTTP->HTTPS)
│   └── deepseek-chat-ssl.conf          (aktiv, mit CGI und envvars)
├── shell-scipts/
│   ├── repo2text.sh                     # Export-Tool für das Repo
│   ├── deploy.sh                        # Kopiert source → Produktion
│   ├── sync-back.sh                     # Kopiert Produktion → source
│   ├── install.sh                       # Installiert deploy/sync-back
│   └── tag-release.sh                   # Erstellt Git-Tags
├── var/www/deepseek-chat/
│   ├── index.html                       # Hauptanwendung (JS/CSS/HTML)
│   ├── manifest                         # Design-Manifest
│   ├── files-directorys                 # Übersicht aller Dateien
│   ├── cgi-bin/
│   │   ├── deepseek-api.py              # Proxy zur DeepSeek-API
│   │   ├── save-session.py              # Speichert Chat-Sessions
│   │   ├── load-session.py              # Lädt Sessions / Liste
│   │   ├── delete-session.py            # Löscht Session
│   │   ├── export-pdf.py                # PDF-Export
│   │   ├── export-markdown.py           # Markdown-Export
│   │   ├── export-txt.py                # TXT-Export
│   │   ├── export-rtf.py                # RTF-Export
│   │   ├── feedback-log.py              # Feedback-Logging
│   │   ├── get-log.py                   # Log-Datei auslesen
│   │   └── deepseek-chat.log            # Log-Datei (wächst)
│   └── sessions/                        # JSON-Session-Dateien
├── LICENSE
└── .gitignore
```

---

## Abhängigkeiten

| Komponente          | Zweck                                                       | Installationshinweis                          |
|---------------------|-------------------------------------------------------------|-----------------------------------------------|
| Apache2             | Webserver, CGI-Unterstützung                                | `apt install apache2`                         |
| Python3             | Serverseitige Skripte                                       | `apt install python3`                          |
| reportlab           | PDF-Export                                                  | `pip3 install reportlab`                       |
| jq                  | JSON-Verarbeitung in `repo2text.sh`                         | `apt install jq`                               |
| pv                  | Fortschrittsanzeige in `repo2text.sh`                       | `apt install pv`                               |
| git                 | Klonen und Versionsverwaltung                               | `apt install git`                              |
| zip                 | Archivierung der Export-Datei in `repo2text.sh`             | `apt install zip`                              |
| pdf.js (CDN)        | Client-seitige PDF-Extraktion                               | Wird über CDN geladen (Fallback)               |

**Keine weiteren exotischen Frameworks** – alles ist Standard in einer Debian-Umgebung.

---

## Fazit / Warum dieses Projekt überzeugt

Dieses Projekt demonstriert auf professionellem Niveau:

- **Saubere, sichere Architektur** – API-Key-Schutz, Magic-Byte-Prüfung, Session-Sicherheit, Trennung von Client und Server.  
- **Durchdachte Benutzerführung** – intuitives Löschen von Nachrichten inkl. Folgekontext, dynamische Kontextwarnung, Hover-Buttons, Toggle-Switches.  
- **Erweiterbarkeit** – zentrale Konfiguration für Modelle, modulare CGI-Skripte, dokumentiertes Manifest.  
- **Praktische Werkzeuge** – `repo2text.sh` erleichtert die Arbeit mit KI-Assistenten enorm.  
- **Minimalismus** – Kein Node, kein React, kein Docker – läuft auf jedem Apache-Server.

Für einen **professionellen Entwickler** zeigt dieses Projekt:
- **Sicherheitsbewusstsein** (Umgang mit API-Keys, Schutz vor Malware-Uploads).  
- **Strukturiertes Arbeiten** (Manifest, Versions-Tags, Deployment-Skripte).  
- **Innovative Features** (Kontextmanagement, Streaming-Responses).  
- **Vollständige Dokumentation** – sowohl im Code als auch in dieser README.

DeepSeek Chat ist ein **Showcase für professionelle Webentwicklung** – ohne überflüssigen Ballast, aber mit höchstem Anspruch an Sicherheit und Benutzerfreundlichkeit.

---

**Hinweis:** Alle Änderungen an diesem Projekt müssen im `manifest` dokumentiert werden. Diese Datei ist die zentrale Quelle für Design-Entscheidungen und Konventionen und darf niemals gelöscht oder unvollständig sein.

---


