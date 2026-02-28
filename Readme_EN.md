# DeepSeek Chat – A Private, Secure Chat Client for the DeepSeek API

**DeepSeek Chat** is a fully self-contained, locally hosted chat client for the DeepSeek API. It was developed with a focus on **security, simplicity, and professional usability**. The architecture requires no exotic frameworks and uses only proven technologies: Apache as the web server, Python CGI for server-side logic, and plain HTML/JavaScript/CSS on the client side.

Key highlights:
- **Unique context management** – Delete individual messages along with all subsequent ones. The chat remains consistent and token usage is dynamically updated.
- **Maximum security** – The API key is never visible on the client side, uploads are protected against executable files via magic byte inspection, and sessions are stored with restrictive file permissions.
- **No exotic frameworks** – Everything is based on Apache, Python, Bash, and plain HTML/JS.
- **Professional export functions** – PDF, Markdown, TXT, RTF for the entire chat or individual messages.
- **Included tool** – The `repo2text.sh` script exports the entire repository as a text file, ideal for working with AI assistants (like this one).

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Unique Context Management](#unique-context-management)
- [Features in Detail](#features-in-detail)
  - [Chat Interface](#chat-interface)
  - [File Upload with Security Check](#file-upload-with-security-check)
  - [DeepThink Mode](#deepthink-mode)
  - [Settings (Toggles instead of Radio Buttons)](#settings-toggles-instead-of-radio-buttons)
  - [Session Management](#session-management)
  - [Export Functions](#export-functions)
  - [Feedback Buttons & Logging](#feedback-buttons--logging)
  - [Dynamic Context Display](#dynamic-context-display)
- [The Helper Script `repo2text.sh`](#the-helper-script-repo2textsh)
- [Security Architecture in Detail](#security-architecture-in-detail)
- [Deployment & Usage](#deployment--usage)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Deploy Scripts](#deploy-scripts)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Conclusion / Why This Project Stands Out](#conclusion--why-this-project-stands-out)

---

## Overview

DeepSeek Chat is a **local web application** that communicates via the DeepSeek API (models `deepseek-chat` and `deepseek-reasoner`). Developed for a private server environment (Debian), it can run on any system with Apache and Python 3. The goal was to create a **secure, extensible, and user-friendly** chat client that operates without cloud dependencies and offers full control over data.

---

## Architecture

The architecture is intentionally simple but well thought out:

1. **Client**
   - Pure HTML/JavaScript/CSS, served via Apache.
   - No build tools, no Node.js, no external libraries (except PDF.js for PDF extraction).
   - The entire logic (message processing, UI updates, streaming reception) is encapsulated in a single `index.html`.

2. **Server**
   - **Apache** with CGI support.
   - **Python CGI scripts** under `/cgi-bin/` handle:
     - Communication with the DeepSeek API (`deepseek-api.py`)
     - Session storage and retrieval (`save-session.py`, `load-session.py`, `delete-session.py`)
     - Exports in various formats (`export-*.py`)
     - Feedback logging (`feedback-log.py`)
     - Log display (`get-log.py`)
   - The **API key** is provided exclusively via an Apache environment variable (`DEEPSEEK_API_KEY` in `/etc/apache2/envvars`) — **never in client code**.

3. **Data Storage**
   - **Sessions** are stored as JSON files in `/var/www/deepseek-chat/sessions/` with `chmod 700`.
   - **Logs** are written to `/var/www/deepseek-chat/cgi-bin/deepseek-chat.log` (without API key).
   - **Settings** remain locally in the browser (`localStorage`).

4. **Helper Scripts**
   - `deploy.sh`, `sync-back.sh`, `install.sh`, `tag-release.sh` facilitate deployment between development and production directories.
   - `repo2text.sh` exports the entire repository as a text file for AI assistants.

---

## Unique Context Management

One of the standout features is the ability to **delete individual messages along with all subsequent ones**. This goes far beyond the typical "delete last message" and allows flexible correction of the conversation history.

**Implementation**:
- Each message (user & AI) receives a unique `id` and is stored in an array `contextHistory.messages`.
- The `deleteMessage(msgId)` function determines the index of the message, truncates the array from `index` onwards, and removes all following elements from the DOM.
- The token estimate (`updateContextEstimation()`) is immediately updated, as is the percentage context utilization.
- The modified session is then automatically saved (`saveSession()`).

**Why is this unique?**
Many chat clients only allow deletion of the last message or no history manipulation at all. Here, the user can **define any point in the conversation as a new starting point** — perfect for testing, corrections, or cleaning up the context window without losing the entire chat.

---

## Features in Detail

### Chat Interface

- **Dark Mode** (fixed, no option) — easy on the eyes, professional.
- **Server header** shows server name, IP, and dynamic context utilization (with warning above 90%).
- **Message container** with hover buttons (see below).
- **Textarea** expands on focus from 40px to 120px — Enter sends, Shift+Enter creates a new line.

### File Upload with Security Check

- Supported formats: `.txt`, `.pdf`, `.doc`, `.docx`, `.jpg`, `.png`, `.csv`, `.xlsx`, `.pptx`.
- **Magic byte inspection** (first 20 bytes) detects executable files (EXE, ELF, Mach-O, shell scripts, Python bytecode) and blocks the upload — even if the file has been renamed.
- PDF extraction with PDF.js (fallback across multiple CDNs), character limit of 50,000 characters, progress display.
- Text files are read directly and also truncated to 50k characters.

### DeepThink Mode

- Switchable via a dedicated button (pill style).
- In DeepThink mode, the `deepseek-reasoner` model is used (real reasoning).
- The configuration for token limits (`MODEL_CONFIG`) is centrally stored and can be easily extended.

### Settings (Toggles instead of Radio Buttons)

- **Form of address** (formal/informal) and **default mode** (Chat/DeepThink) are controlled via **toggle switches**.
- The toggles behave like radio buttons: activating one automatically deactivates the other.
- **Privacy toggle** "Do not use data for training" sets the header `X-No-Training: true`.
- All settings are stored in `localStorage` with version control (`SETTINGS_VERSION`).

### Session Management

- Each chat session receives a unique ID in the format `YYYY-MM-DD_HHMMSS_random`.
- **Automatic saving** after each message (user + AI).
- **"Load chat history" modal** shows all saved sessions with preview and message count.
- Sessions can be individually loaded or deleted. When loading, the current chat is automatically saved.

### Export Functions

- **Global export dropdown** (next to send): PDF, Markdown, TXT, RTF, load chat history.
- **Individual export** per message: hover button "Export" opens a dropdown with TXT, Markdown, RTF, PDF.
  - TXT, Markdown, RTF are generated **client-side** as blobs (no server roundtrip).
  - PDF is created server-side with ReportLab (professional layout with statistics, table of contents, colored messages).
- Exports contain metadata (server, date, settings) and statistics (message count, modes, tokens, files).

### Feedback Buttons & Logging

- On hover, four buttons appear for each AI response:
  - **Copy** (with "Copied!" feedback)
  - **Like** / **Dislike** (log LIKE/DISLIKE in `deepseek-chat.log`, exclusive)
  - **Regenerate** (deletes the old response and generates a new one)
- Server-side logging captures feedback as well as all API accesses (IP, method, path, status) — **never API keys or session contents**.

### Dynamic Context Display

- Below the server IP, current context utilization is shown as a percentage, e.g. `Context: 45% (deepseek-chat)`.
- Above 90%, the text turns red and blinks — warning the user before the token limit is reached.
- The display updates with every message, every deletion, and every model switch.

---

## The Helper Script `repo2text.sh`

This Bash script was specifically developed to **export the entire source code of a GitHub repository as a single text file** — ideal for passing the complete project context to an AI assistant like ChatGPT.

**How it works**:
- Clones the repository with `git clone --depth 1`.
- Analyzes all text files (MIME type + `grep -Iq .`) and writes them with separators into an output file (TXT, JSON or Markdown).
- Explicitly respects `.gitignore` and `.gitattributes` files.
- Creates a ZIP archive of the export file.

**Special options**:
- `--flat`: Use only filenames without paths in the export.
- `-o, --only PATH`: Export only a specific subdirectory.
- `-md5, --md5`: Compute and include the MD5 checksum for each file.
- Intelligent detection of the remote URL when the script is run inside a Git repository.

**Examples**:

```bash
# Simple export of the repo (interactive URL prompt)
./repo2text.sh

# Export with URL and as Markdown
./repo2text.sh -f md https://github.com/debian-professional/private-chatboot.git

# Export only the 'shell-scipts' directory with flat structure
./repo2text.sh --flat -o shell-scipts https://github.com/debian-professional/private-chatboot.git

# Export with MD5 checksums for each file
./repo2text.sh -md5 https://github.com/debian-professional/private-chatboot.git
```

**Why is this useful?**
- Enables complete documentation of the project in a single file.
- Perfect for inserting the entire code into AI chats or for archiving purposes.
- The MD5 option helps verify file integrity after an export.

> `repo2text` is also available as a standalone project: [github.com/debian-professional/repo2text](https://github.com/debian-professional/repo2text)

---

## Security Architecture in Detail

Security was the top priority in this project. Here are the key measures:

1. **API key invisible**
   - The key is held **exclusively** in the Apache environment variable `DEEPSEEK_API_KEY` (in `/etc/apache2/envvars`).
   - The CGI script `deepseek-api.py` retrieves it via `os.environ.get('DEEPSEEK_API_KEY')`.
   - **The client never has access** — even in the event of an XSS attack, the key could not be read.

2. **Magic byte inspection against executable files**
   - Before reading an uploaded file, the first 20 bytes are checked for typical signatures of executable formats (PE, ELF, Mach-O, shebang, Python bytecode).
   - If such a signature is detected, the upload is **blocked** — even if the file is named `image.jpg` but is actually an EXE.
   - The signature list is extensible and covers Windows, Linux, macOS, ARM, and scripts.

3. **Secure session storage**
   - Sessions are located in `/var/www/deepseek-chat/sessions/`.
   - The directory is created with `chmod 700` (only the web server user has access).
   - Each session file receives `chmod 600`.
   - The session ID is generated client-side but validated by the server (format `YYYY-MM-DD_HHMMSS_random`).

4. **Logging without sensitive data**
   - The log contains timestamps, IP, method, path, HTTP status and any error messages — **never API keys or session contents**.
   - OPTIONS requests are ignored to prevent log flooding.

5. **Separation of client and server**
   - All security-critical operations (API calls, session write access) take place server-side.
   - The client communicates exclusively via well-defined CGI endpoints.

6. **No external dependencies with security vulnerabilities**
   - Apart from PDF.js (CDN) and ReportLab (server-side), no third-party libraries are included.
   - PDF.js has fallback mechanisms; ReportLab is only used for PDF export and is well maintained.

---

## Deployment & Usage

### Prerequisites

- Debian-based system (or any other Linux with Apache, Python 3, Bash)
- Apache with CGI module (`a2enmod cgi`)
- Python 3 and required packages: `reportlab`, `jq`, `pv` (for repo2text.sh)
- Git (for cloning and helper scripts)

### Installation

1. **Clone the repository** (e.g. as user `source`):

   ```bash
   git clone https://github.com/debian-professional/private-chatboot.git /home/source/private-chatboot
   ```

2. **Configure Apache**
   - Enable the SSL configuration (example in `etc/apache2/sites-available/deepseek-chat-ssl.conf`).
   - Enter the API key in `/etc/apache2/envvars`:
     `export DEEPSEEK_API_KEY="your-deepseek-api-key"`
   - Enable the site and restart Apache.

3. **Create directories**
   ```bash
   mkdir -p /var/www/deepseek-chat/sessions
   chown www-data:www-data /var/www/deepseek-chat/sessions
   chmod 700 /var/www/deepseek-chat/sessions
   ```

4. **Run deploy script**
   As `root` (or with sudo), run `deploy.sh <username>` to copy the current files from the source repo to the production directory and reload Apache.
   Example:
   ```bash
   sudo /var/www/deepseek-chat/deploy.sh source
   ```

5. **Install helper scripts**
   `install.sh` (as root) copies `deploy.sh` and `sync-back.sh` to the production directory.

### Configuration

- The `manifest` file contains **all design decisions and conventions**. Every change to the project must be documented there — this ensures consistency and traceability.
- The Apache configuration is already optimized (no individual ScriptAlias entries needed, just a generic `/cgi-bin/` alias).
- The model configuration (`MODEL_CONFIG` in `index.html`) can be easily extended when new models are added.

### Deploy Scripts

- **`deploy.sh <user>`** — Copies files from `/home/<user>/private-chatboot/var/www/deepseek-chat/` to `/var/www/deepseek-chat/`, sets ownership and permissions, and reloads Apache.
- **`sync-back.sh <user>`** — Copies changed files from production back to the source repo (e.g. after manual changes).
- **`install.sh`** — Installs the two scripts in the production directory.
- **`tag-release.sh`** — Creates a new Git tag with automatically incremented version number (e.g. v0.80 → v0.81) and pushes it.

---

## Project Structure (Excerpt)

```
/
├── etc/apache2/sites-available/
│   ├── deepseek-chat.conf              (disabled, HTTP->HTTPS only)
│   └── deepseek-chat-ssl.conf          (active, with CGI and envvars)
├── shell-scipts/
│   ├── repo2text.sh                     # Export tool for the repo
│   ├── deploy.sh                        # Copies source → production
│   ├── sync-back.sh                     # Copies production → source
│   ├── install.sh                       # Installs deploy/sync-back
│   └── tag-release.sh                   # Creates Git tags
├── var/www/deepseek-chat/
│   ├── index.html                       # Main application (JS/CSS/HTML)
│   ├── manifest                         # Design manifest
│   ├── files-directorys                 # File overview
│   ├── cgi-bin/
│   │   ├── deepseek-api.py              # Proxy to DeepSeek API
│   │   ├── save-session.py              # Saves chat sessions
│   │   ├── load-session.py              # Loads sessions / list
│   │   ├── delete-session.py            # Deletes session
│   │   ├── export-pdf.py                # PDF export
│   │   ├── export-markdown.py           # Markdown export
│   │   ├── export-txt.py                # TXT export
│   │   ├── export-rtf.py                # RTF export
│   │   ├── feedback-log.py              # Feedback logging
│   │   ├── get-log.py                   # Read log file
│   │   └── deepseek-chat.log            # Log file (grows)
│   └── sessions/                        # JSON session files
├── LICENSE
└── .gitignore
```

---

## Dependencies

| Component | Purpose | Installation |
|-----------|---------|-------------|
| Apache2 | Web server, CGI support | `apt install apache2` |
| Python3 | Server-side scripts | `apt install python3` |
| reportlab | PDF export | `pip3 install reportlab` |
| jq | JSON processing in `repo2text.sh` | `apt install jq` |
| pv | Progress display in `repo2text.sh` | `apt install pv` |
| git | Cloning and version management | `apt install git` |
| zip | Archiving export file in `repo2text.sh` | `apt install zip` |
| pdf.js (CDN) | Client-side PDF extraction | Loaded via CDN (fallback) |

**No exotic frameworks** — everything is standard in a Debian environment.

---

## Conclusion / Why This Project Stands Out

This project demonstrates professional-level development:

- **Clean, secure architecture** — API key protection, magic byte inspection, session security, separation of client and server.
- **Thoughtful user experience** — intuitive deletion of messages including follow-up context, dynamic context warning, hover buttons, toggle switches.
- **Extensibility** — central model configuration, modular CGI scripts, documented manifest.
- **Practical tools** — `repo2text.sh` greatly simplifies working with AI assistants.
- **Minimalism** — No Node, no React, no Docker — runs on any Apache server.

For a **professional developer**, this project demonstrates:
- **Security awareness** (handling API keys, protection against malware uploads).
- **Structured working** (manifest, version tags, deployment scripts).
- **Innovative features** (context management, streaming responses).
- **Complete documentation** — both in the code and in this README.

DeepSeek Chat is a **showcase for professional web development** — without unnecessary overhead, but with the highest standards for security and user-friendliness.

---

**Note:** All changes to this project must be documented in the `manifest`. This file is the central source for design decisions and conventions and must never be deleted or left incomplete.
