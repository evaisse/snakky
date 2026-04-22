# Snakky - IA Chat with Reflex

Minimal chat app powered by **Reflex** (Python framework) + **SQLite** (persisted via Railway volume) + **OpenRouter** LLM.

## Setup

```bash
# Install deps
pip install -r requirements.txt

# Create .env from .env.example
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY

# Init DB + run local
python -c "from snakky.db import init_db; import asyncio; asyncio.run(init_db())"
reflex run
```

Visit `http://localhost:3000`

## Deployment (Railway)

1. **Push to GitHub**
2. **Create Railway project** from Dockerfile
3. **Add volume**: Mount `/data` for persistent SQLite storage
4. **Add secrets**: `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`
5. **Deploy**

The app will:
- Persist conversations in `/data/aiktivist.db`
- Stream responses from OpenRouter
- Serve Reflex frontend on port 3000

## Structure

```
snakky/
├── db.py          # SQLite helpers (conversations, messages)
├── llm.py         # OpenRouter streaming
└── snakky.py      # Reflex app & UI
```
