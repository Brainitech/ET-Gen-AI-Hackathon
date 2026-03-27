
### ET Hackathon Round 2 | 100% Free & Open Source

Three AI-powered features built on live Economic Times RSS feeds:

| Feature | What it does |
|---------|-------------|
| 🗺️ **Story Arc Tracker** | Visual narrative — timeline, key players, sentiment, contrarian views, predictions |
| 📰 **News Summarizer** | 3-sentence AI digest + 5 key takeaways from any article |
| 🌐 **Vernacular Engine** | Culturally-adapted Hindi/Tamil/Telugu/Bengali translation with local context |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com) installed and running

```bash
# Pull the LLM (only once)
ollama pull llama3.1:8b
```

### Run

```bash
cd aether_ai

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (only once)
python -m spacy download en_core_web_sm

# Terminal 1 — Backend API
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs

# Terminal 2 — Streamlit Frontend
streamlit run streamlit_app.py
# Open: http://localhost:8501
```

---

## 🛠️ Architecture

```
aether_ai/
├── requirements.txt              # All free dependencies
├── .env.example                  # Config template (no secrets needed)
├── run.sh                        # One-command startup
├── streamlit_app.py              # Premium dark-themed UI
└── app/
    ├── main.py                   # FastAPI root (3 routers)
    ├── core/config.py            # Ollama/Groq auto-detection
    └── services/
        ├── rss_service.py        # Shared: ET RSS fetcher (5-min cache)
        ├── story_arc_service.py  # VADER + spaCy + LLM narrative
        ├── summarizer_service.py # LLM summary + extractive fallback
        └── vernacular_service.py # Google Translate + LLM post-process
```

## 🔑 API Endpoints

```
POST /api/v1/story-arc      {"topic": "Adani Group"}
POST /api/v1/summarize      {"text": "...", "url": "..."}
POST /api/v1/translate      {"text": "...", "target_lang": "hi|ta|te|bn"}
GET  /api/v1/translate/languages
GET  /health
GET  /docs
```

## 💡 LLM Configuration

By default uses **local Ollama** (no API key needed). To use Groq cloud instead:

```bash
# .env
GROQ_API_KEY=your_key_here
```

The app auto-detects which one to use — no code changes needed.

---

## Tech Stack

- **FastAPI** — Backend API
- **Streamlit** — Frontend
- **Ollama llama3.1:8b** — Local LLM (zero cost, zero API key)
- **vaderSentiment** — Sentiment analysis
- **spaCy en_core_web_sm** — Named entity recognition
- **deep-translator** — Google Translate (free, no key)
- **feedparser** — ET RSS feeds
- **Plotly** — Interactive charts
