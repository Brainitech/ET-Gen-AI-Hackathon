#!/bin/bash
# aether_ai — One-command startup
# Usage: ./run.sh

set -e

echo "⚡ aether_ai — AI-Native Business News"
echo "──────────────────────────────────────"

# Copy .env if not present
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Download spaCy model if needed
python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null || \
    python -m spacy download en_core_web_sm

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting backend on http://localhost:8000 ..."
echo "   (Open another terminal and run: streamlit run streamlit_app.py)"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
