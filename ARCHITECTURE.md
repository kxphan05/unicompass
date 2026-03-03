# UniAdvisor — System Architecture Map

**Version:** 1.0 — MVP  
**Stack Philosophy:** Free-tier first. No paid infrastructure until you have users.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                               │
│                                                                     │
│   ┌──────────────────────┐       ┌──────────────────────────────┐  │
│   │     Web App          │       │       Mobile App             │  │
│   │  Next.js (Vercel)    │       │  Expo + React Native         │  │
│   │  Free tier           │       │  Free (build locally)        │  │
│   └──────────┬───────────┘       └──────────────┬───────────────┘  │
│              │                                   │                  │
└──────────────┼───────────────────────────────────┼──────────────────┘
               │            HTTPS + SSE            │
┌──────────────┼───────────────────────────────────┼──────────────────┐
│              ▼          BACKEND LAYER             ▼                  │
│                                                                      │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │              FastAPI  (Railway — free tier)                  │  │
│   │                                                              │  │
│   │   /api/profile        /api/debate/start                     │  │
│   │   /api/debate/stream  /api/debate/question                  │  │
│   │   /api/scholarships   /api/debate/summary                   │  │
│   └────────┬─────────────────────┬────────────────┬─────────────┘  │
│            │                     │                │                 │
└────────────┼─────────────────────┼────────────────┼─────────────────┘
             │                     │                │
     ┌───────▼───────┐   ┌─────────▼──────┐  ┌─────▼──────────────┐
     │  Agent Layer  │   │   Database     │  │   File Storage     │
     │  (same host)  │   │  Supabase      │  │  Supabase Storage  │
     │               │   │  (free tier)   │  │  (free tier, 1GB)  │
     │  NUS Agent    │   │                │  │                    │
     │  NTU Agent    │   │  PostgreSQL    │  │  PDF uploads       │
     │  SMU Agent    │   │  Auth built-in │  │  Transcripts       │
     │  SUSS Agent   │   │                │  │                    │
     │  SUTD Agent   │   └────────────────┘  └────────────────────┘
     │  SIT Agent    │
     │  Judge Agent  │
     └───────┬───────┘
             │
     ┌───────▼──────────────────────────────────────────┐
     │              EXTERNAL SERVICES                    │
     │                                                   │
     │  ┌─────────────────┐   ┌───────────────────────┐ │
     │  │  OpenRouter API  │   │  Scraping             │ │
     │  │  (pay per token  │   │  Playwright on        │ │
     │  │  ~$0.001/debate) │   │  Railway instance     │ │
     │  └─────────────────┘   └───────────────────────┘ │
     └──────────────────────────────────────────────────┘
```

---

## Stack Decisions

### Why these tools, and what they cost

| Layer | Tool | Free Tier | Notes |
|-------|------|-----------|-------|
| Web frontend | Next.js on **Vercel** | ✅ Free forever | Perfect for Next.js, auto-deploys from GitHub |
| Mobile | **Expo** (React Native) | ✅ Free | Build and test locally; publish to Expo Go for beta |
| Backend API | **FastAPI** on **Railway** | ✅ $5 free credits/month | Runs Python; enough for MVP traffic |
| Database | **Supabase** | ✅ Free (500MB, 50k rows) | PostgreSQL + auth + realtime out of the box |
| File storage | **Supabase Storage** | ✅ Free (1GB) | Replaces S3 — store uploaded PDFs and transcripts here |
| LLM | **OpenRouter** | 🟡 Pay per use | Routes to cheapest model; ~$0.001 per debate at MVP scale |
| Web scraping | **Playwright** | ✅ Free | Runs on your Railway instance, no extra cost |
| Caching | **Upstash Redis** | ✅ Free (10k requests/day) | Cache scraped pages for 24h to avoid re-scraping |
| Auth | **Supabase Auth** | ✅ Free | Built into Supabase — handles email, Google OAuth |

**Estimated monthly cost at MVP (< 500 users): ~$0–3 USD**

---

## Component Breakdown

### 1. Frontend — Next.js on Vercel

```
/app
  /page.tsx              → Landing page
  /profile/page.tsx      → Profile upload form (+ resume PDF upload)
  /debate/page.tsx       → Debate session UI (chat interface)
  /scholarships/page.tsx → Scholarship comparison table
  /summary/page.tsx      → Judge summary + pros/cons
  /api/debate/[id]/
    stream/route.ts      → SSE proxy to backend
    question/route.ts    → Question injection proxy
    next-round/route.ts  → Round advancement proxy

/components
  AgentBubble.tsx        → Chat bubble with university avatar (color from DB)
  UniversitySelector.tsx → Multi-select up to 6 universities before starting
  DebateStream.tsx       → SSE listener, renders tokens as they arrive, "Next Round" button between rounds
  ProfileForm.tsx        → A-Level grades + CCA input + optional resume PDF upload
  ScholarshipCard.tsx    → Individual scholarship display
```

**SSE streaming pattern:**
```typescript
const source = new EventSource(`/api/debate/${sessionId}/stream`);
source.onmessage = (e) => appendToken(JSON.parse(e.data));
```

---

### 2. Backend — FastAPI on Railway

```
/app
  main.py                → FastAPI app entry point
  /routers
    profile.py           → POST /api/profile, POST /api/profile/{id}/resume
    debate.py            → POST /start, GET /stream, POST /question, POST /next-round
    scholarships.py      → GET /api/scholarships
  /agents
    orchestrator.py      → Manages agent turn order, debate state, and round pacing
    base_agent.py        → Base class all university agents inherit from
    nus_agent.py         → NUS ambassador — system prompt + scraper tool
    ntu_agent.py         → NTU ambassador — system prompt + scraper tool
    smu_agent.py         → SMU ambassador — system prompt + scraper tool
    suss_agent.py        → SUSS ambassador — system prompt + scraper tool
    sutd_agent.py        → SUTD ambassador — system prompt + scraper tool
    sit_agent.py         → SIT ambassador — system prompt + scraper tool
    judge_agent.py       → Neutral moderator and summary generator
    registry.py          → Maps university key → agent class (for dynamic loading)
  /tools
    scraper.py           → Playwright scraper, called by agents as a tool
    cache.py             → Upstash Redis read/write for scraped content
  /db
    supabase_client.py   → Supabase Python client (profiles, debates, messages, storage)
    models.py            → Pydantic models (StudentProfile, DebateSession, etc.)
```

---

### 3. Multi-Agent Debate System

The debate follows a structured loop managed by `orchestrator.py`. Students select **2–6 universities** to compare — the orchestrator dynamically loads only the chosen agents.

```
Student selects universities (e.g. NUS, SMU, SUTD)
      │
      ▼
┌─────────────────────────────────────────────┐
│              Orchestrator                   │
│                                             │
│  Loads agents from registry:                │
│    registry["NUS"]  → NUSAgent              │
│    registry["SMU"]  → SMUAgent              │
│    registry["SUTD"] → SUTDAgent             │
│                                             │
│  Round 1:  Each selected agent speaks       │
│  ── pause: wait for "Next Round" click ──   │
│  Round 2:  Each agent rebuts others         │
│  ── pause: wait for "Next Round" click ──   │
│  Round 3:  Each agent closing argument      │
│  Final:    Judge Agent summarises           │
│                                             │
│  (Student can inject questions between      │
│   rounds while paused, or during rounds)    │
└─────────────────────────────────────────────┘
```

**Each agent has:**
- A fixed system prompt defining its persona and university allegiance
- Access to the `scraper` tool (can call it to fetch live data mid-debate)
- The student's profile injected into every prompt
- Memory of the full debate history (passed as context each turn)

**All agents inherit from `BaseUniversityAgent`** — adding a new university is just subclassing and filling in the config:

```python
# agents/base_agent.py
class BaseUniversityAgent:
    university: str        # e.g. "SMU"
    full_name: str         # e.g. "Singapore Management University"
    website: str           # e.g. "smu.edu.sg"
    seed_urls: list[str]   # pages to scrape first
    color: str             # hex color for UI avatar
    strengths: list[str]   # pre-loaded talking points

    def get_system_prompt(self, profile, history) -> str:
        return f"""
You are the official ambassador for {self.full_name} ({self.university}).
Your goal is to persuade the student that {self.university} is the best choice for them.
Student profile: {profile}
Debate history so far: {history}
Use the scrape_page tool to fetch live data from {self.website} to back your claims.
Always cite your sources. Be persuasive but factually accurate.
"""

# agents/registry.py
from agents.nus_agent   import NUSAgent
from agents.ntu_agent   import NTUAgent
from agents.smu_agent   import SMUAgent
from agents.suss_agent  import SUSSAgent
from agents.sutd_agent  import SUTDAgent
from agents.sit_agent   import SITAgent

REGISTRY = {
    "NUS":  NUSAgent,
    "NTU":  NTUAgent,
    "SMU":  SMUAgent,
    "SUSS": SUSSAgent,
    "SUTD": SUTDAgent,
    "SIT":  SITAgent,
}
```

---

### 4. Database Schema (Supabase / PostgreSQL)

```sql
-- Student profiles
CREATE TABLE profiles (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES auth.users,       -- Supabase Auth user
  alevel      JSONB,                            -- { "H2 Math": "A", "H2 Physics": "B", ... }
  ccas        TEXT[],
  course      TEXT,
  citizenship TEXT,
  resume_text TEXT DEFAULT '',                  -- extracted text from uploaded PDF resume
  resume_path TEXT DEFAULT '',                  -- Supabase Storage path (resumes/{profile_id}.pdf)
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- Debate sessions
CREATE TABLE debates (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id  UUID REFERENCES profiles(id),
  agents      TEXT[],                           -- e.g. ['NUS', 'SMU', 'SUTD'] — any subset of 6
  status      TEXT DEFAULT 'active',            -- 'active' | 'completed'
  summary     TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- Individual messages in a debate
CREATE TABLE messages (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  debate_id   UUID REFERENCES debates(id),
  agent       TEXT,                             -- 'NUS'|'NTU'|'SMU'|'SUSS'|'SUTD'|'SIT'|'JUDGE'|'USER'
  content     TEXT,
  sources     TEXT[],                           -- scraped URLs cited
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- University config (one row per university — makes it easy to add more later)
CREATE TABLE universities (
  key         TEXT PRIMARY KEY,                 -- 'NUS', 'NTU', 'SMU', 'SUSS', 'SUTD', 'SIT'
  full_name   TEXT,
  website     TEXT,
  color       TEXT,                             -- hex color for UI avatar
  active      BOOLEAN DEFAULT true             -- toggle off to disable without deleting
);

-- Scholarship data (seed once, update manually)
CREATE TABLE scholarships (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  university  TEXT REFERENCES universities(key),
  name        TEXT,
  bond_years  INT,
  citizenship TEXT[],                           -- eligible citizenships
  url         TEXT,
  notes       TEXT
);
```

**Seed data for `universities` table:**
```sql
INSERT INTO universities (key, full_name, website, color) VALUES
  ('NUS',  'National University of Singapore',        'nus.edu.sg',  '#003D7C'),
  ('NTU',  'Nanyang Technological University',        'ntu.edu.sg',  '#C4122F'),
  ('SMU',  'Singapore Management University',         'smu.edu.sg',  '#0033A0'),
  ('SUSS', 'Singapore University of Social Sciences', 'suss.edu.sg', '#5B2D8E'),
  ('SUTD', 'Singapore University of Technology & Design', 'sutd.edu.sg', '#E4002B'),
  ('SIT',  'Singapore Institute of Technology',       'singaporetech.edu.sg', '#0073CE');
```

---

### 5. File Storage (Supabase Storage — replaces S3)

Supabase Storage is free up to 1GB — more than enough for MVP.

```
supabase storage bucket: "resumes"
  /{profile_id}.pdf                    → uploaded PDF resumes (text extracted server-side via pymupdf)

supabase storage bucket: "uniadvisor"
  /uploads/{user_id}/profile-docs/     → uploaded PDFs (scholarship eligibility)
  /transcripts/{debate_id}/            → exported debate transcripts (PDF)
```

**Upload from frontend:**
```typescript
const { data, error } = await supabase.storage
  .from('uniadvisor')
  .upload(`uploads/${userId}/profile-docs/${file.name}`, file);
```

---

### 6. Scraping Layer

Playwright runs on the same Railway instance as FastAPI. No separate service needed at MVP scale.

```python
# tools/scraper.py
from playwright.async_api import async_playwright
import hashlib
from cache import get_cache, set_cache

async def scrape_page(url: str) -> str:
    cache_key = hashlib.md5(url.encode()).hexdigest()
    cached = await get_cache(cache_key)
    if cached:
        return cached                          # serve from Redis if < 24h old

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, timeout=15000)
        content = await page.inner_text("body")
        await browser.close()

    await set_cache(cache_key, content, ttl=86400)   # cache for 24h
    return content
```

**Key pages to scrape per agent:**

| Agent | Seed URLs |
|-------|-----------|
| NUS  | nus.edu.sg/admissions, nus.edu.sg/scholarships, relevant faculty pages |
| NTU  | ntu.edu.sg/admissions, ntu.edu.sg/scholarships, relevant faculty pages |
| SMU  | smu.edu.sg/admissions, smu.edu.sg/scholarships, relevant school pages |
| SUSS | suss.edu.sg/admissions, suss.edu.sg/scholarships, suss.edu.sg/programmes |
| SUTD | sutd.edu.sg/admissions, sutd.edu.sg/scholarships, sutd.edu.sg/programmes |
| SIT  | singaporetech.edu.sg/admissions, singaporetech.edu.sg/scholarships, programme pages |

---

### 7. LLM — OpenRouter

OpenRouter routes your API calls to the cheapest available model that meets your requirements. No need to commit to OpenAI or Anthropic directly.

```python
# Recommended models for this use case (via OpenRouter)
DEBATE_MODEL  = "anthropic/claude-3-haiku"    # Fast, cheap, great for debate turns
JUDGE_MODEL   = "anthropic/claude-3.5-sonnet" # Better reasoning for final summary

# Rough cost estimate (6-agent debate)
# ~1,500 tokens per agent turn × 6 agents × 3 rounds = ~27,000 tokens
# + 800 token summary = ~27,800 tokens/debate
# At Haiku pricing (~$0.00025/1k tokens input) ≈ $0.007 per debate
# 500 debates/month ≈ $3.50 USD
#
# Tip: let students pick 2–3 universities to keep cost and debate length manageable
```

---

### 8. Caching — Upstash Redis (Free Tier)

Upstash offers a serverless Redis with a free tier of 10,000 requests/day — enough for a student project.

```python
# cache.py
import httpx, os

UPSTASH_URL   = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

async def get_cache(key: str):
    r = await httpx.get(f"{UPSTASH_URL}/get/{key}",
                        headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"})
    return r.json().get("result")

async def set_cache(key: str, value: str, ttl: int = 86400):
    await httpx.get(f"{UPSTASH_URL}/set/{key}/{value}/ex/{ttl}",
                    headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"})
```

---

## Environment Variables

Store these in Railway (backend) and Vercel (frontend) dashboards — never commit to Git.

```bash
# Backend (Railway)
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
OPENROUTER_API_KEY=
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app

# Frontend (Vercel)
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

---

## Deployment Checklist

- [ ] Push backend to GitHub → connect to Railway → auto-deploys on push
- [ ] Push frontend to GitHub → connect to Vercel → auto-deploys on push
- [ ] Create Supabase project → run schema SQL → copy URL and keys
- [ ] Create Upstash Redis instance → copy REST URL and token
- [ ] Sign up for OpenRouter → get API key → add $5 credit to start
- [ ] Set all environment variables in Railway and Vercel dashboards
- [ ] Install Playwright browsers on Railway: `playwright install chromium`
- [ ] Seed `universities` table with all 6 university rows
- [ ] Seed `scholarships` table with scholarships for all 6 universities
- [ ] Test debate end-to-end with a 2-university and 3-university matchup

---

## Scaling Path (When You Do Have Money)

You won't need any of this for a while, but here's the upgrade path:

| Current (Free) | Upgrade To | When |
|----------------|-----------|------|
| Railway free tier | Railway Hobby ($5/mo) or Fly.io | > 500 active users |
| Supabase free | Supabase Pro ($25/mo) | > 50k DB rows or > 1GB storage |
| Upstash free | Upstash Pay-as-you-go | > 10k scrapes/day |
| OpenRouter (Haiku) | Claude Sonnet direct | When quality needs a boost |
| Supabase Storage | Cloudflare R2 ($0.015/GB) | > 1GB of uploaded files |

---

*Built to run on free tiers. Ship first, scale later.*