# — AI-Native Business News Engine

> Built for the Economic Times Gen AI Hackathon · Round 2

_ai transforms how business professionals consume news. Instead of a static, one-size-fits-all homepage, it delivers a fundamentally different experience for every reader — one that understands who you are, what you do, and what the news means \_for you specifically_.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Workflow](#workflow)
- [Tech Stack](#tech-stack)
- [API Reference](#api-reference)
- [Running Locally](#running-locally)
- [Demo](#demo)

---

## Overview

is a full-stack AI news platform built on live Economic Times RSS feeds. It exposes five distinct intelligent features through a FastAPI backend and a unified Streamlit frontend that brings together the personalized newsroom, story intelligence, summarization, and vernacular translation under one surface.

The core thesis: the same piece of news means entirely different things to a retail investor, a startup founder, a student, and a corporate executive. operationalizes that insight at every layer — from article retrieval to AI-generated contextual commentary.

All features run on a fully local, zero-cost LLM stack via Ollama, with optional Groq cloud acceleration through a single environment variable.

---

## Features

### My ET — The Personalized Newsroom

A persona-driven news feed that goes beyond topic filtering. After a one-time onboarding where the user declares their role and context, every article in their feed is enriched with a 1–2 sentence AI snippet explaining what that specific story means for _them_ — referencing their sector, stage, holdings, or strategic priorities.

Four personas are supported, each with a distinct context schema:

- **Investor** — portfolio sectors, tracked stocks, risk appetite, investment style
- **Founder** — startup sector, funding stage, fundraising status, competitors to watch
- **Student** — field of study, career goal, knowledge level
- **Executive** — industry, function, company size, strategic focus areas

Each persona gets persona-specific Deep Dive sections (e.g. an investor sees "Market & Portfolio Impact" and "Action Points for Investors"; a student sees "What Happened in Plain English" and "Key Terms Explained").

### Story Arc Tracker

Enter any business topic — a company, a policy, a market event — and receive a complete narrative intelligence brief: a chronological event timeline, key players extracted via NLP, per-article sentiment scores visualized on an interactive chart, a contrarian perspective, and forward-looking predictions. The system uses a hybrid retrieval strategy: a local SQLite semantic vector cache is checked first, with live RSS fallback when coverage is thin.

### News Summarizer

A map-reduce summarization pipeline built for long-form articles. Articles are chunked along sentence boundaries (via spaCy), each chunk is processed in parallel by the LLM to extract facts, and a final consolidation pass synthesizes a 3-sentence narrative summary, 5 actionable key takeaways, and a contextual impact statement.

### Vernacular Business News Engine

A two-pass translation pipeline for Hindi, Tamil, Telugu, and Bengali. Critical financial acronyms (RBI, SEBI, GDP, NIFTY, etc.) are protected via entity tagging before translation to prevent malformed output. A base literal translation is produced in parallel chunks, then a refinement pass post-processes the full text into fluent journalistic prose, adds a local cultural context note, and extracts a terminology glossary with native-script translations and English explanations.

### Background Ingestion Worker

A persistent async worker that polls RSS feeds every 30 minutes, extracts full article text via a Trafilatura + Playwright hybrid pipeline, runs spaCy NER and VADER sentiment scoring, generates vector embeddings via Ollama, and stores results in a local SQLite semantic index. This powers the low-latency vector search that underpins the Story Arc Tracker's cache layer.

---

## System Architecture

```
/
├── app/
│   ├── main.py                        # FastAPI application root, router registration
│   ├── core/
│   │   ├── config.py                  # Settings, LLM client factory (Ollama / Groq)
│   │   └── database.py                # ChromaDB singleton client and collection helpers
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── my_et_extended.py  # My ET: profile save, briefing, snippet, deep dive
│   │           ├── story_arc.py       # Story Arc Tracker endpoint
│   │           ├── summarizer.py      # News Summarizer endpoint
│   │           ├── vernacular.py      # Vernacular Engine endpoint
│   │           └── articles.py        # Article search and fetch utility endpoints
│   ├── models/
│   │   ├── schemas.py                 # Core Pydantic v2 schemas (all features)
│   │   └── my_et_schemas.py           # Extended My ET schemas and persona context models
│   └── services/
│       ├── rss_service.py             # ET RSS fetcher, in-memory cache, hybrid extractor
│       ├── my_et_service.py           # ChromaDB ingestion and vector-similarity feed
│       ├── my_et_ai_service.py        # Persona snippet, deep dive, and briefing pipeline
│       ├── story_arc_service.py       # VADER + spaCy NER + LLM narrative generation
│       ├── summarizer_service.py      # Map-reduce chunk summarization pipeline
│       ├── vernacular_service.py      # Entity protection, base translate, refinement pass
│       └── ingestion_service.py       # Async background worker: RSS → NLP → SQLite index
├── streamlit_app.py                   # Unified Streamlit frontend (all features including My ET)
├── news_archive.db                    # SQLite semantic index (auto-created on first run)
├── test_pipeline.py                   # Extraction pipeline smoke test
├── run.sh                             # Convenience startup script
├── requirements.txt
└── .env                               # API keys and config (see Running Locally)
```

**Data flow summary:**

```
                         ET RSS Feeds (5 category feeds)
                                      |
                          +-----------+-----------+
                          |                       |
                    (live fetch)            (background poll)
                          |                       |
                          v                       v
               rss_service.py           ingestion_service.py
                          |                       |
                          |               [spaCy NER + VADER]
                          |               [Ollama Embeddings]
                          |                       |
                          |               SQLite Semantic Index
                          |                       |
                          +----------+------------+
                                     |
                                     v
                          FastAPI Endpoint Layer
                                     |
               +----------+----------+----------+----------+
               |          |          |          |          |
               v          v          v          v          v
           my_et_     story_arc_ summar-    vernac-    articles
           extended   service    izer_      ular_      (search /
           .py                   service    service     fetch)
               |          |          |          |
           [LLM:      [VADER +   [parallel  [entity
            persona    spaCy +    map-       protect +
            snippets   LLM arc]   reduce     dual-pass
            deep dive]            LLM]       LLM]
               |          |          |          |
               +----------+----------+----------+
                                     |
                                     v
                         streamlit_app.py
                    (Unified Frontend — all features)
```

---

## Workflow

### My ET — End-to-End

1. User completes onboarding: selects a persona and fills in their context (sectors, stocks, stage, etc.).
2. The frontend `POST`s an `ExtendedUserProfile` to `/api/v1/my-et/profile/extended`. If interests are empty, they are auto-derived from the persona context.
3. The frontend `GET`s `/api/v1/my-et/briefing/{user_id}`.
4. The service queries ET RSS feeds via keyword search against the user's interests, falls back to the full feed if no matches.
5. The top 5 articles are enriched synchronously: for each, a prompt containing the article and the user's plain-English context summary is sent to the LLM, which returns a 1–2 sentence persona snippet.
6. The remaining articles are returned with `snippet_ready: false` for on-demand lazy loading via `/api/v1/my-et/snippet`.
7. For any article, the user can trigger a Deep Dive via `POST /api/v1/my-et/deep-dive`, which returns 4 persona-specific analysis sections and a single bottom-line takeaway.

### Story Arc Tracker — End-to-End

1. User submits a topic string.
2. The service checks the local SQLite vector index (semantic cosine similarity against Ollama-generated embeddings). If fewer than 3 matches are found, it falls back to live RSS keyword search.
3. Live articles are fetched in parallel using `ThreadPoolExecutor` via the Trafilatura + Playwright hybrid extractor.
4. VADER sentiment is scored per article.
5. spaCy NER extracts persons and organisations from the combined article text.
6. An LLM prompt containing numbered, date-annotated article excerpts is sent with a strict JSON schema. The response is validated through Pydantic before returning.
7. NER-extracted entities not already in the LLM's key players list are merged in.

### News Summarizer — End-to-End

1. Input arrives as raw text or a URL (which is scraped via `fetch_article_text`).
2. The text is split into semantically coherent chunks (spaCy sentence boundaries, max 3000 characters).
3. Chunks are processed in parallel via `ThreadPoolExecutor`: each chunk is sent to the LLM with a fact-extraction prompt.
4. All chunk-level fact lists are consolidated in a single reduce-phase LLM call that produces the final JSON output.
5. The response is validated via `SummarizerSchema` (Pydantic). On failure, an extractive keyword-frequency fallback is used.

### Vernacular Engine — End-to-End

1. Financial acronyms and proper nouns are replaced with numbered placeholder tags (`__ENT_1__`, etc.).
2. The protected text is chunked along sentence boundaries.
3. Base literal translation of each chunk is performed in parallel threads.
4. Chunks are joined and sent to a refinement LLM call with the original entity mapping restored. This call produces fluent prose, a cultural context note, and a terminology glossary.
5. All outputs are validated via `VernacularSchema` (Pydantic).

---

## Tech Stack

| Layer                | Technology                              | Role                                                              |
| -------------------- | --------------------------------------- | ----------------------------------------------------------------- |
| Backend Framework    | FastAPI                                 | REST API, async lifespan, CORS                                    |
| Frontend             | Streamlit                               | Unified UI — My ET, Story Arc, Summarizer, Vernacular             |
| Local LLM            | Ollama (llama3.1:8b default)            | All generative tasks — zero cost, no API key                      |
| Cloud LLM (optional) | Groq (llama3-8b-8192)                   | Drop-in replacement via `GROQ_API_KEY`                            |
| LLM Client           | openai (Python SDK)                     | Unified client for both Ollama and Groq via OpenAI-compatible API |
| Vector Store         | ChromaDB (persistent)                   | Article embeddings for My ET similarity retrieval                 |
| Semantic Index       | SQLite + custom embeddings              | Story Arc vector cache, background ingestion                      |
| Embeddings           | Sentence Transformers                   | `all-MiniLM-L6-v2` for My ET article embeddings                   |
| NLP                  | spaCy (`en_core_web_sm`)                | Named entity recognition, sentence boundary detection             |
| Sentiment Analysis   | VADER (vaderSentiment)                  | Per-article sentiment scoring in Story Arc                        |
| Web Scraping         | Trafilatura + Playwright                | Hybrid full-text extraction, Playwright handles JS-rendered pages |
| RSS Parsing          | feedparser                              | ET feed ingestion across 5 category feeds                         |
| Data Validation      | Pydantic v2                             | All request/response and internal schema validation               |
| Concurrency          | `concurrent.futures.ThreadPoolExecutor` | Parallel LLM map phases in Summarizer and Vernacular              |
| Async Worker         | `asyncio.to_thread`                     | Non-blocking background ingestion in FastAPI lifespan             |
| Configuration        | pydantic-settings + python-dotenv       | Environment-driven config with sane defaults                      |
| Charts               | Plotly                                  | Interactive sentiment visualization in Story Arc                  |

---

## API Reference

### My ET

| Method | Endpoint                           | Description                                               |
| ------ | ---------------------------------- | --------------------------------------------------------- |
| `POST` | `/api/v1/my-et/profile/extended`   | Save extended user profile with persona context           |
| `GET`  | `/api/v1/my-et/briefing/{user_id}` | Fetch AI-enriched personalized news briefing              |
| `POST` | `/api/v1/my-et/snippet`            | Generate persona snippet for a single article (lazy load) |
| `POST` | `/api/v1/my-et/deep-dive`          | Full 4-section contextual breakdown of one article        |

### Story Arc Tracker

| Method | Endpoint            | Description                             |
| ------ | ------------------- | --------------------------------------- |
| `POST` | `/api/v1/story-arc` | Generate complete story arc for a topic |

### News Summarizer

| Method | Endpoint            | Description                        |
| ------ | ------------------- | ---------------------------------- |
| `POST` | `/api/v1/summarize` | Summarize article from text or URL |

### Vernacular Engine

| Method | Endpoint                      | Description                                        |
| ------ | ----------------------------- | -------------------------------------------------- |
| `POST` | `/api/v1/translate`           | Translate text to Hindi, Tamil, Telugu, or Bengali |
| `GET`  | `/api/v1/translate/languages` | List supported language codes and metadata         |

### Utilities

| Method | Endpoint                         | Description                                    |
| ------ | -------------------------------- | ---------------------------------------------- |
| `GET`  | `/api/v1/articles/search`        | Keyword search across ET RSS feeds             |
| `GET`  | `/api/v1/articles/fetch`         | Scrape and return full article text from a URL |
| `GET`  | `/api/v1/articles/pipeline_test` | Run hybrid extractor on one article per feed   |
| `GET`  | `/health`                        | Application health check                       |

Full interactive documentation is available at `http://localhost:8000/docs` when the backend is running.

---

## Running Locally

### Prerequisites

- Python 3.9 or higher (project developed on 3.13)
- [Ollama](https://ollama.com) installed and running locally
- Playwright browser binaries (installed separately after pip)

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd <repo-name>

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browser binaries
playwright install

# 5. Download the spaCy language model (one-time)
python -m spacy download en_core_web_sm

# 6. Pull the local LLM (one-time, ~5GB)
ollama pull llama3.1:8b
```

### Environment Configuration

Create a `.env` file in the project root. All fields have sane defaults — the only variable that meaningfully changes runtime behaviour is `GROQ_API_KEY`:

```env
# Optional: set this to use Groq cloud instead of local Ollama
GROQ_API_KEY=

# Ollama settings (defaults shown)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.1:8b

# ChromaDB persistence directory
CHROMA_PERSIST_DIR=./chroma_db
```

### Running

Two terminal sessions are required:

```bash
# Terminal 1 — FastAPI Backend
uvicorn app.main:app --reload
# API docs available at: http://localhost:8000/docs

# Terminal 2 — Streamlit Frontend
streamlit run streamlit_app.py
# Open: http://localhost:8501
```

### Verify Installation

```bash
# Check backend health
curl http://localhost:8000/health

# Run the extraction pipeline test (fetches 1 article per feed)
python test_pipeline.py
```

---

## Demo

<!--Upcoming Demo -->

![ Demo](./ET_DEMO_Final.gif)
▶️ [Watch Demo Video](https://drive.google.com/file/d/1SNUUMFskFPoWsfDVWKeAQFaBv6sMQ8Da/view?usp=sharing)
