# LLM Provider Overview — Decision Guide
## For the Multi-LLM Chat Client (OpenAI · DeepSeek · Google Gemini · Hugging Face · GroqCloud)

> **As of: 19.07.2026** — All prices and limits are subject to change. Official sources:
> [platform.openai.com/docs](https://platform.openai.com/docs) · [api-docs.deepseek.com](https://api-docs.deepseek.com) · [ai.google.dev](https://ai.google.dev/gemini-api/docs) ·
> [huggingface.co/docs](https://huggingface.co/docs/inference-providers) · [console.groq.com/docs](https://console.groq.com/docs/models)

---

## Table of Contents

- [1. Quick Overview (Comparison Table)](#1-quick-overview-comparison-table)
- [2. OpenAI](#2-openai)
- [3. DeepSeek](#3-deepseek)
- [4. Google Gemini](#4-google-gemini)
- [5. Hugging Face](#5-hugging-face)
- [6. GroqCloud](#6-groqcloud)
- [7. Decision Matrix — Who Should Choose What?](#7-decision-matrix--who-should-choose-what)
- [8. Privacy and Legal Aspects](#8-privacy-and-legal-aspects)
- [9. Conclusion](#9-conclusion)

---

## 1. Quick Overview (Comparison Table)

| Criterion | OpenAI | DeepSeek | Google Gemini | Hugging Face | GroqCloud |
|-----------|--------|----------|---------------|--------------|-----------|
| **Origin** | USA | China | USA (Google) | USA (Community) | USA |
| **Own Models** | Yes (GPT-5.6, GPT-5.5, GPT-4.x) | Yes (V4 Flash/Pro) | Yes (Gemini 2.5) | No (Router) | No (Router) |
| **Context Window** | up to 1.05M | 1.05M | up to 1.05M | 8K–128K | 8K–131K |
| **Multimodal** | ✅ Text, Image, Audio¹ | ❌ Text only | ✅ Text, Image, Audio, Video | ❌ Text only* | ❌ Text only |
| **Free Tier** | Limited (gpt-4o-mini, gpt-5.6-luna)² | 5M Tokens (30 days) | Yes (permanent) | Yes (monthly credits) | Yes (permanent) |
| **Cost (cheapest model)** | $0.15/M Token (gpt-4o-mini) | $0.0028/M Token (Cache Hit, V4 Flash) | $0.075/M Token | Pass-through | $0.05/M Token |
| **Strength** | Quality & ecosystem | Lowest price | Multimodal & Context | Model variety | Speed |
| **Weakness** | Price | Privacy (CN) | Complex pricing | Dependent on third parties | Inference only |
| **Native Reasoning** | ✅ (o-series, GPT-5.x via API) | ✅ (V4 Thinking Mode) | ✅ (Flash Thinking) | ❌ | ❌ |
| **Streaming (SSE)** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **OpenAI-compatible Endpoint** | ✅ (native) | ✅ | ❌ (proprietary format) | ✅ | ✅ |

*\* Individual HF models support images, but not through the chat router used in this client.*

*¹ Audio input supported for `gpt-4o` and `gpt-4.1` via the built-in microphone recording feature of this client.*

*² OpenAI does not offer a genuinely free API tier for the GPT-5.x family — "Free" here denotes the cheapest available models, not a $0 quota.*

---

## 2. OpenAI

### 2.1 Company Background

OpenAI is an American AI research company founded in San Francisco in 2015. Originally a non-profit, it transitioned to a "capped-profit" structure in 2019 and has since attracted billions in investment, primarily from Microsoft. OpenAI is widely considered the originator of the modern LLM era — GPT-3 (2020) and ChatGPT (2022) fundamentally changed the public's relationship with AI. The company's models set the de facto industry standard against which all others are benchmarked.

With the GPT-5.6 family — Sol, Terra, and Luna (released 9 July 2026) — OpenAI maintains its position at the frontier of language model capabilities, two full generations ahead of the GPT-5.4 model this client's configuration was originally built around.

### 2.2 Technology

**GPT Architecture:**
OpenAI's GPT series uses a transformer-based decoder architecture. The GPT-5.6 family features a 1.05 million token context window and 128,000 token maximum output across all three variants, with instruction-following and reasoning significantly improved over the GPT-5.4 generation.

**Models in the Client:**

| Model | Context | Max Output | Tier | Notes |
|-------|---------|------------|------|-------|
| `gpt-5.6-sol` | 1,050,000 Token | 128,000 Token | Paid | Flagship model (July 2026) — alias `gpt-5.6` points here |
| `gpt-5.6-terra` | 1,050,000 Token | 128,000 Token | Paid | Balanced performance/cost |
| `gpt-5.6-luna` | 1,050,000 Token | 128,000 Token | Free & Paid | Cheapest/fastest GPT-5.6 tier (successor to the old "nano" class) |
| `gpt-5.5` | 1,050,000 Token | 128,000 Token | Paid | Previous-generation flagship (April 2026) |
| `gpt-5.4` | 1,050,000 Token | 16,384 Token | Paid | Cheaper mainstream option, still supported |
| `gpt-4o` | 128,000 Token | 16,384 Token | Paid | Omni — text + image + audio input; scheduled retirement 23 Oct 2026 |
| `gpt-4.1` | 1,048,576 Token | 32,768 Token | Paid | Coding-optimized, 1M context |
| `gpt-4o-mini` | 128,000 Token | 16,384 Token | Free & Paid | Cost-efficient, high quality; scheduled retirement 23 Oct 2026 |

**API Endpoint:**
OpenAI uses `https://api.openai.com/v1/chat/completions` — the original endpoint that defined the OpenAI-compatible format now used by most other providers. In this client, communication is handled by `openai-api.py`. As of 19 July 2026, the client sends `max_completion_tokens` rather than `max_tokens` — the GPT-5.x family rejects the older parameter with HTTP 400, while `max_completion_tokens` is accepted by the entire lineup including GPT-4o and GPT-4.1.

### 2.3 Pricing (as of 19.07.2026)

All prices in USD per 1 million tokens:

| Model | Input | Output | Free Tier |
|-------|-------|--------|-----------|
| `gpt-5.6-sol` | $5.00/M | $30.00/M | ❌ |
| `gpt-5.6-terra` | $2.50/M | $15.00/M | ❌ |
| `gpt-5.6-luna` | $1.00/M | $6.00/M | ✅ (rate-limited) |
| `gpt-5.5` | $5.00/M | $30.00/M | ❌ |
| `gpt-5.4` | $2.50/M | $15.00/M | ❌ |
| `gpt-4.1` | $2.00/M | $8.00/M | ❌ |
| `gpt-4o` | $2.50/M | $10.00/M | ❌ |
| `gpt-4o-mini` | $0.15/M | $0.60/M | ✅ (rate-limited) |

**Note:** OpenAI pricing remains the most expensive among the five providers in this client, but reflects the highest quality ceiling and the most mature ecosystem. There is no permanent, quota-free tier for any GPT-5.x model — the "Free" grouping in this client denotes the cheapest models, billed at the same per-token rate as any other request.

### 2.4 Strengths

- **Quality Ceiling:** GPT-5.6 Sol represents the current frontier of language model capability
- **Ecosystem:** The original OpenAI API format — the most widely documented and supported API in the industry
- **Reliability:** Enterprise-grade uptime, well-established SLA, global infrastructure
- **Multimodal (all current models):** Image input support alongside text across the entire GPT-4o/4.1/5.x lineup
- **Audio Input (gpt-4o, gpt-4.1):** Microphone recordings can be sent directly to the model via the built-in audio recording feature of this client. Audio is transmitted as base64-encoded WebM/MP4 and processed natively by the model — no transcription step required.
- **Streaming:** Native SSE support, very low latency to first token
- **Context:** The entire GPT-5.x family and GPT-4.1 offer 1M+ token context windows

### 2.5 Weaknesses

- **Price:** The most expensive provider in this client — GPT-5.6 Sol costs roughly 36× more per input token than DeepSeek V4 Flash (cache miss)
- **Free Tier:** Limited to `gpt-4o-mini` and `gpt-5.6-luna` with rate restrictions, not a genuine no-cost quota
- **No Permanent Free Tier:** Free usage is rate-limited, not volume-limited like Google
- **Approaching Retirement:** `gpt-4o` and `gpt-4o-mini` are scheduled for API-wide shutdown on 23 October 2026

### 2.6 Ideal For

Users who need **maximum quality and reliability** and for whom cost is secondary. Also ideal for developers building on the OpenAI ecosystem who want a private, self-hosted frontend. `gpt-5.6-luna` offers an excellent cost-quality ratio for everyday tasks at a fraction of the flagship price.

---

## 3. DeepSeek

### 3.1 Company Background

DeepSeek is a Chinese AI company founded in late 2023, belonging to Hangzhou DeepSeek Artificial Intelligence Co. The company gained worldwide attention in January 2025 when it released DeepSeek V3 and R1 — models that reached GPT-4-level performance with significantly less training effort. This sparked a broad discussion about the efficiency of AI training and caused a short-term drop in Nvidia's stock price.

On 24 April 2026, DeepSeek released **DeepSeek V4** — the generation this client has used since 11 May 2026, replacing the earlier V3.2/R1-based `deepseek-chat`/`deepseek-reasoner` models. Legacy names are scheduled to stop working entirely on **24 July 2026**.

### 3.2 Technology

**Model Architecture:**
DeepSeek V4 uses an expanded **Mixture-of-Experts (MoE)** architecture combined with **Hybrid Attention** — Compressed Sparse Attention (CSA) and Heavily Compressed Attention (HCA). This enables a 1M-token context window at roughly 27% of V3.2's single-token inference FLOPs and only 10% of its KV-cache footprint, alongside **Manifold-Constrained Hyper-Connections (mHC)** for more stable signal propagation across layers.

**Models in the Client:**

| Model | Parameters | Active | Context | Max Output | Capabilities |
|-------|-----------|--------|---------|-----------|--------------|
| `deepseek-v4-flash` | 284B total | 13B | 1,048,576 Token | 8,192 Token | Text only, Thinking + Non-Thinking |
| `deepseek-v4-pro` | 1.6T total | 49B | 1,048,576 Token | 32,768 Token | Text only, Thinking + Non-Thinking |

**DeepThink (V4 Thinking Mode):**
Both V4 models support a Thinking mode with three effort levels (non-think, think-high, think-max), accessible via API parameters. In this client, Thinking mode is activated via the DeepThink button and affects the system prompt; the underlying model (`deepseek-v4-flash` by default, or `deepseek-v4-pro` if selected in the model dropdown) is unaffected by the toggle itself.

### 3.3 Pricing (as of 19.07.2026)

All prices in USD per 1 million tokens:

| Price Type | deepseek-v4-flash | deepseek-v4-pro |
|------------|--------------------|--------------------|
| **Cache Hit (Input)** | $0.0028 | $0.003625 |
| **Cache Miss (Input)** | $0.14 | $0.435 |
| **Output** | $0.28 | $0.87 |

**Context Caching:** Requests that share the same prefix (e.g. system prompt) are automatically cached. Cache hits cost 98% less than cache misses.

**Free Tier:** New API accounts receive 5 million tokens for free (valid for 30 days). No permanent free API tier exists.

### 3.4 Strengths

- **Price-Performance:** Unmatched value — V4 Flash is roughly 35–100× cheaper than GPT-5.5/5.6 at equivalent context lengths
- **Reasoning Capability (Thinking Mode):** V4 Pro undercuts Claude Sonnet 4.6 on price while remaining competitive on reasoning quality
- **OpenAI Compatibility:** Drop-in replacement for OpenAI-based code
- **Context Caching:** Automatic, no configuration needed
- **1M Context as Standard:** Unlike the V3 generation, both V4 models ship with a 1M-token window by default

### 3.5 Weaknesses

- **Text Only:** No image processing, no audio, no video
- **Privacy:** Servers in China; data processed under Chinese law (see Section 8)
- **No Permanent Free Tier:** The 5M free tokens expire after 30 days
- **Self-Reporting Unreliable:** V4 models may misreport their own context window or version when asked directly — verify the actual deployed model via `curl https://api.deepseek.com/v1/models` instead

### 3.6 Ideal For

Users who want to process **high request volumes** at **minimal cost** and whose data does not require a high level of privacy protection. Particularly strong for programming tasks, text analysis, translations, and complex reasoning (Thinking mode with `deepseek-v4-pro`).

---

## 4. Google Gemini

### 4.1 Company Background

Google Gemini is the Large Language Model of Alphabet Inc. (Google). Introduced in December 2023 as the successor to Google PaLM 2, Gemini is deployed across Google Search, Google Workspace, Android, and numerous other products — indirectly used by billions of users every day.

Gemini is currently the only provider in this client that offers true **multimodality** — processing text, images, audio, and video within a single API.

### 4.2 Technology

**Models in the Client:**

| Model | Version | Context Input | Max Output | Capabilities |
|-------|---------|---------------|------------|--------------|
| `gemini-2.5-flash` | 2.5 Flash | 1,048,576 Token | 8,192 Token | Text, Image, Audio, Video |
| `gemini-2.5-pro` | 2.5 Pro | 1,048,576 Token | 65,536 Token | Text, Image, Audio, Video |

**Retired models:** `gemini-2.0-flash` (shut down 1 June 2026) and `gemini-1.5-pro` (retired earlier) have been removed from the client entirely — both are no longer reachable via the API. The client's default fallback model was updated from `gemini-2.0-flash` to `gemini-2.5-flash` accordingly.

**Upcoming retirement:** `gemini-2.5-flash` itself is scheduled for shutdown on **16 October 2026** (successor: `gemini-3.5-flash`, not yet integrated into this client).

### 4.3 Pricing (as of 19.07.2026)

| Model | Input | Output | Free Tier |
|-------|-------|--------|-----------|
| `gemini-2.5-flash` | $0.075/M | $0.30/M | ✅ (permanent, rate-limited: 5 RPM / 20 RPD) |
| `gemini-2.5-pro` | $1.25/M | $5.00/M | ❌ |

### 4.4 Strengths

- **True Multimodality:** Text, image, audio, and video in one API — both Gemini models in this client support live microphone recordings via the built-in audio recording button, and image upload/paste is fully wired end-to-end as of 19 July 2026
- **Large Context:** Up to 1.05M tokens — entire codebases or lengthy legal documents
- **Permanent Free Tier:** No expiry date for `gemini-2.5-flash`
- **GDPR Compliance:** Possible via Vertex AI EU region

### 4.5 Weaknesses

- **Complex Pricing:** Varies by input context size and modality
- **Proprietary Format:** Does not use OpenAI-compatible endpoint format — `google-api.py` performs bidirectional conversion
- **Free Tier Rate Limits:** 429 errors under heavy use (handled automatically in this client via retry with countdown)
- **Shrinking Model Roster:** Two of the four models available a year ago have already been retired; `gemini-2.5-flash` itself has a published shutdown date

### 4.6 Ideal For

Users who need **multimodal capabilities** — including actual image analysis, not just accepted-but-unused uploads — very long context windows, or a permanent free tier without token expiry.

---

## 5. Hugging Face

### 5.1 Company Background

Hugging Face is an American AI company founded in 2016, functioning as a platform and community hub for open-source machine learning. Rather than developing proprietary models, it hosts thousands of open-source models and provides access to them via an Inference Providers API — acting as an intelligent router to various compute backends (AWS, Azure, NVIDIA, etc.).

### 5.2 Models in the Client

| Model | Context | Max Output | Tier |
|-------|---------|------------|------|
| `Qwen/Qwen2.5-72B-Instruct` | 128,000 | 8,192 | Free & Paid |
| `mistralai/Mistral-7B-Instruct-v0.3` | 32,768 | 4,096 | Free |
| `microsoft/Phi-3.5-mini-instruct` | 128,000 | 4,096 | Free |
| `meta-llama/Meta-Llama-3.1-70B-Instruct` | 128,000 | 8,192 | Paid |
| `meta-llama/Meta-Llama-3.1-405B-Instruct` | 128,000 | 8,192 | Paid |

**Removed:** `mistralai/Mixtral-8x7B-Instruct-v0.1` was removed from the client on 19 July 2026 — it is no longer deployed by any Inference Provider on the Hugging Face router and requests would fail.

### 5.3 Strengths

- **Model Variety:** Access to thousands of open-source models
- **No Vendor Lock-in:** Pure open-source weights — run anywhere
- **Monthly Credits:** Free tier with monthly allocation

### 5.4 Weaknesses

- **Dependent on Third Parties:** Actual inference handled by various backends — latency and quality vary, and models can be silently withdrawn from the router (as happened with Mixtral-8x7B)
- **No Proprietary Frontier Models:** Quality ceiling below GPT-5.6 or Gemini 2.5 Pro

### 5.5 Ideal For

Users who want to explore **open-source models** without proprietary dependencies. Excellent for research, experimentation, and tasks where model transparency matters.

---

## 6. GroqCloud

### 6.1 Company Background

Groq is an American semiconductor company that developed its own custom **Language Processing Unit (LPU)** — a chip specifically designed for transformer inference. This hardware advantage results in inference speeds 5–14× faster than GPU-based cloud providers.

### 6.2 Models in the Client

| Model | Context | Max Output |
|-------|---------|------------|
| `llama-3.1-8b-instant` | 131,072 | 8,192 |
| `llama-3.3-70b-versatile` | 128,000 | 8,192 |
| `meta-llama/llama-4-scout-17b-16e-instruct` | 131,072 | 8,192 |
| `qwen/qwen3-32b` | 131,072 | 40,960 |
| `moonshotai/kimi-k2-instruct-0905` | 131,072 | 8,192 |

**Documentation note:** Earlier versions of this document (and of `groq-api.py`'s own header comment) listed `mixtral-8x7b-32768` and `gemma2-9b-it` as the client's GroqCloud models — both were deprecated by Groq in 2025 (20 March and 8 October respectively) and were **never actually the models used by this client's code**. The table above reflects the models genuinely present in `index.html`'s `GROQ_MODELS_FREE`/`GROQ_MODELS_PAID` arrays, corrected on 19 July 2026.

### 6.3 Pricing (as of 19.07.2026)

| Model | Input | Output |
|-------|-------|--------|
| `llama-3.1-8b-instant` | $0.05/M | $0.08/M |
| `llama-3.3-70b-versatile` | $0.59/M | $0.79/M |
| `meta-llama/llama-4-scout-17b-16e-instruct` | $0.11/M | $0.34/M |
| `qwen/qwen3-32b` | $0.29/M | $0.59/M |
| `moonshotai/kimi-k2-instruct-0905` | $1.00/M | $3.00/M (cached input: $0.50/M) |

Free Tier: permanently free with rate limits (30 RPM) — no expiry date, all models included.

### 6.4 Strengths

- **Unmatched Speed:** LPU hardware delivers 5–14× more tokens per second than GPU-based inference
- **Permanent Free Tier:** No expiry, no credit card required, full model access
- **SOC 2, GDPR, HIPAA:** Enterprise compliance available
- **OpenAI Compatible:** Drop-in replacement (note: a `User-Agent` header is required, or Cloudflare blocks the request with error 1010)

### 6.5 Weaknesses

- **Open-Source Models Only:** No frontier proprietary models
- **Inference Only:** No fine-tuning, embeddings, or image generation
- **Limited Context:** Maximum 131K tokens — far below DeepSeek/Gemini/GPT-5.x's 1M+
- **Kimi K2 Pricing Outlier:** At $1.00/$3.00 per million tokens, `moonshotai/kimi-k2-instruct-0905` is priced closer to a mid-tier proprietary model than to Groq's other offerings

### 6.6 Ideal For

Users who prioritize **maximum speed** — for interactive applications, live chat, and rapid brainstorming. Also for users who want a permanently free quota for occasional use with zero setup friction.

---

## 7. Decision Matrix — Who Should Choose What?

### By Use Case

| Use Case | Recommendation | Reason |
|----------|----------------|--------|
| **Analyze images / audio / video** | Google Gemini | Broadest multimodality; OpenAI (gpt-4o/4.1/5.x) also supports images |
| **Send microphone recordings** | Google Gemini or OpenAI (gpt-4o / gpt-4.1) | Built-in audio recording button — visible only for audio-capable models |
| **Highest quality responses** | OpenAI GPT-5.6 Sol | Current frontier model |
| **Complex math / logic** | DeepSeek V4 Pro (Thinking mode) | Best price-performance ratio for reasoning |
| **Very long documents** | DeepSeek V4, Google Gemini, or GPT-5.x | All now offer ~1M token context |
| **Maximum speed** | GroqCloud | LPU-accelerated inference — unmatched latency |
| **Minimum cost** | DeepSeek V4 Flash | Cheapest price per token on the market |
| **Open-source models** | Hugging Face or GroqCloud | Llama, Mistral, Qwen, Kimi K2 — broad selection |
| **Permanently free** | Google (Free) or GroqCloud | Both offer unlimited-duration free tiers |
| **Privacy (EU/GDPR)** | Google Gemini (EU region) | Clear GDPR compliance possible |
| **OpenAI ecosystem** | OpenAI | Native endpoint, best compatibility |
| **Experimentation / Learning** | GroqCloud or HF | Both free to start, straightforward |
| **High-load production** | DeepSeek or GroqCloud | Best cost efficiency at scale |

### By Priority

**I just want fast answers:**
→ **GroqCloud** (`llama-3.1-8b-instant`) — fastest inference, free, ready immediately.

**I want the absolute best answers:**
→ **OpenAI** (`gpt-5.6-sol`) — current quality frontier. Cost-conscious alternative: **DeepSeek** (`deepseek-v4-pro`, Thinking mode).

**I want to pay as little as possible:**
→ **DeepSeek** (`deepseek-v4-flash`) — with context caching, the cheapest frontier-adjacent AI available.

**I don't want to use proprietary models:**
→ **Hugging Face** or **GroqCloud** — both based exclusively on open-source weights.

**I want to analyze images, PDFs, or videos:**
→ **Google Gemini** for full multimodality (image, audio, video); **OpenAI** for image-only analysis on GPT-4o/4.1/5.x.

---

## 8. Privacy and Legal Aspects

### OpenAI
- Server location: **USA** (Microsoft Azure infrastructure)
- Applicable law: US law; GDPR-compliant via enterprise agreements
- SOC 2, ISO 27001
- Data retention: By default, API inputs/outputs are not used to train models (opt-in via API settings)
- **Recommendation:** Well-suited for most professional and enterprise use cases. Clear US jurisdiction; for EU regulated data, check current Data Processing Agreements

### DeepSeek
- Server location: **China** (People's Republic)
- Applicable law: Chinese law, incl. National Intelligence Law (2017)
- **Recommendation:** Often acceptable for personal or non-sensitive data. Caution advised for corporate data, health data, or GDPR-regulated information

### Google Gemini
- Server location: **USA** and other Google Cloud regions (incl. EU possible via Vertex AI)
- SOC 2, ISO 27001, HIPAA (Vertex AI)
- **Recommendation:** Well-suited for EU projects when Vertex AI is used with the EU region

### Hugging Face
- Server location: **USA** (headquarters) with partners worldwide
- Actual data processing takes place at the respective inference providers — privacy law situation is heterogeneous
- **Recommendation:** Well-suited for tests and non-sensitive data

### GroqCloud
- Server location: **USA** with data centers in North America, Europe, Middle East, Asia-Pacific
- Compliance: **SOC 2, GDPR, HIPAA**
- Zero Data Retention available
- **Recommendation:** The most transparent provider with regard to compliance

---

## 9. Conclusion

All five providers are fully-featured, professional LLM services. There is no clear "winner" — each has its specific sweet spot:

**OpenAI** is the choice for maximum quality and reliability. GPT-5.6 Sol represents the current frontier, and `gpt-5.6-luna` offers an excellent cost-quality ratio for everyday tasks at a fraction of the flagship price. The mature ecosystem and native API format make it the industry reference. `gpt-4o`, `gpt-4.1`, and the entire GPT-5.x family support image input, and `gpt-4o`/`gpt-4.1` additionally support direct audio input — this client exposes these capabilities via image upload/paste and a dedicated microphone recording button respectively.

**DeepSeek** is the choice for maximum cost efficiency and strong reasoning capabilities, now on the V4 generation with a 1M-token context window as standard. Those who produce a lot pay the least here. The privacy topic (China) is real and must be evaluated individually. Note the 24 July 2026 deadline: legacy `deepseek-chat`/`deepseek-reasoner` names stop working entirely five days after this document's publication date.

**Google Gemini** is the choice for multimodal tasks (image, audio, video), long contexts, and the best permanent free tier. Both Gemini models in this client support direct microphone recordings and, as of 19 July 2026, genuine image analysis — spoken input and uploaded images are processed natively by the model. Google's infrastructure is reliable and configurable for GDPR compliance, though the roster has shrunk — two previously available models have been retired in the past two months.

**Hugging Face** is the choice for everyone who wants to explore open-source models without risking vendor lock-in. The broad model selection and transparent pass-through pricing are unique, though individual models can and do disappear from the router without much notice (as Mixtral-8x7B did).

**GroqCloud** is the choice for maximum speed. Those who build interactive applications or simply dislike waiting will be impressed by the LPU-accelerated inference. SOC 2 and HIPAA compliance also make it interesting for enterprise applications — just note that `moonshotai/kimi-k2-instruct-0905` breaks from Groq's usual bargain pricing.

**Practical Recommendation for New Users:**
Start with **GroqCloud Free** (free, fast, ready immediately) or **Google Gemini Free Tier** (permanent, multimodal). If you need maximum quality, add **OpenAI** (`gpt-5.6-luna` for cost-efficiency or `gpt-5.6-sol` for the frontier). Once you hit the limits or have specific requirements, decide purposefully using this overview.

---

*Updated: 19.07.2026 | For the Multi-LLM Chat Client github.com/debian-professional/multi-llm-chat*
