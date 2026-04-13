# Vibe Architect

**AI-powered prompt builder for vibe-coding platforms.** Answer 14 questions about your app idea — Vibe Architect produces a complete, structured AI coding prompt ready to paste into Replit, Bolt, Lovable, v0, Cursor, or Emergent.

**Cost:** ~$0.003 per session · **LLM calls:** exactly 2 per session · **Offline NLP:** runs on CPU, no GPU required

---

## How It Works

```
User answers 14 questions
        ↓
Layer 1: Deterministic FSM conversation engine
        ↓
LLM Call 1: Extract structured product context (Groq, temp=0.1)
        ↓
Layer 2: Rule-based preview engine (screens, flows, wireframes — no LLM)
        ↓
LLM Call 2: Narrative synthesis (product identity, user stories, edge cases)
        ↓
Layer 3: Jinja2 template compiler → 12-section prompt
        ↓
Output: Platform-specific prompt for Replit / Bolt / Lovable / v0 / Cursor / Emergent
```

**v3.0 additions:** Emergent platform adapter + 6-module offline NLP layer (DistilBERT, spaCy, RoBERTa, DistilBART, MiniLM, textstat) that pre-processes answers to improve extraction quality.

---

## Quick Start — Groq Cloud (Recommended)

> Requires: Docker + Docker Compose. Get a free Groq API key at [console.groq.com](https://console.groq.com) — no credit card needed.

```bash
# 1. Clone the repo
git clone <repo-url> && cd vibe-architect

# 2. Set up environment
cp .env.example .env
# Edit .env and set: GROQ_API_KEY=gsk_...

# 3. Build and start (first run downloads ~913MB of NLP models)
docker compose up --build

# 4. Open the app
open http://localhost:3000
```

**First build time:** 5–10 minutes (downloads NLP models once, cached in Docker volume). Subsequent starts take ~10 seconds.

**API docs:** http://localhost:8000/docs

---

## Quick Start — Ollama Local (Zero Cost)

> Requires: Docker + Ollama. Best for M-series Mac or NVIDIA GPU.

```bash
cp .env.example .env
# Leave GROQ_API_KEY empty

docker compose -f docker-compose.yml -f docker-compose.ollama.yml up --build
# Ollama will pull llama3.1:8b automatically (~4.7GB)
```

---

## Development Setup (No Docker)

Run the backend and frontend separately with hot-reload.

### Backend

```bash
cd backend

# Create a virtual environment
python3 -m venv venv && source venv/bin/activate

# Install dependencies
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Copy and configure environment
cp ../.env.example .env
# Set GROQ_API_KEY=gsk_... in .env

# Skip NLP model download for fast dev (uses regex fallback)
echo "ENABLE_NLP_LAYER=false" >> .env

# Start Redis (required for session storage)
docker run -d -p 6379:6379 redis:7-alpine

# Run the backend
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

npm install
npm run dev
# → http://localhost:3000
```

The frontend Vite dev server proxies `/api` and `/health` to `http://localhost:8000` automatically.

---

## Running Tests

```bash
cd backend
source venv/bin/activate  # if using venv

# Fast tests (no NLP models needed) — all FSM, extraction, compiler, fallback NLP
ENABLE_NLP_LAYER=false pytest tests/ -v
# Runs in < 30 seconds

# All tests including NLP model tests (requires models downloaded)
ENABLE_NLP_LAYER=true pytest tests/ -v
```

### Test coverage by spec

| Test ID | Description | Requires models |
|---------|-------------|-----------------|
| TC-FSM-01 | FSM advances IDEA→TOUCHPOINTS after 3 answers | No |
| TC-FSM-02 | Vague answer returns probe question | No |
| TC-FSM-03 | 9+ word answer classified as ADEQUATE | No |
| TC-FSM-04 | trigger_extraction fires after Q14 | No |
| TC-FSM-05 | FSM never calls LLM during conversation | No |
| TC-EXT-01 | Call 1 payload contains all 14 Q&A turns + schema | No |
| TC-EXT-02 | Extractor parses JSON into EnrichedContext | No |
| TC-EXT-03 | ExtractionError raised on malformed JSON | No |
| TC-EXT-04 | RICE score > 0 for all must-have features | No |
| TC-EXT-05 | Persona matrix has N×M entries | No |
| TC-EMR-01 | Emergent adapter has DESIGN_INTENT + ENHANCEMENT_LAYER | No |
| TC-EMR-02 | Emergent adapter excludes API_CONTRACTS + BUILD_SEQUENCE | No |
| TC-EMR-03 | design_intent.j2 renders booking mood | No |
| TC-EMR-04 | enhancement_layer.j2 includes mobile instructions | No |
| TC-EMR-05 | Emergent prompt stays under 6000 tokens | No |
| TC-NLP-01 | ADEQUATE for 12-word concrete answer | No |
| TC-NLP-02 | VAGUE for "I don't know" | No |
| TC-NLP-03 | EntityExtractor finds Stripe + admin | Yes |
| TC-NLP-04 | Sentiment → kano_hint=basic for negative | Yes |
| TC-NLP-05 | Sentiment → kano_hint=delighter for positive | Yes |
| TC-NLP-06 | DomainDetector → booking for salon app | Yes |
| TC-NLP-07 | FeatureDeduplicator merges messaging features | Yes |
| TC-NLP-08 | Expertise signal > 0 after expert answers | No |
| TC-NLP-11 | NLPPipeline falls back to regex on error | No |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `groq` | LLM backend: `groq` \| `ollama` \| `openai` \| `anthropic` |
| `GROQ_API_KEY` | — | Groq API key from console.groq.com |
| `GROQ_MODEL` | `llama-3.1-70b-versatile` | Do not change for cloud |
| `OLLAMA_URL` | `http://ollama:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3.1:8b` | Ollama model name |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `SESSION_BACKEND` | `redis` | `redis` or `memory` (dev only) |
| `REDIS_URL` | `redis://redis:6379` | Redis connection string |
| `ENABLE_NLP_LAYER` | `true` | `false` = skip all NLP, use regex fallback |
| `MODEL_CACHE_DIR` | `/models` | Path for downloaded NLP models |
| `ENABLE_NLP_LAYER` | `true` | Disable for lightweight dev |
| `NLP_DEDUP_SIMILARITY_THRESHOLD` | `0.85` | Cosine similarity threshold for feature dedup |
| `EMERGENT_PROMPT_MAX_TOKENS` | `6000` | Token cap for Emergent prompts |
| `RATE_LIMIT_SESSIONS_PER_IP_PER_HOUR` | `3` | Abuse prevention |
| `DAILY_COST_ALERT_USD` | `10.00` | Log warning at this daily spend |
| `APP_ENV` | `development` | `development` or `production` |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |

---

## API Reference

All endpoints at `http://localhost:8000`. Interactive docs at `/docs`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/sessions` | Create session, returns first question |
| `GET` | `/api/v1/sessions/{id}` | Get session state + cost tracking |
| `POST` | `/api/v1/enrichment/answer` | Submit answer → SSE stream of events |
| `POST` | `/api/v1/preview/{session_id}` | Generate screens, flows, wireframes |
| `POST` | `/api/v1/compile/{session_id}/{platform}` | Compile 12-section prompt |
| `GET` | `/health` | Health check |
| `GET` | `/health/nlp` | NLP model load status |

### SSE Events (from `/enrichment/answer`)

| Event | Data | Meaning |
|-------|------|---------|
| `question` | `{text, quick_replies, phase, progress_pct}` | Next question |
| `probe` | `{text}` | Follow-up for vague answer |
| `phase_advance` | `{new_phase, progress_pct, label}` | Phase transition |
| `extracting` | `{}` | LLM Call 1 in progress |
| `extracted` | `{complexity_score}` | Call 1 complete |
| `error` | `{code, message}` | Error occurred |

### Platforms

`replit` · `bolt` · `lovable` · `v0` · `cursor` · `emergent`

---

## Architecture

```
vibe-architect/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI app + lifespan
│   │   ├── config.py            ← All settings from env
│   │   ├── models/              ← All Pydantic models
│   │   ├── api/v1/              ← REST endpoints
│   │   └── core/
│   │       ├── enrichment/
│   │       │   ├── adapters/    ← Groq, Ollama, OpenAI, Anthropic, Mock
│   │       │   ├── fsm/         ← 14-question state machine
│   │       │   ├── extraction/  ← LLM Call 1 (JSON extraction)
│   │       │   ├── scoring/     ← RICE, persona matrix, UX flags
│   │       │   └── nlp/         ← 6-module offline NLP (v3.0)
│   │       ├── preview/         ← Screen derivation, flows, SVG wireframes
│   │       └── compiler/        ← Jinja2 templates + LLM Call 2 + platform adapters
│   ├── tests/                   ← Pytest unit tests
│   └── scripts/                 ← Model download script
└── frontend/
    └── src/
        ├── features/
        │   ├── intake/          ← FSM chat UI with SSE
        │   ├── preview/         ← SVG wireframes, flows, complexity
        │   └── compiler/        ← 12-section prompt with platform tabs
        ├── lib/                 ← API client, Zustand store
        └── components/          ← Shared UI components
```

### Cost Model

| Call | Model | Tokens | Cost |
|------|-------|--------|------|
| Call 1 (extraction) | llama-3.1-70b-versatile | ~2,500 | ~$0.0015 |
| Call 2 (narrative) | llama-3.1-70b-versatile | ~2,800 | ~$0.0017 |
| **Total per session** | | **~5,300** | **~$0.003** |

Groq free tier: ~1,785 sessions/day within 500K token/day limit.

---

## NLP Layer (v3.0)

| Module | Model | Size | Purpose |
|--------|-------|------|---------|
| M1: Answer Quality | DistilBERT (SST-2) | 67MB | Classifies answer substantiveness |
| M2: NER | spaCy en_core_web_sm | 12MB | Extracts personas, tools, integrations |
| M3: Sentiment | RoBERTa (Cardiff) | 499MB | Pre-classifies features as Kano basic/delighter |
| M4: Domain | DistilBART MNLI | 255MB | Detects app domain for design intent |
| M5: Deduplication | all-MiniLM-L6-v2 | 80MB | Merges semantically duplicate features |
| M6: Readability | textstat | <1MB | Expert user detection, complexity signal |

All models run on CPU in-process. Total model cache: ~913MB. Downloaded once at Docker build time.

Disable with `ENABLE_NLP_LAYER=false` for lightweight development.

---

## License

Open source. Spec v2.0 + v3.0 — Vibe Architect Prompt Intelligence Engine.
