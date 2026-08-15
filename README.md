# Counterfactual Replay

A controlled twin-run market experiment: same seed, same frozen roster, **one** variable changed. Divergence is causal *inside the simulation*. This is not a forecast.

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
```

- `CURSOR_API_KEY` — required only for `adapter=cursor`
- `CURSOR_MODEL` — model id reported on `/health` and the paper receipt
- `DEFAULT_ADAPTER=fixture` — fixture-only demo; no Cursor calls
- Ports stay 8000 / 3000 unless you change the start commands

## Fixture-only (no Cursor)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
DEFAULT_ADAPTER=fixture uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. Use **Run this experiment** (fixture) or **Open the prepared Grok Bot paper**.

## Live Cursor SDK

Python 3.10+. Install the SDK:

```bash
cd backend
source .venv/bin/activate
pip install cursor-sdk
pip install -e ".[dev]"
```

Set `CURSOR_API_KEY` and `DEFAULT_ADAPTER=cursor` (or POST `"adapter": "cursor"`). The API process opens `AsyncClient.launch_bridge` for the lifetime of uvicorn and each decision is `AsyncAgent.prompt` with `tools=[]`.

## Checks

```bash
cd backend && .venv/bin/pytest
cd frontend && npx tsc --noEmit
```
