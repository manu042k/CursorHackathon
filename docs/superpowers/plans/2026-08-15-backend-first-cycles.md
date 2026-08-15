# Backend-First Cycles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. One subagent per **phase**. Do not commit until that phase’s review is clean, then one commit for the whole phase.

**Goal:** Ship the locked owner flow backend-first: engine → research contract (offline) → live Reddit/web fetch → owner UI, with Cursor billed from `backend/.env`.

**Architecture:** Hexagonal FastAPI + Next.js. No business-agent class. Research once before the twin (filter → distill onto catalogue labels). Market agents stay `AsyncAgent.prompt` + `tools=[]`. Cursor key is process env only.

**Tech Stack:** FastAPI, Pydantic, pytest, cursor-sdk, Next.js, DESIGN-Guide tokens, Supabase Postgres via `DATABASE_URL`.

## Global Constraints

- One variable live: `price_change` only.
- Roster catalogue: 5 `buyer` agents + 1 `competitor` + 1 `analyst`. No `business` class.
- Four persona layers: `agent_class` + `archetype` label + frozen `ArchetypeProfile` + instance (WTP, loyalty, paraphrased `evidence`). Research must not rewrite `mindset` or `behavior`.
- Rounds: integer 3–8 inclusive, default 4. Grok Bot golden paper stays 8 rounds (`data/experiments/grok-bot-seed-42/`).
- `FrozenModel` uses `extra="forbid"` — new fields need defaults so old papers still load.
- Domain code never imports `cursor_sdk`; adapters implement `DecisionPort`.
- Browser never holds `CURSOR_API_KEY` or `DATABASE_URL`.
- Cursor auth: `CURSOR_API_KEY` in `backend/.env` (and `settings.py`). No Method-strip key field. No per-request key in POST body.
- Research fetch: FastAPI + Python ADR-12 filters. Do **not** enable Cursor `webSearch` on market or research agents.
- Code lives in `frontend/` and `backend/` only.
- UI follows `DESIGN-Guide.md`: no shadows, no coral CTA, no SaaS analytics dashboard.
- One git branch for this revision. **No git commit until the phase review is Approved**, then exactly one commit whose message names the phase and story ids.
- Implement owner-flow task steps from `docs/superpowers/plans/2026-08-15-owner-flow-revision.md` in order inside each phase. TDD: failing test, then code, then pass. Do not start UI until Phase 4.

## Phase map

| Phase | Stories | Layer |
|---|---|---|
| 1 Engine | US-B8, US-B10, US-A7, US-A9, US-A10 | backend |
| 2 Research contract | US-B9, US-A8 (filters + distill + fake sources) | backend |
| 3 Live research IO | US-A8b Reddit, US-A8c web search | backend |
| 4 Owner UI | US-C8, US-C7, US-D8 | frontend |

---

### Task 1: Phase 1 Engine

Implement owner-flow revision Tasks 1–5 **in order**, TDD, no commit until all five pass and the phase review is clean.

**Stories:** US-B8 ledger, US-B10 rounds 3–8, US-A7 catalogue + profiles, US-A9 token limits, US-A10 parallel buyers + competitor on S1.

**Source of exact tests and code:** `docs/superpowers/plans/2026-08-15-owner-flow-revision.md` headings `### Task 1` through `### Task 5`. Use those tests, file paths, and snippets verbatim.

**Files (union):**
- Create: `backend/app/ledger.py`, `backend/tests/test_ledger.py`
- Create: `backend/app/roster/catalogue.py`, `backend/app/roster/profiles.py`
- Create: `backend/tests/test_catalogue.py` as specified in owner-flow Task 3
- Modify: `backend/app/twin_runner.py`, `backend/app/main.py`, `backend/app/contracts.py`, `backend/app/settings.py`, `backend/app/history.py`, `backend/app/agents/port.py`, `backend/app/agents/prompts.py`, `backend/app/roster/fixed_grok_bot.py`
- Modify: `backend/requirements.txt` (add `psycopg[binary]` pin)
- Modify: `frontend/src/types/contracts.ts` for rounds 3–8
- Modify: `backend/tests/test_http_experiments.py`, `backend/tests/test_history.py`, `backend/tests/test_decision_port.py`, other tests named in those five tasks
- Do not rewrite `backend/db/schema.sql` except comments. Status enum stays the shipped six values until Phase 2.

**Interfaces produced:**
- `Ledger.append(...) -> int` with `InMemoryLedger`; Postgres when `DATABASE_URL` set; pytest uses InMemory
- Event types exactly as owner-flow Task 1 (no `research.*` yet)
- `rounds: int = Field(default=4, ge=3, le=8)` plus `applies_from_round` in `1..rounds`
- `RosterAgent.agent_class` / `archetype`; `profiles.py` `ArchetypeProfile` + `profile_for` + `persona_payload` that ignores research mindset rewrites
- `REASON_MAX_LEN = 400`; history truncated oldest-first
- Twin runner: five buyers `asyncio.gather` on S0; competitor after apply on S1; `share`, `mrr`, `wtp_gap` on `AgentDecisionRequest`

**Verify:**
```
cd backend
.venv/Scripts/pytest tests/test_ledger.py tests/test_http_experiments.py tests/test_catalogue.py tests/test_decision_port.py tests/test_history.py tests/test_fixture_adapter.py -v
```
If additional tests exist for twin order (Task 5), include them. Full `pytest` before reporting DONE.

**Do not:** start research status machine, Reddit/web fetch, roster confirm UI, or git commit.

---

### Task 2: Phase 2 Research contract

Implement owner-flow Tasks 6 and 7 **in order**. Live `fetch_reddit` / `fetch_web` remain injectable fakes / empty in production until Phase 3.

**Stories:** US-B9 research then confirm then start; US-A8 filters + distill + fixture propose.

**Source:** owner-flow `### Task 6` and `### Task 7`.

**Files:** as listed in those two tasks (`generate.py`, `research/filters.py`, `sources.py`, `distill.py`, status enum + migration, HTTP start endpoint, tests).

**Verify:**
```
cd backend
.venv/Scripts/pytest tests/test_http_experiments.py tests/test_sse.py tests/test_research_filters.py tests/test_generate_roster.py tests/test_catalogue.py -v
```
Then full `pytest`.

**Do not:** call live Reddit, Brave, or Cursor `webSearch`. Do not git commit until phase review is clean.

---

### Task 3: Phase 3 Live Reddit and web search

Fill `backend/app/roster/research/sources.py` for the Cursor adapter path only. Fixture path still skips fetch.

**Reddit:** PRAW application-only (`REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` in `settings.py` / `.env_template`). `read_only = True`. Search allowlisted category subreddits. Never `r/all`. Map posts to the `filter_items` dict shape (source, subreddit, title, text, score, num_comments, created_utc, nsfw, removed, stickied, url, category).

**Web:** `httpx` GET Brave Search (`BRAVE_SEARCH_API_KEY`) with category + decision queries. Map results to the same item shape (`source="web"`). Do not use Cursor `webSearch`.

**Pipeline:** `fetch_reddit` + `fetch_web` → `filter_items` → if `len(kept) < 4` fixture roster + `research.json` `{quality: "fallback", kept_count}` else `distill` + `{quality: "ok", reddit_ids, web_urls}` with **no raw bodies**. Missing credentials → empty fetch → fallback, do not crash the research thread.

**Tests:** inject fakes; pytest never hits the network. Add `backend/tests/test_research_sources.py` covering mapping helpers and “no creds → []”.

**Verify:**
```
cd backend
.venv/Scripts/pytest tests/test_research_sources.py tests/test_research_filters.py tests/test_generate_roster.py -v
```
Then full `pytest`.

**Do not:** git commit until phase review is clean. Do not add a browser Cursor key field.

---

### Task 4: Phase 4 Owner UI

Implement owner-flow Tasks 8–10 **in order**: US-C8 rounds control, US-C7 roster confirm, US-D8 paper figures.

**Source:** owner-flow `### Task 8` through `### Task 10`.

**Do not:** collect `CURSOR_API_KEY` in the form. Adapter checkbox may remain; key stays in `.env`.

**Verify:** the check scripts and typecheck named in those tasks, plus backend pytest still green.

**Do not:** git commit until phase review is clean.
