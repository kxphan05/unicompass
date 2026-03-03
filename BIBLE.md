# UniAdvisor — Project Bible

**Version:** 0.4 — All Agents + Scholarships
**Last updated:** 2026-03-03

---

## Stack Constraints

| Layer | Technology | Notes |
|-------|-----------|-------|
| Language | Python 3.13 | Managed with `uv` |
| PDF extraction | pymupdf | Fast, lightweight text extraction from uploaded resumes |
| Backend framework | FastAPI | On Fly.io (added in Step 2, deployed Step 5) |
| LLM gateway | OpenRouter | `httpx` calls to `https://openrouter.ai/api/v1/chat/completions` |
| Database | Supabase (PostgreSQL) | Free tier — added in Step 2 |
| Cache | Upstash Redis | REST API via `httpx`, free tier (10k req/day) |
| Web scraping | Playwright (Chromium) | Runs on same host as backend |
| Frontend | Next.js on Vercel | Added in Step 3 — `frontend/` |
| Auth | Supabase Auth | Deferred to later steps |

---

## Environment Variables

```
OPENROUTER_API_KEY=         # Required — OpenRouter API key
UPSTASH_REDIS_REST_URL=     # Required — Upstash Redis REST endpoint
UPSTASH_REDIS_REST_TOKEN=   # Required — Upstash Redis bearer token
SUPABASE_URL=               # Step 2+
SUPABASE_SERVICE_KEY=        # Step 2+
```

Store in `.env` locally, in Fly.io/Vercel dashboards for deployment. **Never commit `.env`.**

---

## Architectural Rules

1. **All university agents inherit `BaseUniversityAgent`** — adding a new university = subclass + config.
2. **Registry pattern** — `app/agents/registry.py` maps university key → agent class. Orchestrator loads agents dynamically.
3. **Scraping is cached** — every `scrape_page()` call checks Upstash Redis first (24h TTL).
4. **Agents get full context** — student profile (including resume text) + debate history injected into every LLM call.
5. **SSE streaming** — debate turns streamed to frontend via Server-Sent Events (Step 2+).
6. **User-paced rounds** — after each round, the backend pauses (`asyncio.Event`) until the student clicks "Next Round". This gives time to read and inject questions.
7. **Resume upload** — optional PDF upload via `POST /api/profile/{id}/resume`. Text extracted server-side with `pymupdf`, original stored in Supabase Storage `resumes` bucket.
8. **Free-tier first** — no paid infrastructure until there are real users.

---

## Data Schema

See `ARCHITECTURE.md` § Database Schema for full SQL. Key tables:

- `profiles` — student A-Level grades, CCAs, course preference, citizenship, resume text/path
- `debates` — session tracking, selected agents, status, summary
- `messages` — individual debate turns with agent attribution and cited sources
- `universities` — config table (key, full_name, website, color)
- `scholarships` — scholarship data per university

Pydantic models live in `app/db/models.py`.

---

## LLM Models (via OpenRouter)

| Purpose | Model | Rationale |
|---------|-------|-----------|
| Debate turns | `anthropic/claude-3-haiku` | Fast, cheap (~$0.00025/1k tokens) |
| Judge summary | `anthropic/claude-3.5-sonnet` | Better reasoning for synthesis |

---

## Implementation Status

| Step | Description | Status |
|------|-------------|--------|
| 0 | Project Bible (this file) | ✅ Done |
| 1 | Tracer Bullet — single agent pitch | ✅ Done |
| 2 | FastAPI + Supabase + multi-agent orchestrator | ✅ Done |
| 3 | Frontend (Next.js) + SSE streaming | ✅ Done |
| 3.1 | PDF resume upload (frontend + backend) | ✅ Done |
| 3.2 | User-paced rounds ("Next Round" button) | ✅ Done |
| 4 | All 6 agents + Judge + scholarships | ✅ Done |
| 4.1 | Parallel agent calls + context scaling | ✅ Done |
| 5 | Deployment (Fly.io + Vercel + CI/CD) | ✅ Done |

---

## Step 4 — All 6 Agents + Judge + Scholarships

### What was built

**4 new university agents** (joining existing NUS + NTU):

| Agent | File | Faculty/School mappings |
|-------|------|------------------------|
| SMU | `app/agents/smu_agent.py` | Computing, Business, Accountancy, Economics, Law, Social Sciences |
| SUSS | `app/agents/suss_agent.py` | Science & Technology, Human Development, Law |
| SUTD | `app/agents/sutd_agent.py` | ISTD, EPD, ASD, SMT, HASS, DAI (pillar system) |
| SIT | `app/agents/sit_agent.py` | ICT, Engineering, Business, Food Tech, Health Sciences, Design |

All agents follow the same pattern as NUS/NTU: `rapidfuzz` keyword matching to resolve the student's preferred course to university-specific programme URLs, capped at 2 faculty URLs + a common scholarships URL.

**Registry** (`app/agents/registry.py`) now maps all 6 keys: `NUS`, `NTU`, `SMU`, `SUSS`, `SUTD`, `SIT`.

**Frontend** (`frontend/src/lib/universities.ts`) updated with all 6 universities and their brand colors.

**Scholarships API** — `GET /api/scholarships?university=NUS&citizenship=Singaporean`:
- `app/db/models.py` — added `Scholarship` Pydantic model
- `app/db/supabase_client.py` — added `get_scholarships()` with optional university/citizenship filters
- `app/routers/scholarships.py` — implemented with query parameters
- `migrations/003_seed_scholarships.sql` — 30 scholarships seeded across all 6 universities (includes NUS AI Talent Scholarship and NTU TAISP)

### Step 4.1 — Performance: Parallel Agents + Context Scaling

With 3+ agents, debates were slow due to sequential LLM calls and growing context. Three changes fix this:

**1. Parallel agent calls** (`app/agents/orchestrator.py`):
- Agents within each round now run via `asyncio.gather()` instead of a sequential loop
- A 6-agent round takes ~1× the time of a single call, not 6×
- Results are yielded in deterministic order after all complete

**2. Reduced max tokens** (`app/agents/base_agent.py`):
- `num_agents >= 3` → `max_tokens = 1024` (was 2048)
- `num_agents < 3` → unchanged at 2048

**3. Capped scrape budget** (`app/agents/base_agent.py`):
- `num_agents >= 3` → `MAX_SCRAPED_MANY_AGENTS = 4000` chars per agent (was 10,000)
- `num_agents < 3` → unchanged at 10,000

---

## Step 5 — Deployment (Fly.io + Vercel + CI/CD)

### What was built

**Backend deployment on Fly.io:**
- `Dockerfile` — multi-stage build: Python 3.13 + uv + Playwright Chromium
- `fly.toml` — Fly.io config: Singapore region (`sin`), 1GB shared VM, auto-stop/start, health checks on `/api/health`
- `.dockerignore` — excludes frontend, .env, .git, etc.
- CORS now environment-aware via `ALLOWED_ORIGINS` env var (defaults to `*` for dev)

**Frontend deployment on Vercel:**
- Standard Next.js deployment — connect GitHub repo, set `frontend/` as root directory
- Set `NEXT_PUBLIC_API_URL` to the Fly.io backend URL

**CI/CD pipeline:**
- `.github/workflows/deploy.yml` — auto-deploys backend to Fly.io on push to `main`
- Frontend auto-deploys via Vercel's GitHub integration

### Environment variables for production

**Fly.io (backend):**
- `OPENROUTER_API_KEY`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- `ALLOWED_ORIGINS` — set to your Vercel frontend URL

**Vercel (frontend):**
- `NEXT_PUBLIC_API_URL` — set to `https://unicompass-api.fly.dev`
