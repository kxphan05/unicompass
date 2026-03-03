# UniCompass — Project Bible

**Version:** 0.6 — Debate UX Polish
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
| Auth | Supabase Auth | Planned for Step 7 |

---

## Environment Variables

```
OPENROUTER_API_KEY=         # Required — OpenRouter API key
UPSTASH_REDIS_REST_URL=     # Required — Upstash Redis REST endpoint
UPSTASH_REDIS_REST_TOKEN=   # Required — Upstash Redis bearer token
SUPABASE_URL=               # Step 2+
SUPABASE_SERVICE_KEY=        # Step 2+
ALLOWED_ORIGINS=            # Production CORS — set to Vercel frontend URL
```

Store in `.env` locally, in Fly.io/Vercel dashboards for deployment. **Never commit `.env`.**

---

## Architectural Rules

1. **All university agents inherit `BaseUniversityAgent`** — adding a new university = subclass + config.
2. **Registry pattern** — `app/agents/registry.py` maps university key → agent class. Orchestrator loads agents dynamically.
3. **Scraping is cached** — every `scrape_page()` call checks Upstash Redis first (24h TTL).
4. **Agents get full context** — student profile (including resume text) + debate history injected into every LLM call.
5. **SSE streaming** — debate turns streamed to frontend via Server-Sent Events, proxied through Next.js API routes to avoid CORS. Custom event types: `message`, `done`, `error`, `wait_for_next`, `pros_cons`.
6. **User-paced rounds** — after each round, the backend pauses (`asyncio.Event`) until the student clicks "Next Round". During the pause, students can inject questions that agents answer inline without advancing the round.
7. **Inline Q&A** — questions injected between rounds are answered immediately by all agents in parallel. The orchestrator races `proceed_event.wait()` against `question_queue.get()` using `asyncio.wait(FIRST_COMPLETED)`, then re-emits `wait_for_next` to stay between rounds.
8. **Resume upload** — optional PDF upload via `POST /api/profile/{id}/resume`. Text extracted server-side with `pymupdf`, original stored in Supabase Storage `resumes` bucket.
9. **Free-tier first** — no paid infrastructure until there are real users.
10. **Parallel agent execution** — agents within each round run via `asyncio.gather()` for performance.
11. **Judge pros/cons extraction** — Judge prompt produces a fenced `json` block with structured pros/cons. Backend parses it (greedy regex for nested braces), strips it from the prose, and emits a separate `pros_cons` SSE event.

---

## Data Schema

See `migrations/` for full SQL. Key tables:

- `profiles` — student A-Level grades, CCAs, course preference, citizenship, additional comments, resume text/path
- `debates` — session tracking, selected agents, status, summary
- `messages` — individual debate turns with agent attribution and cited sources
- `universities` — config table (key, full_name, website, color)
- `scholarships` — scholarship data per university (name, bond_years, citizenship, url, notes)

Pydantic models live in `app/db/models.py`.

---

## LLM Models (via OpenRouter)

| Purpose | Model | Rationale |
|---------|-------|-----------|
| Debate turns | `openrouter/free` | Free tier for MVP development |
| Judge summary | `openrouter/free` | Free tier for MVP development |

> **Note:** Production should use `anthropic/claude-3-haiku` for debate turns and `anthropic/claude-3.5-sonnet` for judge summary for better quality.

---

## Current File Structure

```
app/
├── __init__.py
├── main.py                     # FastAPI app entry point
├── agents/
│   ├── __init__.py
│   ├── base_agent.py           # BaseUniversityAgent — shared scraping + LLM logic
│   ├── judge_agent.py          # Neutral Judge summarizer
│   ├── orchestrator.py         # run_debate() — manages rounds, parallelism, pausing
│   ├── registry.py             # REGISTRY dict mapping key → agent class
│   ├── nus_agent.py
│   ├── ntu_agent.py
│   ├── smu_agent.py
│   ├── suss_agent.py
│   ├── sutd_agent.py
│   └── sit_agent.py
├── db/
│   ├── __init__.py
│   ├── models.py               # Pydantic models
│   └── supabase_client.py      # All Supabase CRUD operations
├── routers/
│   ├── __init__.py
│   ├── debate.py               # /api/debate/* endpoints + SSE
│   ├── profile.py              # /api/profile/* endpoints + resume upload
│   └── scholarships.py         # /api/scholarships endpoint
└── tools/
    ├── __init__.py
    ├── cache.py                # Upstash Redis cache helpers
    └── scraper.py              # Playwright scraper with caching

frontend/src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                # Landing page
│   ├── profile/page.tsx        # Profile form + university selector
│   ├── debate/[id]/page.tsx    # Debate viewer
│   └── api/debate/[id]/        # Next.js proxy routes for SSE, questions, next-round
├── components/
│   ├── AgentBubble.tsx         # Single debate message with university branding + sources
│   ├── DebateStream.tsx        # SSE consumer + round controls + question input + post-debate actions
│   ├── ProsConsTable.tsx       # Structured pros/cons table per university after Judge summary
│   ├── ProfileForm.tsx         # A-Level grades, CCAs, course, citizenship, resume upload
│   └── UniversitySelector.tsx  # Multi-select university picker
└── lib/
    ├── api.ts                  # Backend API client functions
    ├── exportPdf.ts            # html2canvas-pro + jsPDF transcript export
    ├── types.ts                # TypeScript interfaces
    └── universities.ts         # University config (key, fullName, color)
```

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
| 6 | Debate UX polish (pros/cons, transcript export, disclaimer, Q&A) | ✅ Done |
| **7** | **Scholarship frontend + comparison** | **🔲 Planned** |
| **8** | **Profile CRUD + debate history** | **🔲 Planned** |
| **9** | **Authentication (Supabase Auth)** | **🔲 Planned** |
| **10** | **Mobile responsiveness + QA** | **🔲 Planned** |

---

## Completed Steps (1–5)

### Step 1 — Tracer Bullet
Single NUS agent with hardcoded profile → proves LLM + scraping pipeline works end-to-end.

### Step 2 — FastAPI + Supabase + Multi-Agent Orchestrator
Backend API with profile CRUD, debate session management, SSE streaming, and Supabase persistence.

### Step 3 — Frontend + SSE Streaming
Next.js frontend with profile form, university selector, debate viewer with real-time SSE, question injection, and user-paced rounds. Resume upload with PDF text extraction via pymupdf.

### Step 4 — All 6 Agents + Judge + Scholarships

**6 university agents** (NUS, NTU, SMU, SUSS, SUTD, SIT):
- All inherit `BaseUniversityAgent`
- `rapidfuzz` keyword matching to resolve student's course to university-specific programme URLs
- Capped at 2 faculty URLs + common scholarships URL per agent

**Registry** (`app/agents/registry.py`) maps all 6 keys.

**Scholarships API** — `GET /api/scholarships?university=NUS&citizenship=Singaporean`:
- `app/db/models.py` — `Scholarship` Pydantic model
- `app/db/supabase_client.py` — `get_scholarships()` with optional filters
- `app/routers/scholarships.py` — query parameter filtering
- `migrations/003_seed_scholarships.sql` — 30 scholarships seeded across all 6 universities

### Step 4.1 — Performance: Parallel Agents + Context Scaling

- **Parallel agent calls** via `asyncio.gather()` — round takes ~1× single call, not N×
- **Reduced max tokens** — `num_agents >= 3` → `max_tokens = 1024` (was 2048)
- **Capped scrape budget** — `num_agents >= 3` → 4000 chars per agent (was 10,000)

### Step 5 — Deployment (Fly.io + Vercel + CI/CD)

- `Dockerfile` — multi-stage build: Python 3.13 + uv + Playwright Chromium
- `fly.toml` — Singapore region (`sin`), 1GB shared VM, health checks on `/api/health`
- `.github/workflows/deploy.yml` — auto-deploy backend to Fly.io on push to `main`
- Frontend auto-deploys via Vercel GitHub integration
- CORS environment-aware via `ALLOWED_ORIGINS`

---

## Step 6 — Debate UX Polish (Done)

**Goal:** Make the debate output more actionable and shareable. PRD refs: U5, U6, U7, U8.

### 6.1 Pros/Cons Summary Table

Judge prompt updated to append a fenced `json` block with structured pros/cons per university. Backend parses and strips it.

**Backend:**
- `app/agents/judge_agent.py` — prompt instructs Judge to append `{"pros_cons": {"NUS": {"pros": [...], "cons": [...]}, ...}}` in a fenced JSON block. `parse_pros_cons()` extracts it with greedy regex (`\{.*\}` to handle nested braces). `strip_json_block()` removes it from prose.
- `app/routers/debate.py` — after Judge event, parses pros/cons, strips JSON from content before persisting to `messages` table, emits a separate `pros_cons` SSE event.

**Frontend:**
- `frontend/src/lib/types.ts` — `ProsConsData = Record<string, { pros: string[]; cons: string[] }>`
- `frontend/src/components/ProsConsTable.tsx` — responsive grid table. Each university gets a column with green-tinted pros and red-tinted cons. Uses university colors from `UNIVERSITIES` config.
- `frontend/src/lib/api.ts` — `streamDebate()` accepts `onProsCons` callback, handles `pros_cons` SSE event type.
- `frontend/src/components/DebateStream.tsx` — `prosConsData` state, renders `<ProsConsTable>` after Judge bubble.

**Graceful fallback:** If the Judge fails to produce valid JSON, `parse_pros_cons()` returns `None`, no `pros_cons` event is emitted, and no table is shown. The prose summary still displays normally.

### 6.2 Transcript Export (PDF)

Frontend-only PDF export using `html2canvas-pro` (maintained fork with better CSS support) + `jsPDF`.

- `frontend/src/lib/exportPdf.ts` — `exportDebatePdf(elementId, sessionId)` captures the `#debate-content` div via `html2canvas` at 2x scale, splits into A4 pages with `jsPDF`, triggers download as `unicompass-debate-{id}.pdf`.
- `frontend/src/components/DebateStream.tsx` — "Download Transcript" button in post-debate footer. Dynamic import of `exportPdf.ts` to avoid loading the libraries until needed.

**Dependencies added:** `html2canvas-pro`, `jspdf`

### 6.3 Disclaimer Banner

- `frontend/src/app/debate/[id]/page.tsx` — amber disclaimer bar below header: *"UniCompass is a decision-support tool. Always verify information with official university sources."*
- `frontend/src/app/page.tsx` — gray disclaimer text below "Get Started" button.

### 6.4 Share Summary Link

Copy-to-clipboard of the unique debate URL. A full public read-only page deferred to Step 9 (requires auth decisions).

**Backend:**
- `app/routers/debate.py` — `GET /api/debate/{id}/summary` returns debate metadata + messages + summary for completed debates. Returns 400 if debate is not completed.

**Frontend:**
- `frontend/src/components/DebateStream.tsx` — "Copy Link" button in post-debate footer. Uses `navigator.clipboard.writeText(window.location.href)` with a 2-second "Copied!" toast.

### 6.5 Inline Q&A (Between Rounds)

Students can ask questions between rounds. Agents answer directly without advancing to the next debate round.

**Backend:**
- `app/agents/orchestrator.py` — the wait loop between rounds now races `proceed_event.wait()` against `question_queue.get()` using `asyncio.wait(FIRST_COMPLETED)`. When a question arrives: appends to history, yields a `Student` event, runs all agents in parallel with `round_type="answer"`, yields their responses, then re-emits `wait_for_next` to stay paused. Multiple questions can be asked before advancing.
- `app/agents/base_agent.py` — when `round_type == "answer"`, the user message instructs agents to answer the student's question directly and concisely (under 150 words) from their university's perspective.

**Frontend:**
- `frontend/src/lib/types.ts` — `DebateEvent.round` changed from `number` to `number | string` to accommodate `"answer"` and `"question"` round types.
- `frontend/src/components/DebateStream.tsx` — local "You" bubble added immediately on send (blue-tinted). Backend `Student` events filtered out to prevent duplicates. `awaitingAnswer` state disables "Next Round" button while agents respond, showing "Answering your question..." spinner. Question input hidden while awaiting answer. "Next Round" button placed below question input.
- `frontend/src/components/AgentBubble.tsx` — "You" agent styled with blue theme (`#2563EB`, `bg-blue-50`). String round types displayed with capitalized label (e.g. "Answer") instead of "Round X".

---

## Step 7 — Scholarship Frontend + Comparison (Planned)

**Goal:** Expose the existing scholarships API in the frontend. PRD refs: S2, S3, S4, S6.

### 7.1 Scholarship Browsing Page

- New page: `frontend/src/app/scholarships/page.tsx`
- Filters: university dropdown, citizenship dropdown
- Calls `GET /api/scholarships?university=X&citizenship=Y`
- Renders a card grid with scholarship name, university, bond years, link to official page

### 7.2 Scholarship Comparison

- Allow selecting up to 4 scholarships for side-by-side comparison
- New component: `frontend/src/components/ScholarshipCompare.tsx`
- Table columns: name, university, bond years, citizenship eligibility, link

### 7.3 Scholarship Context in Debates

- Inject relevant scholarships into agent system prompts so agents can reference them
- `app/agents/base_agent.py` — in `get_system_prompt()`, query `get_scholarships(university=self.university, citizenship=profile.citizenship)` and append to the prompt
- This way agents naturally weave scholarship info into their arguments

---

## Step 8 — Profile CRUD + Debate History (Planned)

**Goal:** Let users manage their profile and review past debates. PRD refs: P6, H1, H2, H3.

### 8.1 Profile Edit & Delete

**Backend:**
- `app/routers/profile.py` — add `PUT /api/profile/{id}` (update fields) and `DELETE /api/profile/{id}` (cascade delete profile + debates + messages + resume from storage)
- `app/db/supabase_client.py` — add `update_profile()` and `delete_profile()` functions

**Frontend:**
- Allow editing on `/profile` page when a `profile_id` query param or session value is present
- Add a "Delete my data" button with confirmation dialog

### 8.2 Debate History

**Backend:**
- `app/routers/debate.py` — add `GET /api/debates?profile_id=X` to list past debates
- `app/routers/debate.py` — add `GET /api/debate/{id}/messages` to retrieve full transcript
- `app/db/supabase_client.py` — add `get_debates_for_profile()` (already has `get_messages()`)

**Frontend:**
- New page: `frontend/src/app/history/page.tsx` — lists past debates with status, date, agents
- Clicking a debate navigates to `/debate/[id]` which loads from stored messages instead of re-streaming

---

## Step 9 — Authentication (Planned)

**Goal:** Persistent user accounts so profiles and debate history survive across sessions. PRD refs: A1, A2, A3, P5.

### 9.1 Supabase Auth Integration

**Backend:**
- Add Supabase Auth JWT verification middleware to FastAPI
- Protect profile/debate endpoints — tie profiles to `auth.uid()`
- Guest mode: allow unauthenticated access but data is ephemeral (session-bound `profile_id` stored in cookie)

**Frontend:**
- `frontend/src/lib/auth.ts` — Supabase Auth client helpers (signUp, signIn, signOut, getSession)
- New component: `frontend/src/components/AuthModal.tsx` — email/password login + Google OAuth
- Persist `profile_id` in Supabase user metadata so returning users auto-load their profile
- Add login/signup buttons to the header; show user email when logged in

### 9.2 Row-Level Security

- Enable Supabase RLS on `profiles`, `debates`, `messages` tables
- Policies: users can only read/write their own data
- Service key bypasses RLS for backend operations

---

## Step 10 — Mobile Responsiveness + QA (Planned)

**Goal:** Ensure the app works well on mobile devices and is production-ready. PRD ref: U4.

### 10.1 Mobile Layout Fixes

- Test all pages on 375px (iPhone SE) and 390px (iPhone 14) viewports
- Fix any overflow, truncation, or touch-target issues
- Ensure the debate stream scrolls correctly on mobile
- Profile form should be usable without horizontal scroll

### 10.2 Quality Assurance

- Add rate limiting to debate endpoints (max 5 active debates per IP per hour)
- Add input validation / sanitization for profile fields
- Test with 3+ agents on mobile to verify performance
- Verify scraper respects robots.txt for all 6 university domains
- Add error boundaries in React for graceful failure handling
- Test PDF export on mobile browsers

---

## Priority Order

The steps above are ordered by impact and dependency:

1. **Step 6 (Debate UX)** — highest user-facing impact, no backend dependencies
2. **Step 7 (Scholarships)** — backend already exists, just needs frontend
3. **Step 8 (Profile CRUD + History)** — needed before auth makes sense
4. **Step 9 (Auth)** — ties everything together with persistent accounts
5. **Step 10 (Mobile + QA)** — polish pass before public launch
