# Multi-LLM Chat Client – OpenAI, DeepSeek, Google Gemini, Hugging Face & GroqCloud

**Multi-LLM Chat Client** is a fully self-contained, locally hosted chat client supporting five AI providers: OpenAI, DeepSeek, Google Gemini, Hugging Face, and GroqCloud. Developed with a focus on **security, simplicity, and professional usability**, the architecture requires no exotic frameworks and relies exclusively on proven technologies: Apache as the web server, Python CGI for server-side logic, and plain HTML/JavaScript/CSS on the client side.

Key highlights:
- **Multi-LLM support** – Switch between OpenAI, DeepSeek, Google Gemini, Hugging Face, and GroqCloud via a provider toggle in the LLM Settings panel. Each provider has its own model list, tier selection, and configuration options.
- **DeepSeek V4** – Fully migrated to `deepseek-v4-flash` and `deepseek-v4-pro` with 1M token context windows. Legacy model names `deepseek-chat` and `deepseek-reasoner` are scheduled for retirement on 24 July 2026.
- **Multi-file upload** – Select and send multiple files simultaneously. Contents are combined and sent as context with per-file headers and separators.
- **Audio recording via microphone** – Record audio directly in the browser and send it to the AI. Supported natively by Google Gemini (all models) and OpenAI (`gpt-4o`, `gpt-4.1`). The Record Audio button appears automatically only when an audio-capable model is active.
- **Unique context management** – Delete any individual message along with all subsequent ones. The chat remains consistent and token usage is dynamically recalculated.
- **Maximum security** – API keys are never visible on the client side, uploads are protected against executable files via magic byte inspection, and sessions are stored with restrictive file permissions.
- **No exotic frameworks** – Everything is based on Apache, Python 3, Bash, and plain HTML/JavaScript/CSS. No Node.js, no React, no build pipeline.
- **Professional export functions** – PDF, Markdown, TXT, and RTF for the entire chat or individual messages, plus direct copy to clipboard (client-side, no server roundtrip).
- **Multi-language support** – Full UI translation via external `language.xml` (English, German, Spanish, extensible with a custom language slot).
- **Kompressor (context compression)** – Automatic intelligent compression of the chat history when the context window fills up. A second LLM call summarizes the oldest 50% of messages and injects the summary into the system prompt — enabling indefinitely long conversations without losing context.
- **Quota & limit banners** – Persistent visual banners for exhausted credit (red, paid providers) and daily limits (blue, free-tier providers), each with a close button.
- **Context window exceeded handling** – When the maximum context size is reached, an interactive in-chat box offers two choices: continue with compressed context carried forward, or start a clean new chat. The current session is saved automatically in both cases.
- **Clipboard integration** – Ctrl+V handler with dialog for text, images, and protection against accidentally pasting file paths.
- **Streaming responses** – AI answers appear token by token, just like ChatGPT or Claude.
- **429 Rate limit handling** – Automatic retry with countdown display for Google Gemini Free Tier limits.
- **Included tooling** – The `repo2text.sh` script exports the entire repository as a single text file, ideal for working with AI assistants.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Unique Context Management](#unique-context-management)
- [Features in Detail](#features-in-detail)
  - [Chat Interface](#chat-interface)
  - [Streaming Responses](#streaming-responses)
  - [Clipboard Handler (Ctrl+V)](#clipboard-handler-ctrlv)
  - [File Upload with Security Check](#file-upload-with-security-check)
  - [Umlaut Placeholder System](#umlaut-placeholder-system)
  - [DeepThink Mode](#deepthink-mode)
  - [Model Detection & Capabilities](#model-detection--capabilities)
  - [Multi-Language System](#multi-language-system)
  - [Settings (Toggles instead of Radio Buttons)](#settings-toggles-instead-of-radio-buttons)
  - [Session Management](#session-management)
  - [Export Functions](#export-functions)
  - [Feedback Buttons & Logging](#feedback-buttons--logging)
  - [Dynamic Context Display](#dynamic-context-display)
  - [File Card Display](#file-card-display)
  - [Audio Recording](#audio-recording)
  - [Kompressor — Intelligent Context Compression](#kompressor--intelligent-context-compression)
  - [Quota & Limit Banners](#quota--limit-banners)
  - [Context Window Exceeded Handling](#context-window-exceeded-handling)
- [DeepSeek V4 Migration](#deepseek-v4-migration)
- [The Helper Script `repo2text.sh`](#the-helper-script-repo2textsh)
- [Security Architecture in Detail](#security-architecture-in-detail)
- [Deployment & Usage](#deployment--usage)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Deploy Scripts](#deploy-scripts)
- [Project Structure](#project-structure)
- [Model Configuration](#model-configuration)
- [Design Manifest](#design-manifest)
- [Known Limitations & Technical Notes](#known-limitations--technical-notes)
- [Dependencies](#dependencies)
- [Conclusion / Why This Project Stands Out](#conclusion--why-this-project-stands-out)

---

## Overview

Multi-LLM Chat Client is a **local web application** that communicates with external AI APIs exclusively via server-side Python CGI proxy scripts. Developed for a private Debian server environment, it can run on any Linux system with Apache 2.4 and Python 3. The goal was a **secure, extensible, and user-friendly** chat client without cloud dependencies and with full control over data and API credentials.

The project has grown continuously over several weeks of active development, accumulating features like streaming responses, session management, export functions, multilingual support, clipboard integration, intelligent context compression, audio recording, and robust security measures — without ever introducing external JavaScript frameworks or a build toolchain.

The entire client logic resides in a single `index.html` file (~5,000 lines). All UI texts are externalized to `language.xml`. All server-side operations are handled by 15 Python CGI scripts in `/cgi-bin/`.

---

## Architecture

The architecture is intentionally simple but well thought out:

### 1. Client Layer

- Pure HTML5/JavaScript/CSS3, served via Apache.
- No build tools, no Node.js, no external JavaScript libraries (except PDF.js 3.11.174, loaded via CDN, for in-browser PDF text extraction).
- The entire client logic — message processing, UI updates, streaming reception, language switching, clipboard handling, session management, context estimation — is encapsulated in a single `index.html`.
- All UI texts are loaded from an external `language.xml` at startup via `fetch()`. No hardcoded UI strings exist in the HTML.
- Settings are persisted in `localStorage` with version-controlled schema migration.

### 2. Server Layer

- **Apache 2.4** with `mod_cgi` enabled. HTTPS enforced via SSL configuration.
- **Python 3 CGI scripts** under `/cgi-bin/` handle all server-side operations:

| Script | Function |
|--------|----------|
| `openai-api.py` | Streaming proxy to OpenAI Chat Completions endpoint (native format) |
| `deepseek-api.py` | Streaming proxy to DeepSeek Chat Completions endpoint (OpenAI-compatible) |
| `google-api.py` | Proxy to Google Gemini API with format conversion (OpenAI ↔ Gemini) |
| `hugging-api.py` | Streaming proxy to Hugging Face Inference router (OpenAI-compatible) |
| `groq-api.py` | Streaming proxy to GroqCloud API (OpenAI-compatible, LPU hardware) |
| `compress-context.py` | Context compression — summarizes oldest 50% of messages via second LLM call |
| `deepseek-models.py` | Queries DeepSeek `/v1/models` endpoint at startup for live model detection |
| `save-session.py` | POST: receives `{sessionId, messages}`, validates ID, writes JSON to disk |
| `load-session.py` | GET: returns session list with previews; GET `?id=`: returns full session |
| `delete-session.py` | DELETE: removes session JSON file |
| `export-pdf.py` | Server-side PDF export via ReportLab |
| `export-markdown.py` | Server-side Markdown export |
| `export-txt.py` | Server-side TXT export |
| `export-rtf.py` | Server-side RTF export (no external library, manual RTF encoding) |
| `feedback-log.py` | Writes Like/Dislike feedback entries to the server log |
| `get-log.py` | Reads and returns the server log file content |

- **API keys** are provided exclusively via Apache environment variables in `/etc/apache2/envvars` — `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `GOOGLE_API_KEY`, `HF_API_KEY`, `GRQ_API_KEY`. They are **never** present in client code or HTTP responses.
- A single `ScriptAlias /cgi-bin/ /var/www/deepseek-chat/cgi-bin/` covers all scripts — no Apache configuration changes are needed when adding new scripts.

### 3. Data Storage

| Location | Content | Permissions |
|----------|---------|-------------|
| `/var/www/deepseek-chat/sessions/` | Chat session JSON files | `chmod 700` (dir), `chmod 600` (files) |
| `/var/www/deepseek-chat/logs/multi-llm-chat.log` | Server activity log (no API keys, no session content) | `www-data` owned |
| `/var/www/deepseek-chat/kompressor/` | Compression result files (one per compression round) | `www-data` owned |
| Browser `localStorage` | User settings (with version migration), language, model preferences | Client-side only |
| `language.xml` | All UI texts for all languages | Loaded via `fetch()` at page load |

### 4. Helper Scripts

- `deploy.sh` — copies source repo to production directory, sets correct ownership/permissions, reloads Apache.
- `sync-back.sh` — copies changed files from production back to the source repo.
- `install.sh` — installs `deploy.sh` and `sync-back.sh` in the production directory.
- `tag-release.sh` — creates a Git tag with auto-incremented version (e.g. `v0.94 → v0.95`) and pushes it. Runs `git fetch --tags` automatically to avoid conflicts with existing remote tags.
- `repo2text.sh` — exports the entire repository as a single delimited text file for AI assistants.

---

## Unique Context Management

One of the standout features is the ability to **delete any individual message along with all subsequent ones**. This goes far beyond the typical "delete last message" and allows flexible correction of conversation history at any point.

**Implementation**:
- Each message (user & AI) receives a unique ID (format: `msg_N`) and is stored in the array `contextHistory.messages[]`.
- `deleteMessage(msgId)` determines the index of the target message, truncates the array from that index onwards, and removes all following DOM elements (messages + dividers).
- `updateContextEstimation()` immediately recalculates the estimated token count and the percentage context utilization displayed in the header.
- If the context drops below the last triggered compressor threshold after deletion, the compression summary is automatically discarded and threshold tracking is reset — ensuring the compression state always reflects the actual conversation content.
- The modified session is immediately auto-saved via `saveSession()`.

**Why this is unique**: Most chat clients only allow deletion of the last message or no history manipulation at all. Here, the user can **define any point in the conversation as a new starting point** — ideal for testing prompt variations, correcting mistakes mid-conversation, or cleaning up the context window without discarding the entire chat.

**Regenerate function**: Every AI response includes a "Regenerate" button that removes the current response from both context and DOM, then issues a new API call based on the same user message and full preceding history.

---

## Features in Detail

### Chat Interface

- **Fixed Dark Mode** — Background `#121212`, text `#f0f0f0`, accent `#0056b3`. No light mode option by design.
- **Server header** (4 lines): server name (blue `#4dabf7`), internal IP address, dynamic context utilization with active model name, detected model IDs from the DeepSeek API.
- **Message containers**: hover-triggered action buttons (feedback, per-message export, delete). User messages appear in blue (`#4dabf7`), AI responses in white-on-dark.
- **Textarea**: expands on focus from 40px to 120px via CSS transition. Enter sends the message; Shift+Enter inserts a line break.
- **Strict pill-style design**: border-radius 20px, height 36px for all buttons — no square buttons anywhere in the UI.
- `white-space: pre-wrap` on all message content preserves formatting from AI responses.
- Auto-scroll to the latest message is active during and after streaming.

### Streaming Responses

All AI responses are received and displayed **token by token** using Server-Sent Events (SSE):

- All five CGI proxy scripts send their respective API requests with `stream: True` (or equivalent) and forward the raw SSE event stream directly to the client without buffering.
- `index.html` reads the stream via the `ReadableStream` API with `TextDecoder`.
- Each received chunk is appended to the active message DOM element in real time.
- **Technical SSE headers** set by all CGI proxy scripts:
  ```
  Content-Type: text/event-stream
  X-Accel-Buffering: no
  Cache-Control: no-cache
  ```
- The psychological effect is significant: first tokens appear within ~300ms instead of waiting 5–10 seconds for a complete response.
- Both `sendMessage()` and `handleRegenerate()` use identical streaming logic.

### OpenAI Integration

- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Architecture**: Native OpenAI Chat Completions format — no format conversion required. SSE stream forwarded directly by `openai-api.py`.
- **API key**: `OPENAI_API_KEY` via Apache environment variables.
- **Free Tier models**: `gpt-4o-mini`, `gpt-5-mini`
- **Paid Tier models**: `gpt-5.4`, `gpt-5.2-chat-latest`, `gpt-4o`, `gpt-4.1`, `gpt-4o-mini`
- **Audio input**: `gpt-4o` and `gpt-4.1` support microphone recordings. Audio is sent as `input_audio` blocks in OpenAI's native format. The recording button is automatically shown/hidden based on the active model.
- The DeepThink button and indicator are hidden when OpenAI is the active provider.
- System prompt identifies the active model: *"You are [model], an AI assistant made by OpenAI."*

### Google Gemini Integration

- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent`
- **Architecture**: `google-api.py` converts the OpenAI-compatible internal message format to Gemini's `contents` format, sends the request, and converts the Gemini SSE response back to the OpenAI SSE format expected by the client.
- **API key**: `GOOGLE_API_KEY` via Apache environment variables.
- **Free Tier models**: `gemini-2.5-flash` (5 RPM, 20 RPD)
- **Paid Tier models**: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-pro`, `gemini-2.0-flash`
- **Audio input**: All Gemini models support audio natively. Audio is sent as `inline_data` blocks in Gemini format. The recording button is always visible when Google Gemini is active.
- The DeepThink button and indicator are hidden when Google Gemini is the active provider.

### Hugging Face Integration

- **Endpoint**: `https://router.huggingface.co/v1/chat/completions` — the Hugging Face inference router selects the fastest available provider automatically.
- **Architecture**: OpenAI-compatible format — no conversion required. SSE forwarded directly by `hugging-api.py`.
- **API key**: `HF_API_KEY` — a Write token from `huggingface.co/settings/tokens` with "Make calls to Inference Providers" permission.
- **Free Tier models**: `Qwen/Qwen2.5-72B-Instruct`, `mistralai/Mistral-7B-Instruct-v0.3`, `microsoft/Phi-3.5-mini-instruct`
- **Paid Tier models**: `meta-llama/Meta-Llama-3.1-70B-Instruct`, `meta-llama/Meta-Llama-3.1-405B-Instruct`, `Qwen/Qwen2.5-72B-Instruct`, `mistralai/Mixtral-8x7B-Instruct-v0.1`
- The DeepThink button and indicator are hidden when Hugging Face is active.

### GroqCloud Integration

- **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Architecture**: OpenAI-compatible format — no conversion required. SSE forwarded directly by `groq-api.py`.
- **API key**: `GRQ_API_KEY` via Apache environment variables.
- **Important**: A `User-Agent` header is required in all requests — without it, Cloudflare returns error code 1010 and blocks the request.
- **Free & Paid Tier models**: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `meta-llama/llama-4-scout-17b-16e-instruct`, `qwen/qwen3-32b`. Paid only: `moonshotai/kimi-k2-instruct-0905`.
- All models run on GroqCloud's LPU (Language Processing Unit) hardware, delivering very low inference latency.
- The DeepThink button and indicator are hidden when GroqCloud is the active provider.

### LLM Settings Panel

A dedicated **LLM Settings** panel (separate from the main Settings panel) keeps all provider-specific configuration out of the main interface:

- **Provider selection**: Toggle between OpenAI, DeepSeek, Google Gemini, Hugging Face, and GroqCloud — exactly one provider active at a time.
- **OpenAI options**: Free / Paid plan toggle with automatic model list update.
- **DeepSeek options**: Default mode (Normal Chat / DeepThink), Privacy toggle (`X-No-Training` header).
- **Google options**: Free / Paid plan toggle with automatic model list update.
- **Hugging Face options**: Free / Paid plan toggle with automatic model list update.
- **GroqCloud options**: Free / Paid plan toggle with automatic model list update.
- **Kompressor options**: Enable/disable toggle, compression provider selection (paid providers only), compression model selection. Default: enabled, DeepSeek / `deepseek-v4-flash`.
- **Model dropdown**: Always visible, content updates automatically based on the active provider and selected plan.
- All LLM settings are persisted in `localStorage` and survive page reloads.

### 429 Rate Limit Handling

The Google Gemini Free Tier enforces strict rate limits (5 RPM, 20 RPD). The client handles these gracefully without showing a raw error:

- On HTTP 429, the client automatically retries up to **3 times** with **15-second intervals**.
- During the wait, a countdown is displayed directly in the chat: *"Rate limit reached – waiting 15 seconds and retrying... (Attempt 1/3)"*.
- After 3 failed attempts, the daily limit check triggers the blue limit banner if applicable.
- The retry logic distinguishes between temporary RPM limits (retryable) and exhausted daily quota (non-retryable).
- Verbose error details are written to the server log for diagnosis.

### Clipboard Handler (Ctrl+V)

A sophisticated clipboard handler intercepts all paste events and responds intelligently based on content type:

**Text content** → A paste dialog appears with two options:
- *"Insert at cursor position"* — inserts the text directly into the input field at the current cursor position.
- *"Attach as file"* — treats the clipboard text as `clipboard.txt` and attaches it as a file card to the next message.

**Image content** → A thumbnail preview box appears above the input field showing the image, its dimensions in KB, and a remove button. The image is ready to be sent with the next message if the active model supports images.

**File paths from file managers (XFCE/Thunar, KDE/Dolphin, etc.)** → Blocked with an alert:
> *"Files copied in the file manager cannot be read by the browser. Please use the Upload button instead."*

**Technical background**: On Linux/X11/Firefox, `e.preventDefault()` does not reliably block paste events for content originating from file managers. The implemented solution allows the paste, then immediately checks the input field content via `setTimeout(0)` and clears it if file paths are detected. Detection logic: 2 or more lines where every non-empty line begins with `/` or `file://`. A `requestAnimationFrame` call ensures the input field is visually cleared before the alert dialog appears.

### File Upload with Security Check

- **Accepted formats**: `.txt`, `.pdf`, `.doc`, `.docx`, `.jpg`, `.jpeg`, `.png`, `.csv`, `.xlsx`, `.pptx`
- **Content-extractable formats** (text sent to the AI): `.txt`, `.pdf`
- **Other accepted formats**: attached as binary context (without text extraction)
- **Maximum file size**: 10 MB per file
- **Maximum extracted content**: dynamic — calculated as 75% of the active model's context window in characters: `getDynamicMaxFileChars() = Math.floor(config.maxContextTokens × 4 × 0.75)`

**Dynamic upload limit examples**:

| Model | maxContextTokens | Max file content |
|-------|-----------------|------------------|
| `deepseek-v4-flash` | 1,048,576 | ~3,145,000 chars |
| `deepseek-v4-pro` | 1,048,576 | ~3,145,000 chars |
| `gemini-2.5-flash` | 1,048,576 | ~3,145,000 chars |
| `gemini-1.5-pro` | 2,097,152 | ~6,291,000 chars |
| `gpt-4o` | 128,000 | ~384,000 chars |

**Magic byte inspection** (first 20 bytes) detects and blocks executable files regardless of filename extension:

| Platform | Format | Hex Signature |
|----------|--------|---------------|
| Windows 32/64 bit | PE/MZ Executable | `4D 5A` |
| Linux 32 bit | ELF32 | `7F 45 4C 46 01` |
| Linux 64 bit | ELF64 | `7F 45 4C 46 02` |
| ARM 32 bit | ELF32 ARM | `7F 45 4C 46 01 01 01 00 ... 02 00 28 00` |
| ARM 64 bit | ELF64 AArch64 | `7F 45 4C 46 02 01 01 00 ... 02 00 B7 00` |
| macOS 32 bit | Mach-O | `CE FA ED FE` |
| macOS 64 bit | Mach-O | `CF FA ED FE` |
| macOS Universal | Fat Binary | `CA FE BA BE` |
| macOS/iOS ARM 32 | Big Endian | `FE ED FA CE` |
| macOS/iOS ARM 64 | Big Endian | `FE ED FA CF` |
| Linux/macOS | Shell Script | `23 21` (`#!`) |
| Python | Bytecode (.pyc) | `55 0D 0D 0A` |

**PDF extraction**: Uses PDF.js 3.11.174 loaded from CDN with automatic fallback to a secondary CDN. Extraction progress is displayed page by page. Extraction timeout: 30 seconds.

**Pre-upload context check**: Before extracting file content, the client estimates whether adding the file would exceed the dynamic upload limit. If it would, the upload is blocked with a clear error message before any content is extracted.

### Umlaut Placeholder System

A unique solution for a fundamental problem with the DeepSeek API and German text:

**Problem**: DeepSeek internally replaces German umlauts in file content with ASCII equivalents (e.g. `Ä → AeNDERUNG`, `Ü → MUeSSEN`). This behavior cannot be suppressed via system prompts or API parameters.

**Solution**: Before sending file content to DeepSeek, umlauts are replaced with unique bracketed placeholders. DeepSeek returns these placeholders unchanged. JavaScript replaces them back to real umlauts after receiving the response.

| Original | Placeholder |
|----------|-------------|
| `ä` | `[[AE]]` |
| `ö` | `[[OE]]` |
| `ü` | `[[UE]]` |
| `ß` | `[[SS]]` |
| `Ä` | `[[CAE]]` |
| `Ö` | `[[COE]]` |
| `Ü` | `[[CUE]]` |

**Critical implementation detail**: Both `encodeUmlautsForAI()` and `decodeUmlautsFromAI()` use exclusively **Unicode escape sequences** (`\u00e4` instead of `ä`) and `split()/join()` instead of regex — essential to prevent corruption when files are transferred via Git or edited in text editors.

The decode runs **both during streaming** (token by token) and again after the complete response is received, ensuring no placeholders remain visible even with partial chunk delivery.

This system is applied **only to file content**, never to regular user messages or system prompts.

### DeepThink Mode

DeepThink is a dedicated mode for deep analytical reasoning, exclusively available when DeepSeek is the active provider:

- Activated via a dedicated pill-style button in the second button row below the input field.
- When active, `deepseek-v4-flash` is used — the same model as normal mode, but the mode is recorded with each message. The more capable `deepseek-v4-pro` can be selected manually via the model dropdown for maximum reasoning depth.
- The button changes visually: inactive (dark `#2d2d2d`) → active blue (`#1e3a5f` background, `#4dabf7` border and text).
- An indicator bar appears below the button row: *"DeepThink Mode active: In-depth analysis in progress"*.
- Context limits and output token limits are automatically adjusted based on the active model's `MODEL_CONFIG` entry.
- The mode is recorded with each message (field `mode: 'deepthink'`) and shown in all export formats.
- The default mode (Chat or DeepThink) can be configured in Settings and is persisted in `localStorage`.
- The DeepThink button and indicator are automatically hidden when any non-DeepSeek provider is active.

### Model Detection & Capabilities

At startup, `index.html` queries `/cgi-bin/deepseek-models.py`, which calls the DeepSeek `/v1/models` endpoint live:

- The returned model IDs are stored in `detectedModels[]` and displayed in the server header: `Model: deepseek-v4-flash, deepseek-v4-pro`.
- A `MODEL_CAPABILITIES` map defines which models support which input types:
  ```javascript
  const MODEL_CAPABILITIES = {
      'deepseek-v4-flash': { images: false, text: true },
      'deepseek-v4-pro':   { images: false, text: true },
      'default':           { images: false, text: true },
  };
  ```
- If an image is pasted via clipboard or a `.jpg`/`.png` file is uploaded, and the current model does not support images, the operation is blocked with an alert before any upload occurs.
- This architecture is **forward-compatible**: adding image support for a model only requires adding or updating its entry in `MODEL_CAPABILITIES`.

### Multi-Language System

The UI supports multiple languages loaded from an external `language.xml` file. No UI strings are hardcoded in `index.html`.

**Currently included languages**:
- English (`en`) — default, no address form distinction
- German (`de`) — with formal/informal address form (Sie/Du)
- Spanish (`es`) — with formal/informal address form (Usted/Tú)
- Custom slot (`custom`) — activated by setting `visible="true"` in `language.xml`

**Technical implementation**:
- All UI texts are referenced by numeric IDs: `t(205)` returns the Send button label in the current language.
- `loadLanguage()` fetches and parses `language.xml` via `fetch()` at page load.
- `t(id)` — returns text for the current language, falls back to English if the ID is not found.
- `tf(id, ...args)` — supports `{0}`, `{1}`, ... placeholder substitution.
- `tform(idFormal, idInformal)` — returns the appropriate text based on the selected address form.
- Language switching is instant, no page reload required.
- The selected language is persisted in `localStorage`.

**Address form system** (German/Spanish):
- Languages declare `has_address_form="true"` in `language.xml`.
- For such languages, the Settings panel shows an "Address Form" group (Formal/Informal).
- The selected form affects: system prompt (enforces consistent AI response style), input placeholder text, all settings description texts.

**System prompt** is built dynamically per request from:
1. Base prompt (text IDs 29/30 for formal/informal)
2. DeepThink addition (text IDs 31/32)
3. A strict file-handling instruction always appended in English regardless of UI language — ensuring consistent AI behavior when processing file content.

### Settings (Toggles instead of Radio Buttons)

All settings use **toggle switches** (sliding left-to-right), never radio buttons or checkboxes:

| Group | Setting | Toggle Color |
|-------|---------|-------------|
| Language | EN / DE / ES / Custom | Green |
| Address Form | Formal / Informal | Green |
| Default Mode | Normal Chat / DeepThink | Blue |
| Privacy | Do not use data for training | Green |

**Toggle behavior**:
- Within a group, toggles behave as radio buttons: activating one deactivates all others in the group.
- Clicking anywhere on the `setting-item` row activates that toggle — not just the toggle element itself.
- Active items receive a colored background: `#1a2e1a` (green groups) or `#1e3a5f` (blue groups).

**Privacy toggle**: Sets the HTTP header `X-No-Training: true` in all API requests to DeepSeek, utilizing DeepSeek's opt-out mechanism for training data.

**Settings persistence**: All settings are stored in `localStorage` under the key `deepseekSettings`. Current schema version: `SETTINGS_VERSION: 1.7`. The `migrateSettings()` function ensures backward compatibility — missing fields are filled with defaults, unknown modes are normalized.

### Session Management

Every conversation is automatically managed as a server-side session:

- **Session ID format**: `YYYY-MM-DD_HHMMSS_random6chars` (e.g. `2026-05-11_143045_abc123`) — generated client-side, validated server-side via regex before any file I/O.
- **Auto-save**: After every sent message pair (user + AI), the complete `contextHistory.messages[]` array is serialized and saved to the server as a JSON file.
- **Session file**: `{sessionId}.json` in `/var/www/deepseek-chat/sessions/`, `chmod 600`, owned by `www-data`.
- **Load Chat History modal**: Lists all saved sessions with ID, date, message preview (first 80 chars), and message count. Each session has [Load] (green) and [Delete] (red) buttons.
- **Load behavior**: The current chat is auto-saved first, then the selected session is restored — full message history, UI reconstruction, context estimation recalculation.
- **Delete**: The JSON file is removed from the server immediately without confirmation dialog.

**CGI endpoint details**:
- `save-session.py` — `POST`: receives `{sessionId, messages}`, validates ID format (regex), writes `sessions/{sessionId}.json`
- `load-session.py` — `GET`: returns `[{id, preview, count, date}]`; `GET ?id=X`: returns full `{messages: [...]}`
- `delete-session.py` — `DELETE ?id=X`: removes `sessions/{sessionId}.json`

### Export Functions

**Global export** (dropdown button in the main button row):

| Format | Generation | Notes |
|--------|-----------|-------|
| PDF | Server-side (`export-pdf.py`, ReportLab) | Header, statistics, table of contents, full chat |
| Markdown | Server-side (`export-markdown.py`) | Identical structure to PDF, with anchors |
| TXT | Server-side (`export-txt.py`) | Plain text with separators |
| RTF | Server-side (`export-rtf.py`) | Manual RTF encoding, umlauts as RTF escape codes |
| **Copy to clipboard** | **Client-side only (no server roundtrip)** | Plain text assembled in JavaScript, written via `navigator.clipboard.writeText()` |

**Per-message export** (hover button on each message):

| Format | Generation |
|--------|-----------|
| TXT | Client-side (JavaScript Blob, `URL.createObjectURL()`) |
| Markdown | Client-side |
| RTF | Client-side |
| PDF | Server-side (single message sent to `export-pdf.py`) |

**Export content** (PDF / Markdown global export):
- Header: server name, IP, export date, active language, address form
- Statistics: total message count, modes used (chat/deepthink), files attached, estimated token count, session duration
- Table of contents with all message timestamps
- Full chat history with per-message timestamps and mode indicators

**Copy to clipboard**: Assembled client-side in TXT format and written via `navigator.clipboard.writeText()`. A 2-second *"Copied!"* confirmation replaces the Export button label, then resets automatically.

**PDF technical note**: Binary PDF data is written exclusively via `sys.stdout.buffer` with HTTP headers encoded as bytes — avoiding the `"Bad header"` error that occurs when mixing `print()` (text mode stdout) with binary content.

### Feedback Buttons & Logging

Four buttons appear on hover for each AI response (left side, bottom row):

- **Copy** — Copies message text to clipboard; shows *"Copied!"* for 2 seconds, then resets.
- **Like** — Marks the response positively (blue highlight); sends a `LIKE` entry to the server log. Clicking again removes the like.
- **Dislike** — Marks the response negatively (red highlight); sends a `DISLIKE` entry. Like and Dislike are mutually exclusive.
- **Regenerate** — Removes the current AI response from context array and DOM, then calls the API again with the same user message and full preceding history.

**Server log format** (`/var/www/deepseek-chat/logs/multi-llm-chat.log`):
```
2026-05-11T12:30:00.000 | IP: 194.182.64.122 | POST /cgi-bin/deepseek-api.py | Status: 200
2026-05-11T12:30:00.000 | IP: 194.182.64.122 | FEEDBACK | LIKE | msg_5 | "First 60 chars of response..."
```

**Never logged**: API keys, full session contents, or message text beyond the 60-character feedback preview.

### Dynamic Context Display

The server header shows four lines of real-time information:
1. Server name (blue `#4dabf7`)
2. `IP: xxx.xxx.xxx.xxx`
3. `Context: XX% (active-model-name)`
4. `Model: deepseek-v4-flash, deepseek-v4-pro` (live from `/v1/models`)

**Context utilization calculation**:
- Estimated tokens = sum of character counts in the last `maxContextMessages` messages × `TOKENS_PER_CHAR` (0.25)
- System prompt tokens are added as a fixed overhead
- Percentage = estimated tokens / `maxContextTokens` × 100

**Warning system**: Above 90% context utilization, the context line turns red and blinks (CSS keyframe animation, opacity 0 → 1, 1-second cycle). This provides a highly visible early warning.

The display updates automatically after every sent message, every deleted message, and every model switch.

### File Card Display

When a file is uploaded or clipboard text is attached, the user message displays a compact **file card**:

```
┌──────────────────────────────────────┐
│  [PDF]  │  filename.pdf              │
│  icon   │  PDF Document              │
└──────────────────────────────────────┘
```

- File type badge derived from the file extension (PDF, TXT, XLSX, DOCX, etc.)
- Filename truncated to 30 characters with `...` if longer
- Audio recordings display an `AUDIO` badge with the localized label
- Multi-file uploads generate one card per file; all filenames appear in the info bar separated by ` | `

### Audio Recording

The client includes a built-in **microphone recording button** enabling direct voice input to audio-capable models:

- **Visibility**: Controlled by `updateAudioButtonVisibility()`, called on every model change. Visible only when the active model is listed in `AUDIO_CAPABLE_MODELS`.
- **Audio-capable models** (`AUDIO_CAPABLE_MODELS` constant):
  - Google Gemini: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-pro`, `gemini-2.0-flash`
  - OpenAI: `gpt-4o`, `gpt-4.1`
- **Recording flow**: `getUserMedia()` → `MediaRecorder` API → chunked recording (10ms intervals) → `Blob` assembled on stop → base64-encoded.
- **MIME type auto-detection**: `audio/webm` (Chrome/Firefox) or `audio/mp4` (Safari) — detected at runtime via `MediaRecorder.isTypeSupported()`.
- **After recording**: Audio data is shown in the `fileInfo` box as an AUDIO badge card.
- **Request payload**: `audio_data` (base64 string) and `audio_mime_type` are added to the JSON body alongside the text message. The `hasFile` flag is **not** set — no file-processing system prompt is injected for audio.
- **Mutual exclusivity**: File upload and audio recording are mutually exclusive. Starting a recording clears any pending file attachment and vice versa.
- **Backend — Google (`google-api.py`)**: Audio is appended to the last user message as an `inline_data` block in Gemini's native format.
- **Backend — OpenAI (`openai-api.py`)**: Audio is appended as an `input_audio` block with `format: webm` or `mp4`.
- **Maintenance rule** (Manifest rule E.1): Whenever an integrated provider adds or removes audio support for a model, `AUDIO_CAPABLE_MODELS` in `index.html` **must** be updated immediately.

### Kompressor — Intelligent Context Compression

Every language model has a finite context window. In long sessions — particularly with large file uploads, multi-hour conversations, or extensive analysis workflows — the context window eventually fills, causing API errors (HTTP 400/413) that force the user to start over and lose the entire conversation thread.

The **Kompressor** solves this problem automatically and transparently, without any user action required.

#### Core Concept

Instead of truncating old messages or forcing a manual restart, the Kompressor **summarizes** the oldest half of the conversation via a dedicated second LLM call. This summary is injected into the system prompt of all subsequent requests. The active model effectively "remembers" the summarized past — the conversation can continue indefinitely.

#### Activation Thresholds

| Threshold | Action |
|-----------|--------|
| **70%** context utilization | First compression round |
| **85%** context utilization | Second compression round |
| **95%** context utilization | Third compression round |

Each threshold fires at most once per session cycle. After manual message deletion, if the context percentage drops below the last triggered threshold, all threshold tracking resets.

#### Compression Process (Step by Step)

1. After each sent message, `updateContextEstimation()` recalculates context utilization.
2. If a threshold is exceeded, `compress-context.py` is called **before** the main API call.
3. The oldest 50% of messages are extracted. The cutoff advances to the next user message — ensuring API compatibility (context must always start with a user turn).
4. Base64 data, images, and multimedia content are filtered out — only plain text is sent to the compression LLM.
5. The compression LLM (configurable provider and model) returns a structured summary.
6. The old messages are replaced by a single compressed entry (flag `compressed: true`).
7. The summary text is prepended to the system prompt for all subsequent API calls — never sent as a standalone `assistant` message (which causes 400 errors).
8. The compressed context is saved to disk. The main API call proceeds with the reduced context.

#### Smart Summary Discard

When the user manually deletes messages and the context percentage drops below the **last triggered threshold** (not simply below 70%), the compression summary is automatically removed from the system prompt and all threshold counters reset. This ensures the compression state always matches actual conversation content.

#### Provider Restriction (Paid Only)

The Kompressor makes a separate LLM call that can involve large token counts. Free-tier rate limits (Groq: 6,000–12,000 TPM; Hugging Face: variable) are insufficient for reliable compression of real-world conversations. Only paid providers are offered:

| Provider | Available Compression Models |
|----------|------------------------------|
| DeepSeek | `deepseek-v4-flash`, `deepseek-v4-pro` |
| OpenAI | `gpt-4o-mini`, `gpt-4o`, `gpt-4.1` |
| Google | `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-pro` |

**Recommended default**: DeepSeek + `deepseek-v4-flash` — no rate limits, lowest cost per token, most reliable results.

#### Result Files

Each compression round is saved to disk for review:
```
/var/www/deepseek-chat/kompressor/kompressor_YYYYMMDD_HHMMSS.txt
```

### Quota & Limit Banners

**Red Banner — "Credit must be renewed!"** (paid providers):
- Triggered by exhausted credit on a paid API.
- **DeepSeek**: HTTP 402 response.
- **OpenAI**: HTTP 429 + `insufficient_quota` in JSON response body.
- Displayed as a fixed-position element at the top of the viewport until manually closed (× button).

**Blue Banner — "Daily limit reached!"** (free-tier providers):
- Triggered by exhausted daily quota on a free API.
- **Google Gemini**: HTTP 429 + daily quota keywords in response body.
- **GroqCloud**: HTTP 429.
- **Hugging Face**: HTTP 429.
- Same fixed-position display with × close button.

### Context Window Exceeded Handling

When the API returns HTTP 400 with context-related keywords in the response body, an **interactive box** appears directly in the chat instead of a generic error message:

- **Blue-bordered box**: *"The maximum chat size of the current LLM has been reached."*
- **Green button — "Start new chat with current context"** (Option C):
  1. Current session is auto-saved.
  2. The last compression summary (if available) is combined with all subsequent non-compressed messages as plain text.
  3. A new session starts with this combined context preloaded as a file attachment — the conversation continues seamlessly with full context carry-over.
- **Blue button — "Start new chat without context"** (clean restart):
  1. Current session is auto-saved.
  2. New session starts with an empty context.

This enables **chained conversations** across multiple sessions — theoretically unlimited in total length.

All five CGI proxy scripts detect context overflow by checking the HTTP status code and keyword-matching the API error body, returning `error_type: 'context_exceeded'` to the client.

### API Proxy Documentation Headers

Each of the five CGI proxy scripts (`openai-api.py`, `deepseek-api.py`, `google-api.py`, `hugging-api.py`, `groq-api.py`) contains a structured documentation block directly after the encoding declaration:

- **Import/update date** — when the file was last updated
- **Supported models** — version, context/output token limits, capabilities (text/images/audio/video), free/paid assignment
- **Source link** — official API documentation URL with date

This ensures all model specifications are traceable directly in the source code without consulting external documentation.

---

## DeepSeek V4 Migration

### Background

On **24 April 2026**, DeepSeek released the **DeepSeek V4 Preview** — a new generation of MoE (Mixture-of-Experts) language models with dramatically expanded capabilities. The two new models replace `deepseek-chat` (V3) and `deepseek-reasoner` (R1).

### New Models

| Model | Parameters | Active | Context | Max Output | Thinking Mode |
|-------|-----------|--------|---------|-----------|--------------|
| `deepseek-v4-flash` | 284B total | 13B | 1,048,576 tokens | 8,192 tokens | Yes (Thinking + Non-Thinking) |
| `deepseek-v4-pro` | 1.6T total | 49B | 1,048,576 tokens | 32,768 tokens | Yes (Thinking + Non-Thinking) |

### Architecture Improvements (V4 vs. V3)

- **Hybrid Attention**: V4 combines Compressed Sparse Attention (CSA) and Heavily Compressed Attention (HCA) — enabling 1M token context with only 27% of the single-token inference FLOPs of V3.2 and only 10% of the KV cache.
- **Manifold-Constrained Hyper-Connections (mHC)**: Strengthens residual connections for more stable signal propagation across layers.
- **Three reasoning effort modes**: Non-think (fast), Think High (logical analysis), Think Max (full reasoning extent) — accessible via API parameters.

### Deprecation Timeline

| Date | Event |
|------|-------|
| 24 April 2026 | V4 Preview released. `deepseek-chat` and `deepseek-reasoner` begin routing to `deepseek-v4-flash`. |
| **24 July 2026** | **`deepseek-chat` and `deepseek-reasoner` fully retired and inaccessible.** |

### Changes Made in This Project (11 May 2026)

**`index.html`**:
- `MODEL_CONFIG`: `deepseek-chat` (100k tokens) → `deepseek-v4-flash` (1,048,576 tokens); `deepseek-reasoner` (65k tokens) → `deepseek-v4-pro` (1,048,576 tokens)
- `MODEL_CAPABILITIES`: updated to `deepseek-v4-flash` and `deepseek-v4-pro`
- `DEEPSEEK_MODELS`, `COMPRESSOR_MODELS.deepseek`: updated to V4 names
- Model dropdowns (model select + compressor model select): V4 options
- DeepThink logic (8 occurrences): both modes use `deepseek-v4-flash`; `deepseek-v4-pro` selectable via dropdown
- Default settings: `selectedModel` and `compressorModel` default to `deepseek-v4-flash`
- Frontend error handler fixed: `response.json()` body consumption no longer causes empty error messages

**`deepseek-api.py`**:
- Header comment updated to V4 models with correct context/output sizes
- Default model fallback: `'deepseek-chat'` → `'deepseek-v4-flash'`
- Deprecation notice added to header

**`deepseek-models.py`**: No changes needed — fetches model list live from the DeepSeek API. Already returns `deepseek-v4-flash` and `deepseek-v4-pro` correctly.

### API Compatibility

The DeepSeek V4 API uses the same base URL and OpenAI-compatible format as V3. No structural changes to `deepseek-api.py` were required — only the model names needed updating.

---

## The Helper Script `repo2text.sh`

This Bash script was specifically developed to **export the entire source code of a GitHub repository as a single text file** — ideal for passing the complete project context to an AI assistant in a single upload.

**How it works**:
- Clones the repository with `git clone --depth 1`.
- Analyzes all text files (MIME type check + `grep -Iq .`) and writes them sequentially with unique delimiters into an output file.
- Uses `sort -z -u` to deduplicate file paths before processing — prevents duplicate file entries in the output.
- Uses a unique delimiter format (`############ FILE: path/to/file ############`) that cannot appear in source code.
- Explicitly respects `.gitignore` and `.gitattributes`.
- Supports TXT, JSON, and Markdown output formats.
- Creates a ZIP archive of the export file.
- Includes metadata: commit hash, branch, export timestamp.

**Special options**:
- `--flat`: Use only filenames without directory paths.
- `-o, --only PATH`: Export only a specific subdirectory.
- `-md5, --md5`: Compute and include MD5 checksum for each file.
- Intelligent remote URL detection when run inside an existing Git repository.
- Both `md5sum` (Linux) and `md5` (macOS) are supported.

**Usage examples**:

```bash
# Simple export (interactive URL prompt)
./repo2text.sh

# Export with URL as Markdown format
./repo2text.sh -f md https://github.com/debian-professional/multi-llm-chat.git

# Export only the 'shell-scripts' directory with flat structure
./repo2text.sh --flat -o shell-scripts https://github.com/debian-professional/multi-llm-chat.git

# Export with MD5 checksums
./repo2text.sh -md5 https://github.com/debian-professional/multi-llm-chat.git
```

> `repo2text` is also available as a standalone project: [github.com/debian-professional/repo2text](https://github.com/debian-professional/repo2text)

---

## Security Architecture in Detail

Security was a top priority throughout development. All key measures:

### 1. API Keys — Never Exposed to the Client

- All API keys are held exclusively in Apache environment variables (`/etc/apache2/envvars`).
- Each CGI script retrieves its key via `os.environ.get('..._API_KEY')`.
- The client communicates only with local CGI proxies — never directly with external APIs.
- Even a full XSS compromise of the page cannot leak API keys.

### 2. Magic Byte Inspection

- The first 20 bytes of every uploaded file are checked against a comprehensive signature database covering 12 executable formats across 4 platforms.
- If a signature matches, the upload is blocked before any content is read — with a detailed error message showing the detected platform and format.
- Protection works even if malicious files are renamed (e.g. `malware.exe` → `document.pdf`).

### 3. Secure Session Storage

- Sessions directory: `/var/www/deepseek-chat/sessions/` — `chmod 700`, owned by `www-data`.
- Each session file: `chmod 600`.
- Session IDs validated server-side via regex before any file I/O — no path traversal possible.

### 4. Log Without Sensitive Data

- Logged: timestamps, IP addresses, HTTP methods, endpoint paths, status codes, error messages.
- **Never logged**: API keys, session contents, full message text (only 60-char feedback previews).
- OPTIONS preflight requests are filtered to prevent log flooding.

### 5. No Direct Client-API Communication

- All security-critical operations are server-side Python CGI.
- The client has zero knowledge of API credentials, server paths, or session storage locations.

### 6. Input Validation

- Files validated by extension allowlist AND magic byte inspection.
- Session IDs validated against expected format regex server-side.
- Clipboard paste filtered to block file paths before they reach the API.
- `Content-Length` validated before reading POST bodies in CGI scripts.

### 7. Transport Security

- HTTPS enforced via `deepseek-chat-ssl.conf` with Apache mod_ssl.
- Plain HTTP configuration (`deepseek-chat.conf`) disabled via `a2dissite`.

---

## Deployment & Usage

### Prerequisites

- Debian-based Linux (or any Linux with Apache 2.4, Python 3.9+, Bash)
- Apache modules: `mod_cgi`, `mod_ssl`
- Python packages: `reportlab` (for PDF export)
- For `repo2text.sh`: `jq`, `pv`, `zip`, `git`
- Valid API key for at least one supported provider

### Installation

**1. Clone the repository** (as user `source`):
```bash
git clone https://github.com/debian-professional/multi-llm-chat.git /home/source/multi-llm-chat
```

**2. Configure API keys** in `/etc/apache2/envvars`:
```bash
export DEEPSEEK_API_KEY="sk-..."
export OPENAI_API_KEY="sk-proj-..."
export GOOGLE_API_KEY="AIza..."
export HF_API_KEY="hf_..."
export GRQ_API_KEY="gsk_..."
```

**3. Enable Apache configuration**:
```bash
a2ensite deepseek-chat-ssl.conf
a2dissite deepseek-chat.conf
systemctl restart apache2
```

**4. Create required directories**:
```bash
mkdir -p /var/www/deepseek-chat/sessions
chown www-data:www-data /var/www/deepseek-chat/sessions
chmod 700 /var/www/deepseek-chat/sessions
```

**5. Deploy** (as root):
```bash
./deploy.sh source
```

**6. Install helper scripts**:
```bash
./install.sh   # copies deploy.sh and sync-back.sh to production directory
```

### Configuration

**Model configuration** (`MODEL_CONFIG` in `index.html`) — single point of truth for all model limits:
```javascript
const MODEL_CONFIG = {
    // OpenAI
    'gpt-5.4':              { maxContextTokens: 1050000, maxOutputTokens: 16384, maxContextMessages: 100 },
    'gpt-5.2-chat-latest':  { maxContextTokens: 128000,  maxOutputTokens: 16384, maxContextMessages: 80  },
    'gpt-4o':               { maxContextTokens: 128000,  maxOutputTokens: 16384, maxContextMessages: 80  },
    'gpt-4.1':              { maxContextTokens: 1048576, maxOutputTokens: 32768, maxContextMessages: 100 },
    'gpt-4o-mini':          { maxContextTokens: 128000,  maxOutputTokens: 16384, maxContextMessages: 80  },
    'gpt-5-mini':           { maxContextTokens: 128000,  maxOutputTokens: 16384, maxContextMessages: 80  },
    // DeepSeek V4 (as of 11.05.2026)
    'deepseek-v4-flash':    { maxContextTokens: 1048576, maxOutputTokens: 8192,  maxContextMessages: 50  },
    'deepseek-v4-pro':      { maxContextTokens: 1048576, maxOutputTokens: 32768, maxContextMessages: 50  },
    // Google Gemini
    'gemini-2.5-flash':     { maxContextTokens: 1048576, maxOutputTokens: 8192,  maxContextMessages: 100 },
    'gemini-2.5-pro':       { maxContextTokens: 1048576, maxOutputTokens: 65536, maxContextMessages: 100 },
    'gemini-1.5-pro':       { maxContextTokens: 2097152, maxOutputTokens: 8192,  maxContextMessages: 100 },
    'gemini-2.0-flash':     { maxContextTokens: 1048576, maxOutputTokens: 8192,  maxContextMessages: 100 },
    // Hugging Face
    'Qwen/Qwen2.5-72B-Instruct':               { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'mistralai/Mistral-7B-Instruct-v0.3':      { maxContextTokens: 32768,  maxOutputTokens: 4096, maxContextMessages: 40 },
    'microsoft/Phi-3.5-mini-instruct':         { maxContextTokens: 128000, maxOutputTokens: 4096, maxContextMessages: 60 },
    'meta-llama/Meta-Llama-3.1-70B-Instruct':  { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'meta-llama/Meta-Llama-3.1-405B-Instruct': { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'mistralai/Mixtral-8x7B-Instruct-v0.1':    { maxContextTokens: 32768,  maxOutputTokens: 4096, maxContextMessages: 40 },
    // GroqCloud
    'llama-3.3-70b-versatile':                   { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'llama-3.1-8b-instant':                      { maxContextTokens: 131072, maxOutputTokens: 8192, maxContextMessages: 80 },
    'meta-llama/llama-4-scout-17b-16e-instruct': { maxContextTokens: 131072, maxOutputTokens: 8192, maxContextMessages: 80 },
    'qwen/qwen3-32b':                            { maxContextTokens: 131072, maxOutputTokens: 40960, maxContextMessages: 80 },
    'moonshotai/kimi-k2-instruct-0905':          { maxContextTokens: 131072, maxOutputTokens: 8192, maxContextMessages: 80 }
};
const DEEPSEEK_MODELS    = ['deepseek-v4-flash', 'deepseek-v4-pro'];
const OPENAI_MODELS_FREE = ['gpt-4o-mini', 'gpt-5-mini'];
const OPENAI_MODELS_PAID = ['gpt-5.4', 'gpt-5.2-chat-latest', 'gpt-4o', 'gpt-4.1', 'gpt-4o-mini'];
const GOOGLE_MODELS_FREE = ['gemini-2.5-flash'];
const GOOGLE_MODELS_PAID = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-pro', 'gemini-2.0-flash'];
const HF_MODELS_FREE     = ['Qwen/Qwen2.5-72B-Instruct', 'mistralai/Mistral-7B-Instruct-v0.3', 'microsoft/Phi-3.5-mini-instruct'];
const HF_MODELS_PAID     = ['meta-llama/Meta-Llama-3.1-70B-Instruct', 'meta-llama/Meta-Llama-3.1-405B-Instruct', 'Qwen/Qwen2.5-72B-Instruct', 'mistralai/Mixtral-8x7B-Instruct-v0.1'];
const GROQ_MODELS_FREE   = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'meta-llama/llama-4-scout-17b-16e-instruct', 'qwen/qwen3-32b'];
const GROQ_MODELS_PAID   = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'meta-llama/llama-4-scout-17b-16e-instruct', 'qwen/qwen3-32b', 'moonshotai/kimi-k2-instruct-0905'];
const AUDIO_CAPABLE_MODELS = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-pro', 'gemini-2.0-flash', 'gpt-4o', 'gpt-4.1'];
```

**Language configuration** (`language.xml`): Add a `<language id="custom" name="..." visible="true">` block to activate the custom language slot. Set `has_address_form="true"` for languages with formal/informal distinction.

### Deploy Scripts

| Script | Function |
|--------|----------|
| `deploy.sh <user>` | Copies files from `/home/<user>/multi-llm-chat/var/www/deepseek-chat/` to `/var/www/deepseek-chat/`, sets ownership and permissions, reloads Apache |
| `sync-back.sh <user>` | Copies changed files from production back to the source repo |
| `install.sh` | Installs `deploy.sh` and `sync-back.sh` in the production directory |
| `tag-release.sh` | Creates a Git tag with auto-incremented version number and pushes it. Runs `git fetch --tags` first to avoid conflicts with existing remote tags. |

---

## Project Structure

```
/
├── etc/apache2/sites-available/
│   ├── deepseek-chat.conf              (disabled — HTTP only, redirects to HTTPS)
│   └── deepseek-chat-ssl.conf          (active — SSL, CGI, API keys via envvars)
├── shell-scripts/
│   ├── repo2text.sh                    Export entire repo as single text file
│   ├── deploy.sh                       Copies source repo → production
│   ├── sync-back.sh                    Copies production → source repo
│   ├── install.sh                      Installs deploy/sync-back scripts
│   └── tag-release.sh                  Creates and pushes Git version tags
├── var/www/deepseek-chat/
│   ├── index.html                      Main application (~5,000 lines, all JS/CSS/HTML)
│   ├── language.xml                    All UI texts in all languages (EN, DE, ES, Custom)
│   ├── manifest                        Design manifest (all conventions and rules)
│   ├── changelog                       Complete development history (86 entries)
│   ├── files-directorys                File overview / directory listing
│   ├── cgi-bin/
│   │   ├── openai-api.py              Streaming proxy to OpenAI Chat Completions API
│   │   ├── deepseek-api.py            Streaming proxy to DeepSeek Chat Completions API
│   │   ├── google-api.py              Streaming proxy to Google Gemini API (with format conversion)
│   │   ├── hugging-api.py             Streaming proxy to Hugging Face Inference Router
│   │   ├── groq-api.py                Streaming proxy to GroqCloud API (LPU-accelerated)
│   │   ├── compress-context.py        Context compression via second LLM call
│   │   ├── deepseek-models.py         Live model list from DeepSeek /v1/models
│   │   ├── save-session.py            Session save endpoint (POST)
│   │   ├── load-session.py            Session list / load endpoint (GET)
│   │   ├── delete-session.py          Session delete endpoint (DELETE)
│   │   ├── export-pdf.py              PDF export via ReportLab
│   │   ├── export-markdown.py         Markdown export
│   │   ├── export-txt.py              Plain text export
│   │   ├── export-rtf.py              RTF export (manual encoding, no external library)
│   │   ├── feedback-log.py            Like/Dislike feedback logging
│   │   └── get-log.py                 Server log reader
│   ├── logs/                          Server log files (auto-created by Apache/www-data)
│   ├── kompressor/                    Compression result files (auto-created)
│   └── sessions/                      Chat session JSON files (auto-created, chmod 700)
```

---

## Model Configuration

The `MODEL_CONFIG` object in `index.html` is the **single point of truth** for all model-specific limits across all five providers. All features that depend on model limits — context utilization display, dynamic upload limits, context exceeded detection, Kompressor thresholds — read from this single object.

**Updating model configuration**: When a provider updates their models (new model, changed context limits, deprecated model), only the `MODEL_CONFIG` block in `index.html` needs to be updated. No other files require changes unless the model name is also used in the provider model lists (`DEEPSEEK_MODELS`, `GOOGLE_MODELS_*`, etc.) or in `AUDIO_CAPABLE_MODELS`.

Sources: [OpenAI API Docs](https://platform.openai.com/docs), [DeepSeek API Docs](https://api-docs.deepseek.com), [Google Gemini Docs](https://ai.google.dev/gemini-api/docs), [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers), [GroqCloud Docs](https://console.groq.com/docs/models) *(as of 11.05.2026)*.

---

## Design Manifest

The project includes a `manifest` file documenting all design decisions, naming conventions, and development rules. Key rules:

- **All buttons**: Pill-style exclusively (border-radius: 20px, height: 36px). Square buttons are forbidden.
- **Button colors**: Blue (`#0056b3`) for actions, dark-to-blue toggle for modes, red (`#dc3545`) for destructive, green (`#28a745`) for constructive operations.
- **Settings**: Toggle switches only — no radio buttons, no checkboxes anywhere.
- **No emojis** in buttons or labels (exception: the DeepThink icon ✦).
- **No PHP** — exclusively JavaScript (client) and Python 3 (server).
- **No external JavaScript frameworks** — no Node.js, no React, no Vue, no jQuery.
- **Formatting preservation**: Existing indentation and formatting in `index.html` must never be changed by automated tools.
- **`AUDIO_CAPABLE_MODELS` must be kept current** (Manifest rule E.1): Whenever a model gains or loses audio support, the constant must be updated immediately.
- **Provider banners required** (Manifest rule E.1): When adding a new LLM provider, the appropriate quota/limit banner must be implemented in both the CGI script and the client.
- The manifest is a **separate file** and must never be embedded in `index.html`.

---

## Known Limitations & Technical Notes

### "Lost in the Middle" — A Known AI Limitation

All current language models tend to reliably recall content at the **beginning and end** of a long context, while content **in the middle** is sometimes overlooked or hallucinated. (Liu et al., 2023: *"Lost in the Middle: How Language Models Use Long Contexts"*)

**Practical impact**:
- A repository export of this project is approximately 700,000 characters ≈ ~175,000 tokens.
- DeepSeek V4 models (`deepseek-v4-flash`, `deepseek-v4-pro`) have a 1M token context window — the full repository export fits comfortably.
- Google Gemini with 1–2M token context handles the export without issues.
- OpenAI models with 128k context (e.g. `gpt-4o`) **cannot** load the full export — the client will block the upload with a clear error message.
- **Recommendation**: Even with models that technically fit the export, upload only the relevant files for the current task to maximize the model's effective attention.

### GitHub Raw URL Caching

After `git push`, the new version is **not immediately available** via `raw.githubusercontent.com` URLs — GitHub caches these for up to 10 minutes. This is expected behavior and cannot be circumvented. Files are correctly stored on GitHub as soon as `git push` reports success.

### Nano and Unicode — Critical Warning

**Never** edit files containing Unicode escape sequences (such as the umlaut placeholder functions) using `nano` or by copy-pasting into a terminal emulator.

Nano corrupts `\u00e4` sequences to multi-byte garbage (`M-CM-$`), which breaks JavaScript parsing silently.

**The only safe workflow**:
1. Edit files locally in a proper editor (VS Code, gedit, kate).
2. `git add` / `git commit` / `git push` from the local machine.
3. On the server: `git pull` (in the source repo as user `source`).
4. As root: `./deploy.sh source`.

### Linux/X11/Firefox Paste Behavior

On Linux with X11 and Firefox, `e.preventDefault()` in paste event handlers does not reliably block browser-native paste behavior for content originating from file managers. The implemented workaround (allow the paste, check input content in `setTimeout(0)`, clear and alert if file paths detected) is the only reliable solution for this platform-specific limitation.

### Context Overflow Detection Edge Cases

Context overflow detection in all five CGI scripts uses HTTP status code analysis combined with keyword matching in the API error response body. The keyword set is broad enough to cover standard API error messages. However, edge cases with unusual error messages from provider infrastructure changes may not be caught and would fall back to a generic error display.

### DeepSeek Model Self-Reporting

DeepSeek V4 models may report inaccurate self-knowledge when asked about their context window size or version — they respond based on their training data, not their actual API configuration. The actual deployed model (`deepseek-v4-flash` or `deepseek-v4-pro`) can be verified via:
```bash
source /etc/apache2/envvars && curl -s https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

---

## Dependencies

| Component | Purpose | Installation |
|-----------|---------|-------------|
| Apache 2.4 | Web server, CGI, SSL | `apt install apache2` |
| Python 3.9+ | All server-side CGI scripts | `apt install python3` |
| reportlab | Server-side PDF export | `pip3 install reportlab --break-system-packages` |
| PDF.js 3.11.174 | Client-side PDF text extraction | CDN (automatic fallback to secondary CDN) |
| jq | JSON processing in `repo2text.sh` | `apt install jq` |
| pv | Progress display in `repo2text.sh` | `apt install pv` |
| git | Version management | `apt install git` |
| zip | Archive creation in `repo2text.sh` | `apt install zip` |

No exotic frameworks — all dependencies are standard packages in a Debian environment or well-established CDN libraries.

---

## Conclusion / Why This Project Stands Out

This project demonstrates professional-level web development in a minimalist, security-first approach — without unnecessary overhead, but with the highest standards for security, correctness, and user-friendliness.

**Architecture**:
- Clean separation of client (pure HTML/JS) and server (Python CGI) with no blurring of responsibilities.
- API keys never exposed — even a full XSS compromise cannot leak them.
- Single-file client (`index.html`) that is entirely self-contained yet highly modular internally.
- Zero build pipeline — the development environment is identical to production.

**User experience**:
- Streaming responses with sub-second first-token latency.
- Unique flexible context management — delete any message and all following ones.
- Intelligent clipboard handling for text, images, and file path protection.
- Audio recording directly in the browser for Gemini (all models) and OpenAI (`gpt-4o`, `gpt-4.1`).
- Kompressor — automatic context compression enabling indefinitely long conversations.
- Context exceeded handling — interactive in-chat box with smart context carry-over (Option C).
- Quota banners — clear, persistent visual feedback for exhausted credit or daily limits.
- Copy to clipboard — entire chat exported client-side with a single click.
- Multi-language support with address form distinction, loaded from external XML.

**Engineering**:
- Magic byte inspection detecting executables regardless of filename extension — 12 signatures across 4 platforms.
- Umlaut placeholder system solving a fundamental DeepSeek API limitation for German text.
- Forward-compatible model capability map — adding a new model requires a single config entry.
- Precise compressor summary discard: summary invalidated when context drops below the last triggered threshold after manual deletion.
- Dynamic upload limit: 75% of the active model's context window in characters — automatically scales from 384k chars (gpt-4o) to 6.2M chars (gemini-1.5-pro).
- Complete audit trail via Git, detailed 86-entry changelog, and design manifest.

**DeepSeek V4 ready** — migrated to `deepseek-v4-flash` and `deepseek-v4-pro` with 1M token context windows, ahead of the 24 July 2026 legacy model retirement deadline.

**For a professional developer**, this project demonstrates:
- **Security awareness** — API key protection, executable detection, secure session storage, no path traversal.
- **Structured discipline** — design manifest, version tags, strict UI conventions, 86-entry changelog.
- **Problem-solving depth** — X11 paste behavior, umlaut corruption, PDF binary output issues, "Lost in the Middle", context overflow chaining.
- **Complete documentation** — inline code comments, dedicated manifest, per-script documentation headers, three-language README.

---

*Last updated: 11.05.2026*
