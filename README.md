# Butterfly Market

A controlled twin-run market experiment: same seed, same frozen roster, **one** variable changed. Divergence is causal *inside the simulation*. This is not a forecast.

The **business owner** (platform user) enters a product, picks one action and how many rounds (3–8, default 4), confirms a researched roster of **5 user personas + 1 competitor + 1 analyst**, then reads a paper of what that change did. There is no business-agent persona.

**Shipped today:** Grok Bot fixture paper (8 rounds), `POST /experiments` starts the twin run immediately, buyers run sequentially. **Next:** research → confirm, parallel users, competitor after users, tunable rounds, extra figures — see [`architecture.md`](architecture.md) §1.1 and §14.

## Ports

| App | Directory   | Port   |
|-----|-------------|--------|
| API | `backend/`  | `8000` |
| Web | `frontend/` | `3000` |

## Environment

Copy these into `backend/.env` (never commit the file):

```
CURSOR_API_KEY=
CURSOR_MODEL=composer-2.5
DEFAULT_ADAPTER=fixture
DATA_DIR=
DATABASE_URL=
```

- `CURSOR_API_KEY` — required only for `adapter=cursor`
- `CURSOR_MODEL` — model id reported on `/health` and the paper receipt
- `DEFAULT_ADAPTER=fixture` — fixture-only demo; no Cursor calls
- `DATABASE_URL` — Supabase session-pooler Postgres URI (`sslmode=require`). JSON under `data/experiments/` is a paper export, not the live log. Never put the anon or service-role key in the frontend.
- Decision reasons are 40–400 characters (`MAX_REASON_CHARS`). Round history in the prompt is truncated from the oldest round first (`MAX_HISTORY_CHARS`, default 800).
- Research (US-A8, `adapter=cursor`): Reddit + web search only, then hygiene filters (ADR-12). Optional: `RESEARCH_MAX_AGE_DAYS`, `RESEARCH_MIN_SCORE`, `RESEARCH_MIN_COMMENTS`, `RESEARCH_MAX_ITEMS_PER_SOURCE`, `RESEARCH_MIN_KEEP`. Fixture adapter skips fetch.
- Ports stay 8000 / 3000 unless you change the start commands

## Supabase Postgres

1. Create a project at [supabase.com](https://supabase.com).
2. **Project Settings → Database → Connection string → Session pooler** (port **5432**, not 6543). Paste into `DATABASE_URL` and append `?sslmode=require` if missing.
3. Apply the ledger once: SQL Editor → paste [`backend/db/schema.sql`](backend/db/schema.sql) → Run. Or `supabase db push` (migration in `supabase/migrations/`).

The API uses this URI only. It does not use Supabase Auth, Realtime, Storage, or the JS client.

## Fixture-only (no Cursor)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
DEFAULT_ADAPTER=fixture uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. Use **Run this experiment** (fixture) or **Open the prepared Grok Bot paper**. After US-B9/C7 the primary path is **Begin research** → confirm roster → run.

## Live Cursor SDK

Python 3.10+. Install the SDK:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Set `CURSOR_API_KEY` and `DEFAULT_ADAPTER=cursor` (or POST `"adapter": "cursor"`). The API process opens `AsyncClient.launch_bridge` for the lifetime of uvicorn and each decision is `AsyncAgent.prompt` with `tools=[]`.

## Checks

```bash
cd backend && .venv/bin/pytest
cd frontend && npx tsc --noEmit
```

Vijay Ram Enaganti is inviting you to a scheduled Zoom meeting.

Topic: Vijay Ram Enaganti's Zoom Meeting
Join Zoom Meeting
https://ucr.zoom.us/j/99620594965?pwd=QaPA54w7PY9MU6Z0Rq038C8M94kOru.1

Meeting ID: 996 2059 4965
Passcode: 660223

---

One tap mobile
+13462487799,,99620594965# US (Houston)
+17209289299,,99620594965# US (Denver)

---

Dial by your location
• +1 346 248 7799 US (Houston)
• +1 720 928 9299 US (Denver)
• +1 206 337 9723 US (Seattle)
• +1 213 338 8477 US (Los Angeles)
• +1 669 219 2599 US (San Jose)
• +1 786 635 1003 US (Miami)
• +1 312 626 6799 US (Chicago)
• +1 470 250 9358 US (Atlanta)
• +1 646 876 9923 US (New York)

---
