# UniCompass — Product Requirements Document (PRD)

**Version:** 1.1 — Post-MVP Gap Analysis
**Status:** Active
**Last Updated:** March 2026
**Author:** TBD

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Goals & Success Metrics](#3-goals--success-metrics)
4. [Target Users](#4-target-users)
5. [User Journeys](#5-user-journeys)
6. [Product Requirements](#6-product-requirements)
7. [Out of Scope (v1.1)](#7-out-of-scope-v11)
8. [Assumptions & Constraints](#8-assumptions--constraints)
9. [Risks & Mitigations](#9-risks--mitigations)
10. [Open Questions](#10-open-questions)

---

## 1. Executive Summary

UniCompass is an AI-powered web application that helps post-A Level students in Singapore decide which university and scholarship to pursue. Using a multi-agent debate system, AI ambassadors representing Singapore's six autonomous universities (NUS, NTU, SMU, SUTD, SIT, SUSS) argue for their respective institutions based on the student's personal academic profile. Students watch the debate, ask questions, and receive a neutral summary — turning an overwhelming life decision into an informed, personalised conversation.

---

## 2. Problem Statement

### The Challenge

Post-A Level students in Singapore face one of the most consequential decisions of their lives with limited, fragmented information. University open houses are brief. Peer advice is biased. Official websites are dense and hard to compare. Scholarship options are scattered across portals.

### Key Pain Points

- **Information overload:** University websites contain thousands of pages of content that students struggle to parse and compare side-by-side.
- **Generic advice:** Existing tools (rankings, forums, YouTube vlogs) are not personalised to the student's specific subject combination, grades, or interests.
- **Decision paralysis:** Without a structured framework for comparison, many students default to following peers rather than making the best choice for themselves.
- **Scholarship blindspots:** Many students miss scholarship opportunities they are eligible for due to poor discoverability.

### Why Now

Large language models and multi-agent AI frameworks have matured to the point where personalised, real-time, web-aware debate agents are technically feasible at consumer scale and cost.

---

## 3. Goals & Success Metrics

### Product Goals

| Goal | Description |
|------|-------------|
| Personalised guidance | Every debate is tailored to the student's specific A-Level results, CCAs, and course interests |
| Live, accurate information | Agents scrape university websites in real-time so data is never stale |
| Engagement over passivity | Students actively participate in the debate rather than reading a static report |
| Scholarship discoverability | Surface relevant scholarships students may not have considered |

### Success Metrics (MVP)

| Metric | Target (3 months post-launch) |
|--------|-------------------------------|
| Monthly Active Users | 2,000+ |
| Debate completion rate | > 65% of started debates are completed |
| Profile upload rate | > 80% of users upload a profile before debating |
| User satisfaction (CSAT) | > 4.2 / 5.0 |
| Transcript download rate | > 30% of completed debates |
| Avg. session duration | > 8 minutes |

---

## 4. Target Users

### Primary: Post-A Level Students

- **Age:** 17–19
- **Context:** Awaiting or just received A-Level results; applying to NUS, NTU, SMU, SUTD, SIT, SUSS, or overseas universities
- **Needs:** Personalised comparison, scholarship info, course-specific guidance
- **Tech comfort:** High — mobile-first, comfortable with chat interfaces

### Secondary: Parents

- **Age:** 40–55
- **Context:** Supporting their child's decision; may view transcripts or summaries shared by students
- **Needs:** Trust in accuracy of information, clear pros/cons, scholarship financial details

### Tertiary: JC / School Counsellors

- **Context:** May recommend the tool to students; could use summaries in counselling sessions
- **Needs:** Shareable outputs, unbiased framing

---

## 5. User Journeys

### Journey 1: First-Time Student

```
1. Student lands on UniCompass homepage
2. Continues as guest (no account required for v1.1)
3. Uploads academic profile:
     - A-Level subjects and grades
     - CCAs and achievements
     - Intended course / faculty
     - Citizenship
     - Optional: resume PDF, additional comments
4. Selects 2+ universities to compare (from NUS, NTU, SMU, SUTD, SIT, SUSS)
5. Debate begins — watches university agents argue in structured rounds
6. Pauses between rounds to read; asks follow-up questions
7. Debate concludes with Judge agent summary
8. Views pros/cons table and scholarship matches
9. Downloads or shares transcript
```

### Journey 2: Returning Student

```
1. Student returns; re-enters profile (or logs in if auth is live)
2. Starts a new debate for a different course or university set
3. Reviews past debate transcripts for comparison
4. Shares summary card with parents
```

### Journey 3: Scholarship-Focused Student

```
1. Student uploads profile including citizenship
2. Navigates to Scholarship page directly
3. Views matched scholarships filtered by university and citizenship
4. Compares scholarships side-by-side
5. Starts a targeted debate focused on scholarship offerings
```

---

## 6. Product Requirements

### 6.1 Profile Management

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| P1 | Students can input A-Level subjects and grades via a structured form | Must Have | ✅ Done |
| P2 | Students can list CCAs, roles, and achievements as free text | Must Have | ✅ Done |
| P3 | Students can select their intended course / faculty from a text input | Must Have | ✅ Done |
| P4 | Students can upload a PDF resume (max 5MB) for richer context | Should Have | ✅ Done |
| P5 | Profiles persist across sessions (tied to account) | Should Have | ❌ Missing — requires auth |
| P6 | Students can edit or delete their profile | Must Have | ❌ Missing — no PUT/DELETE endpoints or UI |

### 6.2 Agent Debate Engine

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| D1 | System supports 2–6 concurrent agents (NUS, NTU, SMU, SUTD, SIT, SUSS) | Must Have | ✅ Done |
| D2 | Each agent is equipped with a real-time web scraper for its university's website | Must Have | ✅ Done |
| D3 | Agents receive the student's profile as context and reference it in arguments | Must Have | ✅ Done |
| D4 | Debate follows a structured turn-based format (pitch → rebuttal → closing) | Must Have | ✅ Done |
| D5 | A neutral Judge agent synthesises the debate and produces a final summary | Must Have | ✅ Done |
| D6 | Students can submit questions that redirect the debate between rounds | Must Have | ✅ Done |
| D7 | Agent responses cite their sources (scraped URLs) displayed in the UI | Should Have | ✅ Done |
| D8 | Debate round count is configurable (default: 3 rounds) | Nice to Have | ❌ Missing — hardcoded to 3 |
| D9 | User-paced rounds — debate pauses between rounds until student clicks "Next Round" | Must Have | ✅ Done |
| D10 | Agents run in parallel within each round for performance | Must Have | ✅ Done |

### 6.3 Debate UI

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| U1 | Chat-style interface with distinct agent colour branding per university | Must Have | ✅ Done |
| U2 | Agent responses rendered as Markdown with university-branded left border | Must Have | ✅ Done |
| U3 | Student question input is always accessible during an active debate | Must Have | ✅ Done |
| U4 | Debate is viewable on both web and mobile with responsive layout | Must Have | ⚠️ Partial — basic Tailwind responsive, not mobile-tested |
| U5 | Completed debate shows a structured pros/cons table per university | Must Have | ❌ Missing — only raw Judge markdown |
| U6 | Full debate transcript is exportable as PDF | Should Have | ❌ Missing |
| U7 | Summary card is shareable as an image or link | Should Have | ❌ Missing |
| U8 | Disclaimer banner: "Decision support tool, not a decision maker" | Must Have | ❌ Missing |

### 6.4 Scholarship Module

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| S1 | System maintains a database of scholarships across all 6 universities | Must Have | ✅ Done (30 seeded) |
| S2 | Scholarships can be filtered by university and citizenship | Must Have | ✅ Done (backend only) |
| S3 | Frontend scholarship browsing page | Must Have | ❌ Missing — no frontend page |
| S4 | Side-by-side comparison table for up to 4 scholarships | Should Have | ❌ Missing |
| S5 | Scholarship data links to official pages for application details | Must Have | ✅ Done (URL field in DB) |
| S6 | Agents reference relevant scholarships during the debate | Should Have | ❌ Missing — no scholarship injection into agent context |
| S7 | Scholarship eligibility scoring matched to student profile | Nice to Have | ❌ Missing |

### 6.5 Authentication & Accounts

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| A1 | Students can use the app as a guest (profile stored per session) | Must Have | ⚠️ Partial — works as guest but profile goes to Supabase with no session binding |
| A2 | Students can create an account with email + password (Supabase Auth) | Should Have | ❌ Missing |
| A3 | OAuth login via Google | Should Have | ❌ Missing |
| A4 | Singpass / MyInfo integration for profile pre-fill | Nice to Have | ❌ Out of scope |

### 6.6 Debate History & Retrieval

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| H1 | Backend endpoint to list past debates for a profile | Must Have | ❌ Missing |
| H2 | Backend endpoint to retrieve all messages for a completed debate | Must Have | ⚠️ Partial — `get_messages()` exists in DB client but no router endpoint |
| H3 | Frontend page to browse and replay past debates | Should Have | ❌ Missing |

---

## 7. Out of Scope (v1.1)

The following are explicitly excluded and earmarked for future versions:

- **Overseas universities** (e.g. UK, US, Australian universities)
- **Polytechnic vs JC comparison** — focused on post-A Level university decisions only
- **Live chat with a human counsellor**
- **Application submission assistance** (the app informs decisions, not applications)
- **Peer comparison** ("students like me chose...")
- **Push notifications** for application deadlines
- **Mandarin / Malay language support**
- **SIM agent** (may be added later)
- **Mobile native app** (web-only for now)
- **Singpass / MyInfo integration**

---

## 8. Assumptions & Constraints

### Assumptions

- University public-facing websites remain scrapable and do not block automated access
- Students are willing to share academic grades within the app in exchange for personalised advice
- LLM inference costs are manageable at MVP scale (~2,000 MAU) without per-user throttling
- The debate format (rather than a static report) meaningfully increases user engagement and trust

### Constraints

- **Regulatory:** No storage of NRIC or full name — profiles use grades and interests only
- **Data accuracy:** Agents can only be as accurate as their scraped sources; hallucination risk must be mitigated via source citation and grounding
- **Scraping ethics:** Must comply with robots.txt and university ToS; may need to negotiate data access agreements for production
- **Cost:** LLM API costs per debate session must be kept under SGD $0.10 at MVP scale
- **Free-tier infrastructure:** Supabase free tier, Upstash free tier (10k req/day), Fly.io shared VM

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| University websites block scrapers | Medium | High | Respectful rate limiting; 24h Redis cache; explore official data partnerships |
| LLM hallucination produces inaccurate info | Medium | High | Require agents to cite scraped sources; add disclaimer UI; source links in bubbles |
| Students treat AI recommendation as authoritative | High | Medium | Frame app as "decision support, not decision maker"; include prominent disclaimer; Judge agent uses balanced language |
| Low profile completion rate | Medium | Medium | Show value preview before requiring profile; allow partial profiles with graceful degradation |
| High LLM cost at scale | Low (MVP) / High (growth) | High | Token budgets per debate; dynamic max_tokens scaling; cached scrape content |
| Data breach of student profiles | Low | High | No PII beyond grades; right-to-delete (requires profile delete endpoint); Supabase RLS |

---

## 10. Open Questions

| # | Question | Owner | Target Resolution |
|---|----------|-------|-------------------|
| 1 | Should the Judge agent produce a single recommendation, or remain strictly neutral? | Product | Before Phase 2 |
| 2 | What is the right default number of debate rounds? (UX research needed) | Design | Phase 2 |
| 3 | Do we need formal approval from universities to scrape their websites? | Legal | Before public launch |
| 4 | Should parents have a separate view/login, or share via a link? | Product | Phase 3 |
| 5 | Should the pros/cons table be LLM-generated or structured from Judge output? | Engineering | Step 6 |
| 6 | What analytics/tracking should we add for success metrics? | Product | Step 7 |

---

*This PRD is a living document. It should be reviewed and updated at the start of each development phase.*
