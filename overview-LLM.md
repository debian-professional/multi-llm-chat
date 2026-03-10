# LLM Provider Overview — Decision Guide
## For the Multi-LLM Chat Client (OpenAI · DeepSeek · Google Gemini · Hugging Face · GroqCloud)

> **As of: 10.03.2026** — All prices and limits are subject to change. Official sources:
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
| **Own Models** | Yes (GPT-5.4, GPT-4.x) | Yes (V3.2, R1) | Yes (Gemini 2.5/3.x) | No (Router) | No (Router) |
| **Context Window** | up to 1M | 128K | up to 2M | 8K–128K | 8K–131K |
| **Multimodal** | ✅ Text, Image | ❌ Text only | ✅ Text, Image, Audio, Video | ❌ Text only* | ❌ Text only |
| **Free Tier** | Limited (gpt-4o-mini, gpt-5-mini) | 5M Tokens (30 days) | Yes (permanent) | Yes (monthly credits) | Yes (permanent) |
| **Cost (cheapest model)** | $0.15/M Token (gpt-4o-mini) | $0.028/M Token (Cache) | $0.075/M Token | Pass-through | $0.05/M Token |
| **Strength** | Quality & ecosystem | Lowest price | Multimodal & Context | Model variety | Speed |
| **Weakness** | Price | Privacy (CN) | Complex pricing | Dependent on third parties | Inference only |
| **Native Reasoning** | ✅ (o-series via API) | ✅ (R1 DeepThink) | ✅ (Flash Thinking) | ❌ | ❌ |
| **Streaming (SSE)** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **OpenAI-compatible Endpoint** | ✅ (native) | ✅ | ❌ (proprietary format) | ✅ | ✅ |

*\* Individual HF models support images, but not through the chat router used in this client.*

---

## 2. OpenAI

### 2.1 Company Background

OpenAI is an American AI research company founded in San Francisco in 2015. Originally a non-profit, it transitioned to a "capped-profit" structure in 2019 and has since attracted billions in investment, primarily from Microsoft. OpenAI is widely considered the originator of the modern LLM era — GPT-3 (2020) and ChatGPT (2022) fundamentally changed the public's relationship with AI. The company's models set the de facto industry standard against which all others are benchmarked.

With GPT-5.4 (released March 2026), OpenAI maintains its position at the frontier of language model capabilities.

### 2.2 Technology

**GPT Architecture:**
OpenAI's GPT series uses a transformer-based decoder architecture. GPT-5.4 features an extended context window of up to 1.05 million tokens and significantly improved instruction-following and reasoning compared to its predecessors.

**Models in the Client:**

| Model | Context | Max Output | Tier | Notes |
|-------|---------|------------|------|-------|
| `gpt-5.4` | 1,050,000 Token | 16,384 Token | Paid | Flagship model (March 2026) |
| `gpt-5.2-chat-latest` | 128,000 Token | 16,384 Token | Paid | ChatGPT-optimized version |
| `gpt-4o` | 128,000 Token | 16,384 Token | Paid | Omni — text + image input |
| `gpt-4.1` | 1,048,576 Token | 32,768 Token | Paid | Coding-optimized, 1M context |
| `gpt-4o-mini` | 128,000 Token | 16,384 Token | Free & Paid | Cost-efficient, high quality |
| `gpt-5-mini` | 128,000 Token | 16,384 Token | Free | Lightweight GPT-5 variant |

**API Endpoint:**
OpenAI uses `https://api.openai.com/v1/chat/completions` — the original endpoint that defined the OpenAI-compatible format now used by most other providers. In this client, communication is handled by `openai-api.py`.

### 2.3 Pricing (as of 10.03.2026)

All prices in USD per 1 million tokens:

| Model | Input | Output | Free Tier |
|-------|-------|--------|-----------|
| `gpt-5.4` | $1.05/M | $4.20/M | ❌ |
| `gpt-4.1` | $2.00/M | $8.00/M | ❌ |
| `gpt-4o` | $2.50/M | $10.00/M | ❌ |
| `gpt-5.2-chat-latest` | $1.50/M | $6.00/M | ❌ |
| `gpt-4o-mini` | $0.15/M | $0.60/M | ✅ (rate-limited) |
| `gpt-5-mini` | $0.30/M | $1.20/M | ✅ (rate-limited) |

**Note:** OpenAI pricing is the most expensive among the five providers in this client, but reflects the highest quality ceiling and the most mature ecosystem.

### 2.4 Strengths

- **Quality Ceiling:** GPT-5.4 represents the current frontier of language model capability
- **Ecosystem:** The original OpenAI API format — the most widely documented and supported API in the industry
- **Reliability:** Enterprise-grade uptime, well-established SLA, global infrastructure
- **Multimodal (gpt-4o):** Image input support alongside text
- **Streaming:** Native SSE support, very low latency to first token
- **Context:** gpt-5.4 and gpt-4.1 offer up to 1M+ token context windows

### 2.5 Weaknesses

- **Price:** The most expensive provider in this client — GPT-5.4 costs 37× more per input token than DeepSeek (cache hit)
- **Free Tier:** Limited to gpt-4o-mini and gpt-5-mini with rate restrictions
- **No Permanent Free Tier:** Free usage is rate-limited, not volume-limited like Google

### 2.6 Ideal For

Users who need **maximum quality and reliability** and for whom cost is secondary. Also ideal for developers building on the OpenAI ecosystem who want a private, self-hosted frontend. GPT-4o-mini offers an excellent cost-quality ratio for everyday tasks.

---

## 3. DeepSeek

### 3.1 Company Background

DeepSeek is a Chinese AI company founded in late 2023, belonging to Hangzhou DeepSeek Artificial Intelligence Co. The company gained worldwide attention in January 2025 when it released DeepSeek V3 and R1 — models that reached GPT-4-level performance with significantly less training effort. This sparked a broad discussion about the efficiency of AI training and caused a short-term drop in Nvidia's stock price.

DeepSeek represents a fundamental shift in the AI landscape: high-quality models do not have to be expensive.

### 3.2 Technology

**Model Architecture:**
DeepSeek uses a **Mixture-of-Experts (MoE)** architecture combined with **Multi-Head Latent Attention (MLA)**. Instead of activating all parameters for every request, the model dynamically selects only the relevant "experts". This enables a drastic reduction in inference costs without significant loss of quality.

**DeepSeek Sparse Attention (DSA):**
Introduced in late 2025, DSA reduces KV-cache memory requirements by up to 57× compared to standard attention. This innovation allowed a 50% price reduction for the API.

**Models in the Client:**

| Model | Version | Context | Max Output | Capabilities |
|-------|---------|---------|------------|--------------|
| `deepseek-chat` | V3.2 (as of 10.03.2026) | 128K Token | 8,192 Token | Text only |
| `deepseek-reasoner` | R1 (as of 10.03.2026) | 128K Token | 64K Token (Thinking) | Text only + CoT |

**DeepThink (R1 Reasoning):**
The `deepseek-reasoner` model uses genuine Chain-of-Thought Reasoning. It "thinks" step by step internally before responding. This makes it significantly better at complex math, logic, and programming tasks, but also slower and more expensive. In the client, this mode is activated via the DeepThink button.

### 3.3 Pricing (as of 10.03.2026)

All prices in USD per 1 million tokens:

| Price Type | deepseek-chat (V3.2) | deepseek-reasoner (R1) |
|------------|----------------------|------------------------|
| **Cache Hit (Input)** | $0.028 | $0.14 |
| **Cache Miss (Input)** | $0.28 | $0.55 |
| **Output** | $0.42 | $2.19 |

**Context Caching:** Requests that share the same prefix (e.g. system prompt) are automatically cached. Cache hits cost 90% less than cache misses.

**Off-Peak Discount:** Between 16:30–00:30 UTC, discounts of up to 75% (R1) and 50% (V3.2) apply.

**Free Tier:** New API accounts receive 5 million tokens for free (valid for 30 days).

### 3.4 Strengths

- **Price-Performance:** Unmatched value compared to OpenAI GPT-5.4 ($1.05/M) or Claude Sonnet 4.6 ($3/M)
- **Reasoning Capability (R1):** Competitive with OpenAI o1 at a fraction of the price
- **OpenAI Compatibility:** Drop-in replacement for OpenAI-based code
- **Context Caching:** Automatic, no configuration needed

### 3.5 Weaknesses

- **Text Only:** No image processing, no audio, no video
- **Privacy:** Servers in China; data processed under Chinese law (see Section 8)
- **No Permanent Free Tier:** The 5M free tokens expire after 30 days

### 3.6 Ideal For

Users who want to process **high request volumes** at **minimal cost** and whose data does not require a high level of privacy protection. Particularly strong for programming tasks, text analysis, translations, and complex reasoning (R1).

---

## 4. Google Gemini

### 4.1 Company Background

Google Gemini is the Large Language Model of Alphabet Inc. (Google). Introduced in December 2023 as the successor to Google PaLM 2, Gemini is deployed across Google Search, Google Workspace, Android, and numerous other products — indirectly used by billions of users every day.

Gemini is currently the only provider in this client that offers true **multimodality** — processing text, images, audio, and video within a single API.

### 4.2 Technology

**Models in the Client:**

| Model | Version | Context Input | Max Output | Capabilities |
|-------|---------|---------------|------------|--------------|
| `gemini-2.5-flash` | 2.5 Flash (as of 10.03.2026) | 1,048,576 Token | 8,192 Token | Text, Image, Audio, Video |
| `gemini-2.5-pro` | 2.5 Pro (as of 10.03.2026) | 1,048,576 Token | 65,536 Token | Text, Image, Audio, Video |
| `gemini-2.0-flash` | 2.0 Flash (as of 10.03.2026) | 1,048,576 Token | 8,192 Token | Text, Image, Audio, Video |
| `gemini-1.5-pro` | 1.5 Pro (as of 10.03.2026) | 2,097,152 Token | 8,192 Token | Text, Image, Audio, Video |

**Largest Context Window:** With 1–2 million tokens of context, Gemini is in a category of its own.

### 4.3 Pricing (as of 10.03.2026)

| Model | Input | Output | Free Tier |
|-------|-------|--------|-----------|
| `gemini-2.5-flash` | $0.075/M | $0.30/M | ✅ (permanent, rate-limited) |
| `gemini-2.5-pro` | $1.25/M | $5.00/M | ❌ |
| `gemini-1.5-pro` | $1.25/M | $5.00/M | ❌ |
| `gemini-2.0-flash` | $0.10/M | $0.40/M | ✅ (permanent, rate-limited) |

### 4.4 Strengths

- **True Multimodality:** Text, image, audio, and video in one API
- **Massive Context:** Up to 2M tokens — entire codebases or lengthy legal documents
- **Permanent Free Tier:** No expiry date for gemini-2.5-flash and gemini-2.0-flash
- **GDPR Compliance:** Possible via Vertex AI EU region

### 4.5 Weaknesses

- **Complex Pricing:** Varies by input context size and modality
- **Proprietary Format:** Does not use OpenAI-compatible endpoint format
- **Free Tier Rate Limits:** 429 errors under heavy use (handled automatically in this client)

### 4.6 Ideal For

Users who need **multimodal capabilities**, very long context windows, or a permanent free tier without token expiry.

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
| `mistralai/Mixtral-8x7B-Instruct-v0.1` | 32,768 | 4,096 | Paid |

### 5.3 Strengths

- **Model Variety:** Access to thousands of open-source models
- **No Vendor Lock-in:** Pure open-source weights — run anywhere
- **Monthly Credits:** Free tier with monthly allocation

### 5.4 Weaknesses

- **Dependent on Third Parties:** Actual inference handled by various backends — latency and quality vary
- **No Proprietary Frontier Models:** Quality ceiling below GPT-5.4 or Gemini 2.5 Pro

### 5.5 Ideal For

Users who want to explore **open-source models** without proprietary dependencies. Excellent for research, experimentation, and tasks where model transparency matters.

---

## 6. GroqCloud

### 6.1 Company Background

Groq is an American semiconductor company that developed its own custom **Language Processing Unit (LPU)** — a chip specifically designed for transformer inference. This hardware advantage results in inference speeds 10–30× faster than GPU-based cloud providers.

### 6.2 Models in the Client

| Model | Context | Max Output |
|-------|---------|------------|
| `llama-3.3-70b-versatile` | 128,000 | 8,192 |
| `llama-3.1-8b-instant` | 131,072 | 8,192 |
| `mixtral-8x7b-32768` | 32,768 | 32,768 |
| `gemma2-9b-it` | 8,192 | 8,192 |

### 6.3 Pricing (as of 10.03.2026)

| Model | Input | Output |
|-------|-------|--------|
| `llama-3.1-8b-instant` | $0.05/M | $0.08/M |
| `llama-3.3-70b-versatile` | $0.59/M | $0.79/M |
| `mixtral-8x7b-32768` | $0.24/M | $0.24/M |
| `gemma2-9b-it` | $0.20/M | $0.20/M |

Free Tier: permanently free with rate limits — no expiry date.

### 6.4 Strengths

- **Unmatched Speed:** 400–1,200 tokens/second
- **Permanent Free Tier:** No expiry, no credit card required
- **SOC 2, GDPR, HIPAA:** Enterprise compliance available
- **OpenAI Compatible:** Drop-in replacement

### 6.5 Weaknesses

- **Open-Source Models Only:** No frontier proprietary models
- **Inference Only:** No fine-tuning, embeddings, or image generation
- **Limited Context:** Maximum 131K tokens

### 6.6 Ideal For

Users who prioritize **maximum speed** — for interactive applications, live chat, and rapid brainstorming. Also for users who want a permanently free quota for occasional use.

---

## 7. Decision Matrix — Who Should Choose What?

### By Use Case

| Use Case | Recommendation | Reason |
|----------|----------------|--------|
| **Analyze images / audio / video** | Google Gemini | Only provider with true multimodality |
| **Highest quality responses** | OpenAI GPT-5.4 | Current frontier model |
| **Complex math / logic** | DeepSeek R1 | Best price-performance ratio for reasoning |
| **Very long documents** | Google Gemini | 1–2M token context, no alternative |
| **Maximum speed** | GroqCloud | 400–1,200 tokens/sec — unmatched |
| **Minimum cost** | DeepSeek | Cheapest price per token on the market |
| **Open-source models** | Hugging Face | Llama, Mistral, Qwen — broad selection |
| **Permanently free** | Google (Free) or GroqCloud | Both offer unlimited free tiers |
| **Privacy (EU/GDPR)** | Google Gemini (EU region) | Clear GDPR compliance possible |
| **OpenAI ecosystem** | OpenAI | Native endpoint, best compatibility |
| **Experimentation / Learning** | GroqCloud or HF | Both free to start, straightforward |
| **High-load production** | DeepSeek or GroqCloud | Best cost efficiency at scale |

### By Priority

**I just want fast answers:**
→ **GroqCloud** (`llama-3.1-8b-instant`) — fastest inference, free, ready immediately.

**I want the absolute best answers:**
→ **OpenAI** (`gpt-5.4`) — current quality frontier. Cost-conscious alternative: **DeepSeek** (`deepseek-reasoner`).

**I want to pay as little as possible:**
→ **DeepSeek** (`deepseek-chat`) — with context caching and off-peak hours, the cheapest frontier AI available.

**I don't want to use proprietary models:**
→ **Hugging Face** or **GroqCloud** — both based exclusively on open-source weights.

**I want to analyze images, PDFs, or videos:**
→ **Google Gemini** — the only option in this client.

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

**OpenAI** is the choice for maximum quality and reliability. GPT-5.4 represents the current frontier, and gpt-4o-mini offers an excellent cost-quality ratio for everyday tasks. The mature ecosystem and native API format make it the industry reference.

**DeepSeek** is the choice for maximum cost efficiency and strong reasoning capabilities. Those who produce a lot pay the least here. The privacy topic (China) is real and must be evaluated individually.

**Google Gemini** is the choice for multimodal tasks (image, audio, video), very long contexts, and the best permanent free tier. Google's infrastructure is reliable and configurable for GDPR compliance.

**Hugging Face** is the choice for everyone who wants to explore open-source models without risking vendor lock-in. The broad model selection and transparent pass-through pricing are unique.

**GroqCloud** is the choice for maximum speed. Those who build interactive applications or simply dislike waiting will be impressed by the LPU-accelerated inference. SOC 2 and HIPAA compliance also make it interesting for enterprise applications.

**Practical Recommendation for New Users:**
Start with **GroqCloud Free** (free, fast, ready immediately) or **Google Gemini Free Tier** (permanent, multimodal). If you need maximum quality, add **OpenAI** (`gpt-4o-mini` for cost-efficiency or `gpt-5.4` for the frontier). Once you hit the limits or have specific requirements, decide purposefully using this overview.

---

*Updated: 10.03.2026 | For the Multi-LLM Chat Client github.com/debian-professional/private-chatboot*
