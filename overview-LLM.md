# LLM Provider Overview — Decision Guide
## For the Multi-LLM Chat Client (DeepSeek · Google Gemini · Hugging Face · GroqCloud)

> **As of: 08.03.2026** — All prices and limits are subject to change. Official sources:
> [api-docs.deepseek.com](https://api-docs.deepseek.com) · [ai.google.dev](https://ai.google.dev/gemini-api/docs) ·
> [huggingface.co/docs](https://huggingface.co/docs/inference-providers) · [console.groq.com/docs](https://console.groq.com/docs/models)

---

## Table of Contents

- [1. Quick Overview (Comparison Table)](#1-quick-overview-comparison-table)
- [2. DeepSeek](#2-deepseek)
- [3. Google Gemini](#3-google-gemini)
- [4. Hugging Face](#4-hugging-face)
- [5. GroqCloud](#5-groqcloud)
- [6. Decision Matrix — Who Should Choose What?](#6-decision-matrix--who-should-choose-what)
- [7. Privacy and Legal Aspects](#7-privacy-and-legal-aspects)
- [8. Conclusion](#8-conclusion)

---

## 1. Quick Overview (Comparison Table)

| Criterion | DeepSeek | Google Gemini | Hugging Face | GroqCloud |
|-----------|----------|---------------|--------------|-----------|
| **Origin** | China | USA (Google) | USA (Community) | USA |
| **Own Models** | Yes (V3.2, R1) | Yes (Gemini 2.5/3.x) | No (Router) | No (Router) |
| **Context Window** | 128K | up to 2M | 8K–128K | 8K–131K |
| **Multimodal** | ❌ Text only | ✅ Text, Image, Audio, Video | ❌ Text only* | ❌ Text only |
| **Free Tier** | 5M Tokens (30 days) | Yes (permanent) | Yes (monthly credits) | Yes (permanent) |
| **Cost (cheapest model)** | $0.028/M Token (Cache) | $0.075/M Token | Pass-through | $0.05/M Token |
| **Strength** | Lowest price | Multimodal & Context | Model variety | Speed |
| **Weakness** | Privacy (CN) | Complex pricing | Dependent on third parties | Inference only |
| **Native Reasoning** | ✅ (R1 DeepThink) | ✅ (Flash Thinking) | ❌ | ❌ |
| **Streaming (SSE)** | ✅ | ✅ | ✅ | ✅ |
| **OpenAI-compatible Endpoint** | ✅ | ❌ (proprietary format) | ✅ | ✅ |

*\* Individual HF models support images, but not through the chat router used in this client.*

---

## 2. DeepSeek

### 2.1 Company Background

DeepSeek is a Chinese AI company founded in late 2023, belonging to Hangzhou DeepSeek Artificial Intelligence Co. The company gained worldwide attention in January 2025 when it released DeepSeek V3 and R1 — models that reached GPT-4-level performance with significantly less training effort. This sparked a broad discussion about the efficiency of AI training and caused a short-term drop in Nvidia's stock price.

DeepSeek represents a fundamental shift in the AI landscape: high-quality models do not have to be expensive.

### 2.2 Technology

**Model Architecture:**
DeepSeek uses a **Mixture-of-Experts (MoE)** architecture combined with **Multi-Head Latent Attention (MLA)**. Instead of activating all parameters for every request, the model dynamically selects only the relevant "experts". This enables a drastic reduction in inference costs without significant loss of quality.

**DeepSeek Sparse Attention (DSA):**
Introduced in late 2025, DSA reduces KV-cache memory requirements by up to 57× compared to standard attention. This innovation allowed a 50% price reduction for the API.

**Models in the Client:**

| Model | Version | Context | Max Output | Capabilities |
|-------|---------|---------|------------|--------------|
| `deepseek-chat` | V3.2 (as of 08.03.2026) | 128K Token | 8,192 Token | Text only |
| `deepseek-reasoner` | R1 (as of 08.03.2026) | 128K Token | 64K Token (Thinking) | Text only + CoT |

**DeepThink (R1 Reasoning):**
The `deepseek-reasoner` model uses genuine Chain-of-Thought Reasoning. It "thinks" step by step internally before responding. This makes it significantly better at complex math, logic, and programming tasks, but also slower and more expensive. In the client, this mode is activated via the DeepThink button.

### 2.3 Pricing (as of 08.03.2026)

All prices in USD per 1 million tokens:

| Price Type | deepseek-chat (V3.2) | deepseek-reasoner (R1) |
|------------|----------------------|------------------------|
| **Cache Hit (Input)** | $0.028 | $0.14 |
| **Cache Miss (Input)** | $0.28 | $0.55 |
| **Output** | $0.42 | $2.19 |

**Context Caching:** Requests that share the same prefix (e.g. system prompt) are automatically cached. Cache hits cost 90% less than cache misses. When reusing the same system prompt repeatedly, this is extremely cost-efficient.

**Off-Peak Discount:** Between 16:30–00:30 UTC (approx. 18:30–02:30 CET), discounts of up to 75% (R1) and 50% (V3.2) apply.

**Free Tier:** New API accounts receive 5 million tokens for free (valid for 30 days). No credit card required to register.

**Example Cost:** An average chat session with 100K input tokens and 5K output tokens costs approximately **$0.030** on a cache miss — less than one cent.

### 2.4 Strengths

- **Price-Performance:** Unmatched value compared to GPT-5 ($1.25/M) or Claude Sonnet 4.6 ($3/M)
- **Reasoning Capability (R1):** Competitive with OpenAI o1 at a fraction of the price
- **OpenAI Compatibility:** Drop-in replacement for OpenAI-based code (just swap the base URL)
- **Context Caching:** Automatic, no configuration needed
- **Streaming:** Native SSE support, very low latency to the first token

### 2.5 Weaknesses

- **Text Only:** No image processing, no audio, no video
- **Privacy:** Servers in China; data is processed under Chinese law (see Section 7)
- **Reliability:** The public API has experienced outages in the past due to high demand (especially after major model releases)
- **No Permanent Free Tier:** The 5M free tokens expire after 30 days
- **Umlaut Issue:** The model has a known tendency to handle German special characters inconsistently in long texts (resolved in the client via the Umlaut Placeholder System)

### 2.6 Ideal For

Users who want to process **high request volumes** at **minimal cost** and whose data does not require a high level of privacy protection. Particularly strong for programming tasks, text analysis, translations, and complex reasoning tasks (R1).

---

## 3. Google Gemini

### 3.1 Company Background

Google Gemini is the Large Language Model of Alphabet Inc. (Google). It was introduced in December 2023 as the successor to Google PaLM 2. Google has invested considerable resources in Gemini — it is the AI model used in Google Search, Google Workspace, Android, and numerous other Google products, meaning it is indirectly used by billions of users every day.

Gemini is currently the only provider in this client that offers true **multimodality** — i.e. processing text, images, audio, and video within a single API.

### 3.2 Technology

**Multimodality as Core Competency:**
Gemini was designed from the ground up as a multimodal model. It can not only generate text but also directly understand and analyze images, audio files, and videos. This is a fundamental difference from the other three providers in this client.

**Models in the Client:**

| Model | Version | Context Input | Max Output | Capabilities |
|-------|---------|---------------|------------|--------------|
| `gemini-2.5-flash` | 2.5 Flash (as of 08.03.2026) | 1,048,576 Token | 8,192 Token | Text, Image, Audio, Video |
| `gemini-2.5-pro` | 2.5 Pro (as of 08.03.2026) | 1,048,576 Token | 65,536 Token | Text, Image, Audio, Video |
| `gemini-2.0-flash` | 2.0 Flash (as of 08.03.2026) | 1,048,576 Token | 8,192 Token | Text, Image, Audio, Video |
| `gemini-1.5-pro` | 1.5 Pro (as of 08.03.2026) | 2,097,152 Token | 8,192 Token | Text, Image, Audio, Video |

**Note on Gemini 3.x:**
Since February 2026, Gemini 3.1 Pro and further models of the 3.x series exist. These are not yet configured in this client, but the underlying `google-api.py` is prepared for future extensions.

**Largest Context Window:**
With 1–2 million tokens of context, Gemini is in a category of its own. A context of 1M tokens corresponds to approximately 750,000 words — equivalent to a complete novel, a lengthy legal code, or an entire large software project as an attachment.

### 3.3 Pricing (as of 08.03.2026)

All prices in USD per 1 million tokens (≤200K token input context):

| Model | Input | Output | Free Tier |
|-------|-------|--------|-----------|
| `gemini-2.5-flash` | $0.30 | $2.50 | ✅ 5 RPM / 20 RPD |
| `gemini-2.5-pro` | $1.25 | $10.00 | ❌ |
| `gemini-2.0-flash` | $0.10 | $0.40 | ✅ |
| `gemini-1.5-pro` | $1.25 | $5.00 | ✅ (limited) |

**Important – Long Context Pricing:** When the input context exceeds 200,000 tokens, prices for Pro models double. This is relevant when transferring very large documents.

**Free Tier (permanent):**
Unlike DeepSeek, the Google Free Tier is permanent — it does not expire after 30 days. For `gemini-2.5-flash`: 5 requests/minute and 20 requests/day.

The client has an automatic **429 Rate Limit Retry Logic** implemented: when the limit is reached, the client automatically waits 15 seconds and retries up to 3 times — with a visible countdown in the chat.

**Example Cost (Paid):** 100K input + 5K output with `gemini-2.5-flash` costs approximately **$0.043**. With `gemini-2.5-pro` approximately **$0.175**.

### 3.4 Strengths

- **Only Multimodal Provider in the Client:** Images, audio, video processable (not directly used in the current client configuration for text chats, but available through the API)
- **Massive Context Window:** 1M–2M tokens — ideal for very long documents
- **Permanent Free Tier:** The most generous among all major providers; neither OpenAI nor Anthropic offer a permanent free API tier
- **Google Infrastructure:** High availability, worldwide CDN, SLA
- **GDPR-Compliant:** Data processing in Europe possible (Vertex AI, EU region)
- **Strong Performance:** Gemini 2.5 Pro competes with GPT-5 and Claude Opus on benchmarks

### 3.5 Weaknesses

- **No OpenAI-Compatible Endpoint:** The API uses its own format (`contents` instead of `messages`). In the client, `google-api.py` handles the conversion, but direct portability to other frameworks is more complex
- **Rate Limit Frustration:** The Free Tier is very restricted (20 requests/day). Active users hit the limit quickly
- **Pricing Complexity:** Long-context pricing, multiple model generations, Preview vs. Stable — the pricing structure is more complex than DeepSeek's
- **Consistency:** Some developers report less consistent output for creative and nuanced tasks compared to Claude
- **Rapid Model Deprecation:** Google deprecates models relatively frequently (e.g. Gemini 3 Pro Preview — shutdown announced for 09.03.2026)

### 3.6 Ideal For

Users who want to process **images, audio, or videos**, need very long documents within a single context, or are looking for a **permanently free** quota for occasional use.

---

## 4. Hugging Face

### 4.1 Company Background

Hugging Face is an AI platform founded in New York in 2016, which started as a chatbot company and has grown into the central open-source AI community. With over 500,000 publicly available models, datasets, and demos, Hugging Face is today the "GitHub for AI models".

**Key difference from the other providers:** Hugging Face does not develop its own large language models. Instead, Hugging Face acts as an **aggregator and router** — it provides access to models from Meta (Llama), Mistral, Qwen, Microsoft, Google, and countless others, all through a unified API.

### 4.2 Technology

**Inference Providers (Router Concept):**
Hugging Face operates an OpenAI-compatible router endpoint (`https://router.huggingface.co/v1/chat/completions`) that automatically forwards requests to the fastest and most available inference provider. Over 15 providers are currently integrated (e.g. AWS, Azure, Fireworks AI, SambaNova, Cerebras). Hugging Face charges **no markup** — costs are passed through 1:1 from the provider.

**Models in the Client:**

| Model | Provider | Context | Max Output | Plan | Capabilities |
|-------|----------|---------|------------|------|--------------|
| `Qwen/Qwen2.5-72B-Instruct` | Alibaba | 128K | 8,192 | Free + Paid | Text only |
| `mistralai/Mistral-7B-Instruct-v0.3` | Mistral AI | 32,768 | 4,096 | Free | Text only |
| `microsoft/Phi-3.5-mini-instruct` | Microsoft | 128K | 4,096 | Free | Text only |
| `meta-llama/Meta-Llama-3.1-70B-Instruct` | Meta | 128K | 8,192 | Paid | Text only |
| `meta-llama/Meta-Llama-3.1-405B-Instruct` | Meta | 128K | 8,192 | Paid | Text only |
| `mistralai/Mixtral-8x7B-Instruct-v0.1` | Mistral AI | 32,768 | 4,096 | Paid | Text only |

### 4.3 Pricing (as of 08.03.2026)

**Account Plans:**

| Plan | Cost | Inference Credits |
|------|------|-------------------|
| Free | $0 | Monthly credits (limited) |
| PRO | $9/month | 20× more credits |
| Team | $20/user/month | Shared credits |
| Enterprise | from $50/user/month | Customizable |

**Important:** The monthly credits in the Free Plan are limited. With intensive use, the limit is reached quickly (HTTP 402). The PRO subscription for $9/month provides 20× more credits.

**Token Prices (pass-through, no markup):** Depend on the respective provider. Examples for Llama 3.1 70B: approx. $0.80–$1.00 per 1M tokens depending on provider.

**No Surprises:** Hugging Face shows exactly how much each provider call costs on the billing page.

### 4.4 Strengths

- **Model Variety:** Sole access to a broad range of open-source models (Llama, Mistral, Qwen, Phi) without own infrastructure
- **No Vendor Lock-in:** The router automatically selects the best available provider. If one fails, another takes over
- **Transparent Pricing:** No markup on provider costs — unusually fair
- **Open-Source Ethos:** Those who want to deploy models themselves can download the weights directly (freely available for most models)
- **PRO Plan Very Affordable:** $9/month for 20× more capacity is a good deal
- **Community:** Largest AI community worldwide; model documentation, benchmarks, discussions directly on the platform

### 4.5 Weaknesses

- **Free Tier Limits:** The free credits are sufficient for testing, but not for sustained productive use. Limits are reached without much warning (HTTP 402)
- **Higher Latency:** Since requests go through the router and on to an external provider, latency is higher than with direct APIs. Cold starts for rarely used models can take several seconds (client timeout: 120s)
- **No Own Models:** Hugging Face has no proprietary AI research for frontier models. Quality depends on the third-party models
- **Complexity:** The routing logic is a black box. You don't always know which provider is actually responding
- **Text Only in the Chat Router:** Image processing and other multimodal tasks are not available through the chat completions endpoint

### 4.6 Ideal For

Users who want to explore **open-source models**, want to avoid vendor lock-in with proprietary models, or prefer specific models such as Llama 3.1 or Mistral for their tasks.

---

## 5. GroqCloud

### 5.1 Company Background

Groq was founded in 2016 by Jonathan Ross — a former Google engineer who played a key role in developing the first Google TPU. The company has focused on a single goal: **the fastest AI inference in the world**.

Groq develops and operates **Language Processing Units (LPUs)** — a completely new chip architecture optimized from the ground up for executing LLM inference, not for gaming or graphics like GPUs. The result is an inference speed that surpasses GPU-based systems by a multiple.

### 5.2 Technology

**LPU (Language Processing Unit) — The Unique Selling Point:**
While all other providers rely on NVIDIA GPUs (H100, A100), Groq has developed its own hardware:

- **Deterministic Execution:** No stochastic variation in execution time — every request of the same type takes exactly the same amount of time
- **Integrated SRAM:** Hundreds of MB of SRAM directly on the chip enable extremely fast memory access without the typical GPU bottlenecks
- **Single-Core Architecture:** Tensor parallelism across chips without the synchronization overhead of typical GPU clusters
- **Energy Efficiency:** Up to 10× more efficient than comparable GPU deployments

**Performance Figures (as of 08.03.2026):**
- Up to **1,200 tokens/second** for lightweight models (Llama 3.1 8B)
- Over **400 tokens/second** for Llama 4 and similar sizes
- **Time to First Token:** Frequently under 200ms

For comparison: GPU-based systems typically deliver 40–100 tokens/second for comparable model sizes.

**Models in the Client:**

| Model | Version | Context | Max Output | Capabilities |
|-------|---------|---------|------------|--------------|
| `llama-3.3-70b-versatile` | Llama 3.3 70B (as of 08.03.2026) | 128K | 8,192 | Text only |
| `llama-3.1-8b-instant` | Llama 3.1 8B (as of 08.03.2026) | 131,072 | 8,192 | Text only |
| `mixtral-8x7b-32768` | Mixtral 8x7B v0.1 (as of 08.03.2026) | 32,768 | 32,768 | Text only |
| `gemma2-9b-it` | Gemma 2 9B IT (as of 08.03.2026) | 8,192 | 8,192 | Text only |

Groq does not host proprietary models — all models are open-source weights (Meta Llama, Mistral, Google Gemma) executed on the LPU infrastructure.

### 5.3 Pricing (as of 08.03.2026)

**Account Tiers:**

| Tier | Cost | Notes |
|------|------|-------|
| Free | $0 | Rate limits (tokens/day), no credit card required |
| Developer | Pay-as-you-go | 10× higher rate limits than Free |
| Enterprise | Custom | GroqRack on-premise available |

**Token Prices (Developer Tier):**

| Model | Input | Output |
|-------|-------|--------|
| `llama-3.1-8b-instant` | $0.05/M | $0.08/M |
| `llama-3.3-70b-versatile` | $0.59/M | $0.79/M |
| `mixtral-8x7b-32768` | $0.24/M | $0.24/M |
| `gemma2-9b-it` | $0.20/M | $0.20/M |

**Special Features:**
- **Batch API:** 50% discount for asynchronous processing (24h–7 day processing window)
- **Prompt Caching:** 50% discount on cached input tokens
- **Free Tier:** Permanently free with rate limits — no expiry date

**Technical Note:** A `User-Agent` HTTP header is mandatory because the Groq API sits behind Cloudflare. Without the correct header, the request is rejected with error code 1010. In the client, this is correctly implemented in `groq-api.py`.

### 5.4 Strengths

- **Unmatched Speed:** 400–1,200 tokens/second — no other API provider comes anywhere close. Responses feel literally "instant"
- **Low Price for Small Models:** `llama-3.1-8b-instant` at $0.05/M input is extremely affordable at high speed
- **Permanent Free Tier:** No expiry date, no credit card required
- **OpenAI Compatible:** Drop-in replacement for OpenAI code
- **Deterministic Behavior:** Consistent response times, no "cold/warm" effect as with serverless GPUs
- **SOC 2, GDPR, HIPAA:** Enterprise compliance available

### 5.5 Weaknesses

- **Open-Source Models Only:** No proprietary frontier models like GPT-5, Claude, or Gemini. Sufficient for many tasks, but the absolute quality ceiling is missing
- **Inference Only:** No fine-tuning, no training, no embeddings, no DALL-E — purely specialized for inference
- **Text Only (in this client):** Groq also supports Speech-to-Text (Whisper) and TTS, but not through the endpoint configured in this client
- **Limited Context Window:** Maximum 131K tokens (Llama 3.1 8B), significantly smaller than Gemini's 1M+
- **Limited Model Selection:** Fewer models than Hugging Face; no proprietary reasoning models

### 5.6 Ideal For

Users who prioritize **maximum speed** — for interactive applications, live chats, rapid brainstorming, and all cases where waiting is disruptive. Also for users looking for a permanently free quota for occasional use.

---

## 6. Decision Matrix — Who Should Choose What?

### By Use Case

| Use Case | Recommendation | Reason |
|----------|----------------|--------|
| **Analyze images / audio / video** | Google Gemini | Only provider with true multimodality |
| **Complex math / logic** | DeepSeek R1 | Best price-performance ratio for reasoning |
| **Very long documents** | Google Gemini | 1–2M token context, no alternative |
| **Maximum speed** | GroqCloud | 400–1,200 tokens/sec — unmatched |
| **Minimum cost** | DeepSeek | Cheapest price per token on the market |
| **Open-source models** | Hugging Face | Llama, Mistral, Qwen — broad selection |
| **Permanently free** | Google (Free) or GroqCloud | Both offer unlimited free tiers |
| **Privacy (EU/GDPR)** | Google Gemini (EU region) | Clear GDPR compliance possible |
| **Experimentation / Learning** | GroqCloud or HF | Both free to start, straightforward |
| **High-load production** | DeepSeek or GroqCloud | Best cost efficiency at scale |

### By Priority

**I just want fast answers:**
→ **GroqCloud** (`llama-3.1-8b-instant`) — fastest inference, free, ready to use immediately.

**I want the best answers, cost no object:**
→ **Google Gemini** (`gemini-2.5-pro`) or **DeepSeek** (`deepseek-reasoner`) — both at world-class level, but for different task types.

**I want to pay as little as possible:**
→ **DeepSeek** (`deepseek-chat`) — with context caching and off-peak hours, this is the cheapest frontier AI in the world.

**I don't want to use proprietary models:**
→ **Hugging Face** or **GroqCloud** — both are based exclusively on open-source weights.

**I want to analyze images, PDFs, or videos:**
→ **Google Gemini** — the only option in this client.

---

## 7. Privacy and Legal Aspects

This overview aims to inform objectively and without bias. Privacy is a relevant decision criterion.

### DeepSeek
- Server location: **China** (People's Republic)
- Applicable law: Chinese law, incl. National Intelligence Law (2017)
- The law may obligate Chinese companies to cooperate with authorities under certain circumstances
- **Recommendation:** Often acceptable for personal or non-sensitive data. Caution is advised for corporate data, health data, or privacy-regulated information (GDPR)
- DeepSeek offers the `X-No-Training` header (implemented in the client), signaling that data should not be used for training — however, binding guarantees are difficult to verify

### Google Gemini
- Server location: **USA** and other Google Cloud regions (incl. EU possible via Vertex AI)
- Applicable law: US law; GDPR-compliant deployment possible via Vertex AI in the EU region
- SOC 2, ISO 27001, HIPAA (Vertex AI)
- **Recommendation:** Well-suited for EU projects when Vertex AI is used with the EU region. The Google AI Studio endpoint used in this client (without Vertex AI) is subject to Google's standard privacy terms

### Hugging Face
- Server location: **USA** (headquarters) with partners worldwide
- Actual data processing takes place at the respective inference providers (AWS, Azure, etc.) — privacy law situation is heterogeneous
- **Recommendation:** Well-suited for tests and non-sensitive data. For regulated data, it should be checked which provider is responding in each individual case

### GroqCloud
- Server location: **USA** with data centers in North America, Europe, Middle East, Asia-Pacific
- Compliance: **SOC 2, GDPR, HIPAA**
- Zero Data Retention available (requests are not stored)
- **Recommendation:** The most transparent of the four providers with regard to compliance. HIPAA suitability is a clear enterprise signal

---

## 8. Conclusion

All four providers are fully-featured, professional LLM services. There is no clear "winner" — each has its specific sweet spot:

**DeepSeek** is the choice for maximum cost efficiency and strong reasoning capabilities. Those who produce a lot pay the least here. The privacy topic (China) is real and must be evaluated individually.

**Google Gemini** is the choice for multimodal tasks (image, audio, video), very long contexts, and the best permanent free tier. Google's infrastructure is reliable and configurable for GDPR compliance.

**Hugging Face** is the choice for everyone who wants to explore open-source models without risking vendor lock-in. The broad model selection and the transparent pass-through pricing are unique.

**GroqCloud** is the choice for maximum speed. Those who build interactive applications or simply dislike waiting will be impressed by the LPU-accelerated inference. SOC 2 and HIPAA compliance also make it interesting for enterprise applications.

**Practical Recommendation for New Users:**
Start with **GroqCloud Free** (free, fast, ready immediately) or **Google Gemini Free Tier** (permanent, multimodal). Once you hit the limits or have specific requirements, decide purposefully using this overview.

---

*Created: 08.03.2026 | For the Multi-LLM Chat Client github.com/debian-professional/private-chatboot*
