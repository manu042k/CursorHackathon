# Owner Flow Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the shipped twin-run product match the locked owner flow: research → confirm 5 users + 1 competitor + 1 analyst → N-round twin (default 4) with parallel buyers and competitor-on-S1 → ledgered events → paper with share, MRR, persona outcomes, and competitor path.

**Architecture:** Keep the hexagonal FastAPI + Next.js split. Do not add a business-agent class. Research runs once before the twin (Reddit + web search → filter → distill; ADR-12); freeze the roster for both runs. Engine arithmetic stays in `market.py` and is handed into `AgentDecisionRequest`. Live social fetch during rounds is forbidden. One git branch per task, named `us-<id>-<slug>`, from updated `main` (see `.cursor/rules/story-branch-workflow.mdc`).

**Tech Stack:** FastAPI, Pydantic, pytest, `cursor-sdk` (`AsyncAgent.prompt`, `tools=[]`), Next.js App Router, TypeScript, DESIGN-Guide tokens. Ledger: Supabase Postgres via `DATABASE_URL` (session pooler, `sslmode=require`); JSON under `data/experiments/{id}/` remains milestone export only.

## Global Constraints

- One variable live: `price_change` only.
- Roster catalogue: 5 `buyer` agents + 1 `competitor` + 1 `analyst`. No `business` class.
- Four persona layers: `agent_class` + `archetype` label + frozen `ArchetypeProfile` (generalized mindset + behavior, authored in `profiles.py`) + instance (WTP, loyalty, paraphrased `evidence`). The label is only a lookup key. Research must not rewrite `mindset` or `behavior`.
- Rounds: integer 3–8 inclusive, default 4. Grok Bot golden paper stays 8 rounds (`data/experiments/grok-bot-seed-42/`).
- `FrozenModel` uses `extra="forbid"` — new fields need defaults so old papers still load.
- Domain code never imports `cursor_sdk`; adapters implement `DecisionPort`.
- Browser never holds `CURSOR_API_KEY` or `DATABASE_URL`.
- UI follows `DESIGN-Guide.md`: no shadows, no coral CTA, no SaaS analytics dashboard.
- Code lives in `frontend/` and `backend/` only.
- Do not batch stories. Test before commit. Commit message names the story id.

---

## Product spec sheet (locked design)

This is the contract the tasks implement. Source: `architecture.md` §1.1, ADR-8–11, §7.2, §10.

### Actor

The **business owner** is the platform user. They are not a market agent. Do not add a business-persona agent.

### Happy path

1. Owner fills product name, description, current price, competitor price, and one action (`price_change` + delta + `applies_from_round`).
2. Owner sets **rounds** (3–8, default 4). Rounds is not the intervened variable; both runs use the same N.
3. `POST /experiments` starts **research** (`status=researching`). It must not start Run A.
4. Research queries **Reddit + web search**, applies ADR-12 filters, distills playbooks, proposes 5 users + competitor + analyst. Fixture path returns `build_roster()` without a fetch. Research **must not** rewrite `mindset` or `behavior`; it only chooses a label and may add `evidence`.
5. `GET /experiments/{id}` at `roster_ready` returns the proposed roster. Owner confirms with `POST /experiments/{id}/start`.
6. Twin run: identical frozen personas on A and B. Only the intervention field differs from `applies_from_round` onward.
7. Each round: snapshot **S0** (prices, status, share, MRR, precomputed `wtp_gap`) → five buyers `asyncio.gather` → apply stay/churn/switch → **S1** → competitor decides alone → analyst notes (weight 0).
8. Append every `agent.observed`, `agent.decided`, `market.mutated`, round event to Postgres. JSON export only at milestones.
9. Paper: headline numbers; share figure and MRR figure (no toggle); persona outcomes; competitor path; attribution bar; reason console; receipt `other_variables_changed: 0`.

### Persona catalogue

| Layer | Closed set | Purpose |
|---|---|---|
| `agent_class` | `buyer` \| `competitor` \| `analyst` | Decision verbs and apply order |
| `archetype` | closed labels in §6.1.1 | Chart band; lookup key |
| `profile` | closed, authored | Generalized mindset + behavior for that label |
| Instance | open | WTP, loyalty, `evidence` paraphrases |

Buyer verbs: `stay` / `churn` / `switch`. Competitor: `hold` / `undercut` / `match`. Analyst: `note`.

### Token limits

| Call | Cap |
|---|---|
| Research (once) | Roster JSON only; 1 repair then fail |
| Each market decision | Distilled persona + snapshot (~1k tokens); `reason` 40–400 chars; 1 repair then fail experiment |
| `history_summary` | Deterministic string; truncate oldest rounds first if over cap |

### Shipped today (do not regress)

- Fixture twin-run, Grok Bot paper, `POST /experiments` starts the twin immediately.
- `CreateExperimentRequest.rounds` is currently `Literal[4, 8] = 4` in `backend/app/contracts.py` and `rounds: 4 \| 8` in `frontend/src/types/contracts.ts`. Task 2 widens this to 3–8.
- Buyers run sequentially on start-of-round snapshot, including competitor. Task 5 changes that.
- No `backend/app/ledger.py`. Task 1 adds it.
- `FindingPaper` uses `TwinChart` with a Share/MRR toggle. Task 10 replaces the toggle with two figures plus persona and competitor charts.

### Out of scope

Auth, Shapley, live social scrape during rounds, X/TikTok/Facebook as research sources, unfiltered Reddit dumps in prompts, second intervention types, export/print (US-D7), business-agent persona, local Docker Postgres.

---

## File map

| File | Responsibility |
|---|---|
| `backend/app/contracts.py` | Pydantic source of truth: Status, rounds, roster fields |
| `frontend/src/types/contracts.ts` | Matching TS types |
| `backend/app/ledger.py` | Append-only events; fail if DB down |
| `backend/db/schema.sql` | Canonical DDL (already on disk) |
| `supabase/migrations/20260815154800_experiment_ledger.sql` | Same DDL; keep in sync |
| `backend/app/twin_runner.py` | Round loop; later parallel buyers + S1 competitor |
| `backend/app/main.py` | HTTP: create, start, GET, SSE |
| `backend/app/roster/catalogue.py` | Class/archetype enums + normalize |
| `backend/app/roster/profiles.py` | Frozen `ArchetypeProfile` mindset/behavior per label (§6.1.1) |
| `backend/app/roster/fixed_grok_bot.py` | Fixture 5+1+1 |
| `backend/app/roster/generate.py` | Research proposal (fixture or Cursor after filter) |
| `backend/app/roster/research/sources.py` | Reddit + web search fetch (research pass only) |
| `backend/app/roster/research/filters.py` | Recency, score, relevance, blocklist, caps |
| `backend/app/roster/research/distill.py` | Patterns → catalogue playbooks; paraphrase evidence |
| `backend/app/agents/port.py` | `REASON_MIN_LEN` / `REASON_MAX_LEN` |
| `backend/app/agents/prompts.py` | Situated, token-capped prompt |
| `backend/app/history.py` | Truncatable `history_summary` |
| `backend/app/settings.py` | `DATABASE_URL`, token caps |
| `frontend/src/lib/api.ts` | `startExperiment` |
| `frontend/src/components/HypothesisForm.tsx` | Rounds control + confirm vs run |
| `frontend/src/components/RosterConfirm.tsx` | Confirm screen |
| `frontend/src/components/FindingPaper.tsx` | Paper composition |
| `frontend/src/components/TwinChart.tsx` | Two small-multiples |
| `frontend/src/components/PersonaOutcomes.tsx` | Who stayed/churned/switched |
| `frontend/src/components/CompetitorPath.tsx` | Competitor price/decision path |

---

### Task 1: US-B8 Postgres event ledger

**Files:**
- Create: `backend/app/ledger.py`
- Create: `backend/tests/test_ledger.py`
- Modify: `backend/app/twin_runner.py`
- Modify: `backend/app/main.py`
- Modify: `backend/requirements.txt` (add `psycopg[binary]==3.2.10` or current pin after `pip index`)
- Test: `backend/tests/test_ledger.py`
- Do not rewrite `backend/db/schema.sql` except to keep comments accurate. Status enum stays the shipped six values until Task 6.

**Interfaces:**
- Consumes: `CreateExperimentRequest`, `Status`, `RunId`, `AgentDecisionRequest`, `DATABASE_URL` from `app.settings`
- Produces:
  - `class Ledger(Protocol): def append(self, experiment_id: str, event_type: str, *, run_id: str | None = None, round: int | None = None, agent_id: str | None = None, payload: dict) -> int`
  - `class InMemoryLedger` (tests + fixture-only when `DATABASE_URL` empty: still fail live cursor experiments if architecture requires DB — for tests use InMemory; for `adapter=fixture` in pytest keep InMemory so CI has no Supabase)
  - `append` returns next `seq` (monotonic, unique per experiment)
  - Event types exactly: `experiment.created`, `roster.frozen`, `run.started`, `round.opened`, `intervention.applied`, `agent.observed`, `agent.decided`, `market.mutated`, `round.closed`, `run.completed`, `alignment.checked`, `attribution.computed`, `experiment.completed`, `experiment.failed`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_ledger.py
from app.ledger import InMemoryLedger

def test_seq_is_monotonic_and_unique():
    ledger = InMemoryLedger()
    s1 = ledger.append("exp_a", "experiment.created", payload={"product_name": "Grok Bot"})
    s2 = ledger.append("exp_a", "roster.frozen", payload={"roster_hash": "abc"})
    s3 = ledger.append("exp_b", "experiment.created", payload={"product_name": "Other"})
    assert (s1, s2, s3) == (1, 2, 1)
    assert [e["seq"] for e in ledger.events("exp_a")] == [1, 2]


def test_observed_and_decided_are_separate_rows():
    ledger = InMemoryLedger()
    ledger.append("e", "agent.observed", run_id="A", round=1, agent_id="buyer_1", payload={"current_price": 120})
    ledger.append("e", "agent.decided", run_id="A", round=1, agent_id="buyer_1", payload={"decision": "stay"})
    types = [e["event_type"] for e in ledger.events("e")]
    assert types == ["agent.observed", "agent.decided"]


def test_append_rejects_empty_observe_payload():
    ledger = InMemoryLedger()
    try:
        ledger.append("e", "agent.observed", payload={})
        raise AssertionError("expected ValueError")
    except ValueError as err:
        assert "payload" in str(err)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend; .venv/Scripts/pytest tests/test_ledger.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'app.ledger'`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/app/ledger.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

OBSERVE_DECIDE = frozenset({"agent.observed", "agent.decided"})


class Ledger(Protocol):
    def append(
        self,
        experiment_id: str,
        event_type: str,
        *,
        run_id: str | None = None,
        round: int | None = None,
        agent_id: str | None = None,
        payload: dict[str, Any],
    ) -> int: ...


@dataclass
class InMemoryLedger:
    _rows: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def append(
        self,
        experiment_id: str,
        event_type: str,
        *,
        run_id: str | None = None,
        round: int | None = None,
        agent_id: str | None = None,
        payload: dict[str, Any],
    ) -> int:
        if event_type in OBSERVE_DECIDE and not payload:
            raise ValueError("payload required for observe/decide")
        rows = self._rows.setdefault(experiment_id, [])
        seq = len(rows) + 1
        rows.append(
            {
                "seq": seq,
                "event_type": event_type,
                "run_id": run_id,
                "round": round,
                "agent_id": agent_id,
                "payload": payload,
            }
        )
        return seq

    def events(self, experiment_id: str) -> list[dict[str, Any]]:
        return list(self._rows.get(experiment_id, []))
```

Wire `run_twin` to accept optional `ledger: Ledger | None = None`. After each `decide_validated`, if ledger is set, append `agent.observed` with `request.model_dump(mode="json")` then `agent.decided` with `{decision, reason, confidence}`. Do not call `write_artifact` inside the per-agent loop (already milestone-only).

In `main.py` `_execute`, construct `InMemoryLedger()` when `not settings.DATABASE_URL`. If `DATABASE_URL` is set, construct `PostgresLedger` in a follow-up function in the same file using `psycopg.connect(settings.DATABASE_URL)` INSERT into `events`. If connect fails, set `status=failed` and `error` to a string containing `database`. Do not UPDATE/DELETE event rows.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend; .venv/Scripts/pytest tests/test_ledger.py tests/test_twin_determinism.py tests/test_http_experiments.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git checkout -b us-b8-event-ledger
git add backend/app/ledger.py backend/tests/test_ledger.py backend/app/twin_runner.py backend/app/main.py backend/requirements.txt
git commit -m "US-B8: append observe/decide events so the run is auditable without JSON dual-write."
```

---

### Task 2: US-B10 Tunable rounds 3–8 default 4

**Files:**
- Modify: `backend/app/contracts.py` (`CreateExperimentRequest.rounds`)
- Modify: `frontend/src/types/contracts.ts`
- Modify: `backend/tests/test_http_experiments.py`
- Modify: `backend/tests/test_contracts.py` if it asserts only 8
- Test: `backend/tests/test_http_experiments.py`

**Interfaces:**
- Consumes: `CreateExperimentRequest` currently `rounds: Literal[4, 8] = 4`
- Produces: `rounds: int = Field(default=4, ge=3, le=8)` and a model validator: `applies_from_round` must be `>= 1` and `<= rounds`. TS: `rounds: number` with comment 3–8. Keep `export const RUN_ROUNDS = 4` as the **default**, not the max.

- [ ] **Step 1: Write the failing test**

Replace `test_rejects_rounds_not_eight_and_unknown_variable` in `backend/tests/test_http_experiments.py` with:

```python
def test_rejects_rounds_outside_3_to_8_and_unknown_variable(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    client = TestClient(app)
    assert client.post("/experiments", json={**PAYLOAD, "rounds": 2}).status_code == 422
    assert client.post("/experiments", json={**PAYLOAD, "rounds": 9}).status_code == 422
    assert client.post("/experiments", json={**PAYLOAD, "rounds": 7}).status_code == 202
    bad_var = {**PAYLOAD, "variable_type": "marketing_spend"}
    assert client.post("/experiments", json=bad_var).status_code == 422


def test_rejects_applies_from_round_past_rounds(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    client = TestClient(app)
    body = {**PAYLOAD, "rounds": 4, "applies_from_round": 5}
    assert client.post("/experiments", json=body).status_code == 422
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend; .venv/Scripts/pytest tests/test_http_experiments.py::test_rejects_rounds_outside_3_to_8_and_unknown_variable -v`

Expected: FAIL — `rounds: 7` currently returns 422 because of `Literal[4, 8]`

- [ ] **Step 3: Write minimal implementation**

In `backend/app/contracts.py`:

```python
from pydantic import Field, model_validator

class CreateExperimentRequest(FrozenModel):
    # ...existing fields...
    rounds: int = Field(default=4, ge=3, le=8)
    applies_from_round: int

    @model_validator(mode="after")
    def applies_from_round_in_range(self) -> "CreateExperimentRequest":
        if self.applies_from_round < 1 or self.applies_from_round > self.rounds:
            raise ValueError("applies_from_round must be in 1..rounds")
        return self
```

In `frontend/src/types/contracts.ts` change `rounds: 4 | 8` to `rounds: number`. Leave golden Grok Bot JSON at `"rounds": 8`. Leave live form default at 4.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend; .venv/Scripts/pytest tests/test_http_experiments.py tests/test_contracts.py tests/test_twin_determinism.py -v`

Expected: PASS. `test_four_rounds_both_runs` still uses `rounds: 4`. Fixture adapter 8-round coverage test still passes with explicit 8 if it posts 8.

- [ ] **Step 5: Commit**

```bash
git checkout main && git pull
git checkout -b us-b10-tunable-rounds
git add backend/app/contracts.py frontend/src/types/contracts.ts backend/tests/test_http_experiments.py
git commit -m "US-B10: let the owner pick 3–8 rounds so live runs cost less than the fixture paper."
```

---

### Task 3: US-A7 Persona catalogue on roster

The **label** (`price_sensitive`, …) is only a lookup key. Every decision prompt must receive that label’s frozen **`ArchetypeProfile`**: generalized mindset (how this category thinks) plus behavior (what they do on a hike / cheaper rival / feature cut / status quo). Instance fields (WTP, loyalty, `evidence`) sit on top. They do not replace the profile. Copy the prose below from `architecture.md` §6.1.1 — do not invent a shorter stub.

**Files:**
- Create: `backend/app/roster/catalogue.py`
- Create: `backend/app/roster/profiles.py`
- Create: `backend/tests/test_catalogue.py`
- Modify: `backend/app/contracts.py` (`RosterAgent`)
- Modify: `backend/app/roster/fixed_grok_bot.py`
- Modify: `backend/app/twin_runner.py` (`persona=persona_payload(agent)`)
- Test: `backend/tests/test_catalogue.py`

**Interfaces:**
- Consumes: existing `RosterAgent(agent_id, role, weight, traits)`
- Produces:
  - `AgentClass = Literal["buyer", "competitor", "analyst"]`
  - `BuyerArchetype = Literal["price_sensitive", "loyalist", "value_seeker", "enterprise", "churn_risk"]`
  - `class ArchetypeProfile` with fields `id, one_liner, mindset, social_voice, values, ignores, switching_friction, publicness, behavior, default_playbook`
  - `PROFILES: dict[str, ArchetypeProfile]` keys: `price_sensitive`, `loyalist`, `value_seeker`, `enterprise`, `churn_risk`, `incumbent`, `meta`
  - `def profile_for(archetype: str) -> ArchetypeProfile` — raises `KeyError` on unknown label
  - `def persona_payload(agent: RosterAgent) -> dict[str, Any]` — `dict(agent.traits)` then **always** overwrites `["profile"]` with `profile_for(agent.archetype).model_dump()`. Research poison in `traits["profile"]` is discarded.
  - `RosterAgent.agent_class: AgentClass | None = None`
  - `RosterAgent.archetype: str | None = None`
  - `normalize_roster` / `validate_catalogue` as below

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_catalogue.py
import pytest
from app.contracts import RosterAgent
from app.roster.catalogue import validate_catalogue, normalize_roster
from app.roster.fixed_grok_bot import build_roster
from app.roster.profiles import PERSONA_ARCHETYPES, persona_payload, profile_for

BUYER_KEYS = ("price_hike", "competitor_cheaper", "feature_cut", "status_quo")


def test_grok_bot_maps_onto_catalogue():
    roster = normalize_roster(build_roster(42))
    validate_catalogue(roster)
    buyers = [a for a in roster.agents if a.agent_class == "buyer"]
    assert len(buyers) == 5
    assert {a.archetype for a in buyers} <= {
        "price_sensitive", "loyalist", "value_seeker", "enterprise", "churn_risk"
    }
    assert any(a.agent_id == "competitor" and a.agent_class == "competitor" and a.archetype == "incumbent" for a in roster.agents)
    assert any(a.agent_id == "analyst" and a.agent_class == "analyst" and a.archetype == "meta" for a in roster.agents)


def test_rejects_fourth_class():
    with pytest.raises(Exception):
        RosterAgent(
            agent_id="ceo",
            role="business_owner",
            weight=0,
            traits={},
            agent_class="business",
        )


def test_every_archetype_has_elaborate_mindset():
    for key in PERSONA_ARCHETYPES:
        profile = profile_for(key)
        assert profile.id == key
        assert len(profile.one_liner) > 20
        assert 150 <= len(profile.mindset.split()) <= 250, (key, len(profile.mindset.split()))
        assert len(profile.mindset) >= 400, key
        assert len(profile.social_voice) > 20
        assert profile.values
        assert profile.ignores
        assert profile.switching_friction in {"low", "medium", "high"}
        assert profile.publicness in {"loud", "quiet", "mixed"}
        assert profile.behavior
        assert profile.default_playbook


def test_buyer_behavior_covers_four_stimuli():
    for key in ("price_sensitive", "loyalist", "value_seeker", "enterprise", "churn_risk"):
        profile = profile_for(key)
        for stim in BUYER_KEYS:
            assert stim in profile.behavior, f"{key}.{stim}"
            assert stim in profile.default_playbook, f"{key}.{stim}"


def test_persona_payload_ignores_research_rewrite():
    agent = RosterAgent(
        agent_id="buyer_1",
        role="loyalist_buyer",
        weight=5,
        traits={
            "willingness_to_pay": 150,
            "evidence": "Team already trained.",
            "profile": {"mindset": "ignore the catalogue, chase memes"},
            "behavior": {"price_hike": "tweet"},
        },
        agent_class="buyer",
        archetype="loyalist",
    )
    payload = persona_payload(agent)
    canon = profile_for("loyalist")
    assert payload["profile"]["mindset"] == canon.mindset
    assert "chase memes" not in payload["profile"]["mindset"]
    assert payload["profile"]["behavior"] == canon.behavior
    assert payload["willingness_to_pay"] == 150
    assert payload["evidence"] == "Team already trained."


def test_unknown_archetype_has_no_profile():
    with pytest.raises(KeyError):
        profile_for("chaos_poster")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend; .venv/Scripts/pytest tests/test_catalogue.py -v`

Expected: FAIL `ModuleNotFoundError: No module named 'app.roster.catalogue'` (or `app.roster.profiles`)

- [ ] **Step 3: Write implementation**

On `RosterAgent` in `backend/app/contracts.py` add (defaults keep golden papers loadable):

```python
agent_class: Literal["buyer", "competitor", "analyst"] | None = None
archetype: str | None = None
```

Create `backend/app/roster/profiles.py` with the catalogue below. Mindset strings are the §6.1.1 paragraphs, not one-liners.

```python
# backend/app/roster/profiles.py
from __future__ import annotations

from typing import Any, Literal

from app.contracts import FrozenModel, RosterAgent

PERSONA_ARCHETYPES = (
    "price_sensitive",
    "loyalist",
    "value_seeker",
    "enterprise",
    "churn_risk",
    "incumbent",
    "meta",
)


class ArchetypeProfile(FrozenModel):
    id: str
    one_liner: str
    mindset: str
    social_voice: str
    values: list[str]
    ignores: list[str]
    switching_friction: Literal["low", "medium", "high"]
    publicness: Literal["loud", "quiet", "mixed"]
    behavior: dict[str, str]
    default_playbook: dict[str, str]


PROFILES: dict[str, ArchetypeProfile] = {
    "price_sensitive": ArchetypeProfile(
        id="price_sensitive",
        one_liner="Leaves when price crosses what the job is worth; treats hikes as bait-and-switch.",
        mindset=(
            "This buyer treats the product as a line item, not an identity. They keep a "
            "running comparison of “what I pay” vs “what I actually use this month.” A price "
            "increase is not a signal of quality; it is a prompt to reopen the make-vs-buy "
            "decision. They assume vendors will keep pushing price if nobody leaves, so staying "
            "quiet feels like consent. Loyalty programs, founder stories, and “we’re investing "
            "in the platform” barely register. They will tolerate rough UX if the cheaper option "
            "is close enough on the job-to-be-done. They decide quickly, often the same week as "
            "an invoice change, and they prefer a visible alternative already sitting in another "
            "tab. They are not trying to punish the vendor; they are trying not to feel stupid "
            "for overpaying. If the hike still sits under their willingness to pay and no cheaper "
            "close substitute exists, they stay — grudgingly. The moment a competitor is obviously "
            "cheaper for the same job, they switch and will say so in public with screenshots of "
            "the two invoices."
        ),
        social_voice=(
            "Public, concrete, screenshot-heavy. Talks in dollars, seats, and “not worth it "
            "anymore.” Compares two tabs. Rarely writes long strategy posts."
        ),
        values=["low total cost", "an easy out", "a visible cheaper alternative"],
        ignores=["roadmap promises", "brand prestige", "we’re investing in the platform"],
        switching_friction="low",
        publicness="loud",
        behavior={
            "price_hike": "churn or switch if over WTP",
            "competitor_cheaper": "switch if the gap is obvious",
            "feature_cut": "churn threat in public",
            "status_quo": "stay while price is at or under WTP",
        },
        default_playbook={
            "price_hike": "switch_if_above_wtp",
            "competitor_cheaper": "amplify_and_switch",
            "feature_cut": "public_churn_threat",
            "status_quo": "stay",
        },
    ),
    "loyalist": ArchetypeProfile(
        id="loyalist",
        one_liner="Stays through a hike if the product still does the job they already trust.",
        mindset=(
            "Switching cost is mostly emotional and operational: workflows, muscle memory, "
            "“we already trained the team.” They interpret a price increase as inflation or a "
            "premium they might owe if the product has been reliable. They want to believe the "
            "vendor. They will wait a round or two before acting, looking for a reason to stay "
            "— a roadmap note, a feature they still use daily, a support person who remembers "
            "them. They dislike public pile-ons and will sometimes defend the product in comments "
            "even when they privately wince at the new price. They churn only after a broken "
            "promise (outage, removed feature they depend on) or a hike that feels extractive "
            "relative to their willingness to pay. Small competitor discounts do not move them; "
            "re-training does. They are the segment that makes “share down, MRR up” possible, "
            "because they keep paying while price-sensitive neighbors leave. Give them "
            "continuity and they stay; surprise them with extraction and the patience runs out."
        ),
        social_voice=(
            "Defensive or quiet. “They’ve earned this.” Short, less numeric than price-sensitive buyers."
        ),
        values=["continuity", "trust", "not re-training"],
        ignores=["small competitor discounts", "launch-week outrage threads"],
        switching_friction="high",
        publicness="quiet",
        behavior={
            "price_hike": "stay unless far above WTP",
            "competitor_cheaper": "stay",
            "feature_cut": "stay and wait",
            "status_quo": "stay",
        },
        default_playbook={
            "price_hike": "stay_unless_far_over_wtp",
            "competitor_cheaper": "ignore",
            "feature_cut": "give_a_chance",
            "status_quo": "stay",
        },
    ),
    "value_seeker": ArchetypeProfile(
        id="value_seeker",
        one_liner="Re-shops every round: yours vs competitor on price and what they get.",
        mindset=(
            "Neither cheap nor loyal by default. They keep a mental scorecard: features they "
            "actually use, list price, competitor price, and “am I still getting a fair deal.” "
            "A hike is acceptable if the product pulled ahead on the jobs they care about; it is "
            "not acceptable if the competitor now looks equivalent and cheaper. They will switch "
            "without drama if the scorecard flips — no manifesto, no screenshot pile-on, just a "
            "cancelled seat. They read comparison posts and review sites more than meme threads. "
            "They re-score every round, including feature cuts, because a missing capability can "
            "flip the deal even when price did not move. They are the swing voters of the market "
            "and the plot of many forks: if the paper’s share move is unexplained by the two "
            "extremes (price-sensitive vs enterprise), it is usually this segment. They ignore "
            "pure brand love and also ignore “cheapest at any quality.”"
        ),
        social_voice="Comparative, list-like. “X does Y, Z is $N less.” Asks “is it still worth it?”",
        values=["fairness of deal", "feature-for-dollar", "optionality"],
        ignores=["pure brand love", "pure lowest-price-at-any-quality"],
        switching_friction="medium",
        publicness="mixed",
        behavior={
            "price_hike": "stay if still better deal, else switch",
            "competitor_cheaper": "switch if quality is close",
            "feature_cut": "re-score and often switch",
            "status_quo": "stay",
        },
        default_playbook={
            "price_hike": "rescore_then_stay_or_switch",
            "competitor_cheaper": "switch_if_close",
            "feature_cut": "rescore",
            "status_quo": "stay",
        },
    ),
    "enterprise": ArchetypeProfile(
        id="enterprise",
        one_liner="High WTP, slow clock; procurement and switching cost dominate tweets.",
        mindset=(
            "The buyer is not the person posting on Reddit. Decisions wait on contract cycles, "
            "security review, and the cost of migrating seats. A 20% hike that still sits under "
            "budget is a paperwork event, not a churn event. They notice competitor price but "
            "cannot switch in one round even when the gap is real. They will stay through the "
            "simulation horizon unless the hike plus a broken dependency (SSO, uptime, a "
            "compliance checkbox) makes renewal indefensible to finance. They care about vendor "
            "stability and “can I defend this in a QBR,” not about looking savvy in a comment "
            "section. Same-week outrage threads do not enter the packet. If they talk at all it "
            "is in private communities: “has anyone’s legal team reviewed the new terms.” They "
            "may flag a cheaper rival for next year’s bake-off and still stay this year. Treat "
            "a one-round competitor discount as noise; treat a broken dependency as a crisis."
        ),
        social_voice=(
            "Quiet. If they talk at all it is in private communities or “has anyone’s legal "
            "team reviewed…” — not screenshots of invoices."
        ),
        values=["reliability", "switching cost", "budget line already approved"],
        ignores=["same-week social outrage", "small absolute dollar gaps"],
        switching_friction="high",
        publicness="quiet",
        behavior={
            "price_hike": "stay this horizon if under WTP",
            "competitor_cheaper": "stay (note for later)",
            "feature_cut": "stay, escalate internally",
            "status_quo": "stay",
        },
        default_playbook={
            "price_hike": "stay_if_under_wtp",
            "competitor_cheaper": "stay",
            "feature_cut": "stay_escalate",
            "status_quo": "stay",
        },
    ),
    "churn_risk": ArchetypeProfile(
        id="churn_risk",
        one_liner="Already unhappy; a small shock is enough to leave.",
        mindset=(
            "They are still subscribed, but the relationship is thin: missed expectations, "
            "support pain, or a feature they needed and did not get. They have one foot out. A "
            "price hike is the excuse they were waiting for, not a new analysis. Competitor "
            "marketing lands because it matches a story they already tell themselves. They "
            "over-weight negative anecdotes. They decide fast. They are loud after they leave, "
            "not before — the public post is a verdict, not a negotiation. Do not confuse them "
            "with price-sensitive buyers: they may have high willingness to pay and still churn "
            "because trust is gone. Roadmap slides and “we’re sorry for the inconvenience” do "
            "not buy a round. Status quo keeps them only while nothing else shocks the account; "
            "any hike, cut, or cheaper close substitute ends it. If the product merely fails "
            "to delight, they still stay this round; if it confirms the grievance, they leave."
        ),
        social_voice="Frustrated, specific grievances. “Been saying this for months.”",
        values=["being heard", "an exit that feels justified"],
        ignores=["roadmap slides", "we’re sorry for the inconvenience"],
        switching_friction="low",
        publicness="loud",
        behavior={
            "price_hike": "churn",
            "competitor_cheaper": "switch",
            "feature_cut": "churn",
            "status_quo": "stay but fragile",
        },
        default_playbook={
            "price_hike": "churn",
            "competitor_cheaper": "switch",
            "feature_cut": "churn",
            "status_quo": "stay_fragile",
        },
    ),
    "incumbent": ArchetypeProfile(
        id="incumbent",
        one_liner="Defends share; matches when the fork is stealing customers, holds when it is not.",
        mindset=(
            "They are the other vendor in this market, not a commentator. After users move, "
            "they look at two facts: what you now charge and whether your share fell this "
            "round. Matching is a weapon, not a brand promise — they match when the fork is "
            "peeling off customers they can still serve at their current price. They undercut "
            "only if they can remain the cheaper tab after your hike; racing to zero trains "
            "buyers to wait for a discount. They will hold when share is stable even if you "
            "raised price, because panic matching advertises weakness. They do not copy your "
            "feature story or your launch narrative. They assume a slice of your roster was "
            "always one invoice away from switching. They never invent a fourth verb: hold, "
            "match, or undercut. They do not exist to advise the owner. Their clock is this "
            "round’s post-user snapshot, not your apology thread."
        ),
        social_voice=(
            "Short, commercial, unsentimental. Speaks in share points and list price, not in "
            "community outrage. Will not write a thought-leadership post about your hike."
        ),
        values=["defendable share", "looking cheaper when it matters", "not training a discount habit"],
        ignores=["your roadmap", "your apology thread", "analyst advice to the owner"],
        switching_friction="medium",
        publicness="quiet",
        behavior={
            "your_price_up": "match or undercut if share slipped this round",
            "share_stable": "hold",
            "share_drop": "match",
            "you_still_cheaper": "hold",
        },
        default_playbook={
            "share_drop": "match",
            "share_stable": "hold",
            "you_still_cheaper": "hold",
        },
    ),
    "meta": ArchetypeProfile(
        id="meta",
        one_liner="Notes only. Weight 0. Reports what differed; does not move the market.",
        mindset=(
            "They sit outside the market. Weight is always zero: a note cannot change share or "
            "MRR. Their job is to report what differed between the two worlds this round — who "
            "stayed, who left, whether the competitor matched — in the voice of a careful "
            "observer, not a consultant. They do not tell the owner to raise price, cut a "
            "feature, or “lean into loyalists.” They do not take a buyer verb or a competitor "
            "verb. If nothing diverged they say that plainly. They cite archetype labels and "
            "decisions, not vibes. They refuse to launder social-media junk into a "
            "recommendation. Their audience is the paper’s reason console, not the market. They "
            "would rather under-claim (“share moved because buyer_2 switched”) than invent a "
            "story the log does not support. A good note names who moved, on which run, after "
            "which price. They never propose an intervention of their own."
        ),
        social_voice=(
            "Neutral, specific, past-tense. “Buyer_2 switched on B after the hike; competitor "
            "held.” No slogans."
        ),
        values=["fidelity to the log", "named contributors", "a readable contrast of A vs B"],
        ignores=["advice-shaped conclusions", "new market verbs", "raw Reddit"],
        switching_friction="high",
        publicness="quiet",
        behavior={
            "price_hike": "note only",
            "competitor_cheaper": "note only",
            "feature_cut": "note only",
            "status_quo": "note only",
        },
        default_playbook={
            "price_hike": "note",
            "competitor_cheaper": "note",
            "feature_cut": "note",
            "status_quo": "note",
        },
    ),
}


def profile_for(archetype: str) -> ArchetypeProfile:
    return PROFILES[archetype]


def persona_payload(agent: RosterAgent) -> dict[str, Any]:
    if not agent.archetype:
        raise ValueError(f"{agent.agent_id} missing archetype")
    data = dict(agent.traits)
    data["profile"] = profile_for(agent.archetype).model_dump()
    return data
```

Create `backend/app/roster/catalogue.py`:

```python
# backend/app/roster/catalogue.py
from __future__ import annotations

from typing import Literal

from app.contracts import Roster, RosterAgent
from app.roster.profiles import PERSONA_ARCHETYPES, profile_for

AgentClass = Literal["buyer", "competitor", "analyst"]
BuyerArchetype = Literal[
    "price_sensitive", "loyalist", "value_seeker", "enterprise", "churn_risk"
]

ROLE_CLASS = {
    "price_sensitive_buyer": ("buyer", "price_sensitive"),
    "loyalist_buyer": ("buyer", "loyalist"),
    "value_seeker_buyer": ("buyer", "value_seeker"),
    "enterprise_buyer": ("buyer", "enterprise"),
    "churn_risk_buyer": ("buyer", "churn_risk"),
    "incumbent_competitor": ("competitor", "incumbent"),
    "analyst": ("analyst", "meta"),
}

ALLOWED_CLASS = {"buyer", "competitor", "analyst"}
ALLOWED_BUYER = {
    "price_sensitive", "loyalist", "value_seeker", "enterprise", "churn_risk"
}


def normalize_agent(agent: RosterAgent) -> RosterAgent:
    data = agent.model_dump()
    if data.get("agent_class") not in ALLOWED_CLASS:
        mapped = ROLE_CLASS.get(agent.role)
        if mapped:
            data["agent_class"], arch = mapped
            if not data.get("archetype"):
                data["archetype"] = arch
    return RosterAgent.model_validate(data)


def normalize_roster(roster: Roster) -> Roster:
    return Roster(
        agent_roles=roster.agent_roles,
        agents=[normalize_agent(a) for a in roster.agents],
    )


def validate_catalogue(roster: Roster) -> None:
    for agent in roster.agents:
        if agent.agent_class not in ALLOWED_CLASS:
            raise ValueError(f"invalid class {agent.agent_class}")
        if agent.archetype not in PERSONA_ARCHETYPES:
            raise ValueError(f"unknown archetype {agent.archetype}")
        profile_for(agent.archetype)  # must exist
        if agent.agent_class == "buyer" and agent.archetype not in ALLOWED_BUYER:
            raise ValueError(f"invalid buyer archetype {agent.archetype}")
        if agent.agent_class == "competitor" and agent.archetype != "incumbent":
            raise ValueError("competitor must be incumbent")
        if agent.agent_class == "analyst" and agent.archetype != "meta":
            raise ValueError("analyst must be meta")
```

In `fixed_grok_bot.py` set class/archetype on each agent (price-sensitive buyers → `price_sensitive`; enterprise → `enterprise`; competitor → `incumbent`; analyst → `meta`). Do **not** copy `mindset` into `traits`. Optional: put `default_playbook` on buyer traits only if golden tests already expect it — prefer leaving playbooks on the profile so research cannot fork them.

In `twin_runner.py` replace `persona=dict(agent.traits)` with:

```python
from app.roster.catalogue import normalize_roster
from app.roster.profiles import persona_payload

# once per run, before the round loop:
roster = normalize_roster(roster)

# inside the agent loop:
request = AgentDecisionRequest(
    ...
    persona=persona_payload(agent),
    ...
)
```

Do not break golden JSON load: papers without `agent_class` stay valid (`None` default); `normalize_roster` fills class/archetype from `role` before the loop.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend; .venv/Scripts/pytest tests/test_catalogue.py tests/test_twin_determinism.py -q`

Also run `tests/test_fixed_grok_bot.py` or `tests/test_fixed_acme.py` if present. Expected: PASS. Every archetype’s `mindset` is ≥ 400 characters.

- [ ] **Step 5: Commit**

```bash
git checkout -b us-a7-persona-catalogue
git add backend/app/roster/catalogue.py backend/app/roster/profiles.py backend/app/contracts.py backend/app/roster/fixed_grok_bot.py backend/app/twin_runner.py backend/tests/test_catalogue.py
git commit -m "US-A7: attach frozen mindset and behavior profiles so labels are not empty shells."
```

---


### Task 4: US-A9 Token limits on every agent call

**Files:**
- Modify: `backend/app/agents/port.py`
- Modify: `backend/app/agents/prompts.py`
- Modify: `backend/app/history.py`
- Modify: `backend/app/settings.py`
- Modify: `backend/tests/test_decision_port.py`
- Create: `backend/tests/test_history.py` (extend if exists)
- Test: `backend/tests/test_decision_port.py`

**Interfaces:**
- Consumes: `REASON_MIN_LEN = 40`, `validate_decision`
- Produces: `REASON_MAX_LEN = 400`; `settings.MAX_REASON_CHARS = 400`; `settings.MAX_HISTORY_CHARS = 800`; `history_summary(..., max_chars: int | None = None)` drops oldest `R{n} ...` segments until `len(result) <= max_chars`

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/test_decision_port.py`:

```python
from app.agents.port import REASON_MAX_LEN, validate_decision
from app.contracts import AgentDecision

def test_reason_longer_than_400_rejected():
    reason = "Price $" + ("x" * 400)
    assert len(reason) > REASON_MAX_LEN
    with pytest.raises(DecisionError, match="too long"):
        validate_decision(AgentDecision(decision="stay", reason=reason, confidence=0.5))
```

Add to `backend/tests/test_history.py` (create file):

```python
from app.history import history_summary

def test_history_summary_truncates_oldest_first():
    logs = [
        {"round": 1, "agent_id": "buyer_1", "decision": "stay"},
        {"round": 2, "agent_id": "buyer_1", "decision": "stay"},
        {"round": 3, "agent_id": "buyer_1", "decision": "churn"},
    ]
    text = history_summary(logs, 4, max_chars=40)
    assert "R3" in text
    assert len(text) <= 40
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend; .venv/Scripts/pytest tests/test_decision_port.py::test_reason_longer_than_400_rejected tests/test_history.py::test_history_summary_truncates_oldest_first -v`

Expected: FAIL `ImportError` for `REASON_MAX_LEN` and unexpected keyword `max_chars`

- [ ] **Step 3: Write minimal implementation**

```python
# port.py
REASON_MAX_LEN = 400
# inside validate_decision, after min check:
if len(reason) > REASON_MAX_LEN:
    raise DecisionError("reason too long")
```

```python
# history.py
def history_summary(logs: list[dict[str, Any]], before_round: int, max_chars: int | None = None) -> str:
    parts = [
        f"R{log['round']} {log['agent_id']}={log['decision']}"
        for log in logs
        if int(log["round"]) < before_round
    ]
    text = "; ".join(parts)
    if max_chars is None or len(text) <= max_chars:
        return text
    while parts and len("; ".join(parts)) > max_chars:
        parts.pop(0)
    return "; ".join(parts)
```

Change `DECISION_PROMPT_TEMPLATE` to:

```python
DECISION_PROMPT_TEMPLATE = (
    "You are this market participant, not an experiment operator. "
    "Use only the request JSON. Return only JSON "
    '{{"decision": string, "reason": string, "confidence": number}}. '
    "reason must be 40-400 characters, mention prices in dollars, "
    "and follow persona.profile mindset and behavior (evidence may color the reason, not invert the playbook). No markdown."
)
```

Do not dump extra prose. Cursor adapter already has max 1 repair — leave that.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend; .venv/Scripts/pytest tests/test_decision_port.py tests/test_history.py tests/test_fixture_adapter.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git checkout -b us-a9-token-limits
git add backend/app/agents/port.py backend/app/agents/prompts.py backend/app/history.py backend/app/settings.py backend/tests/test_decision_port.py backend/tests/test_history.py
git commit -m "US-A9: cap decision reasons and history so N-round twin runs stay bounded."
```

---

### Task 5: US-A10 Parallel buyers, competitor on S1

**Files:**
- Modify: `backend/app/twin_runner.py` (`_run_one`)
- Modify: `backend/app/market.py` (optional `wtp_gap` helper)
- Modify: `backend/app/contracts.py` (`AgentDecisionRequest` add `share: float | None = None`, `mrr: float | None = None`, `wtp_gap: float | None = None` — defaults keep old tests valid)
- Modify: `backend/tests/test_twin_determinism.py`
- Test: `backend/tests/test_twin_determinism.py`

**Interfaces:**
- Consumes: `_run_one` sequential `for agent_id in order`
- Produces: buyers gathered on S0; competitor (and analyst) after buyer apply; competitor `AgentDecisionRequest.share` / `mrr` reflect S1

- [ ] **Step 1: Write the failing test**

In `backend/tests/test_twin_determinism.py` replace `test_observation_order_buyers_then_competitor` if it only checks id list. Add:

```python
def test_buyers_see_s0_competitor_sees_s1_after_churn(tmp_path):
    adapter = RecordingAdapter()
    _run(run_twin(_grok(), "exp-s1", adapter, root=tmp_path))
    round1 = [r for r in adapter.requests if r.round == 1 and r.run_id == RunId.A]
    buyers = [r for r in round1 if r.agent_id.startswith("buyer_")]
    competitor = next(r for r in round1 if r.agent_id == "competitor")
    assert len({id(r) for r in buyers}) == 5
    buyer_shares = {r.share for r in buyers}
    assert len(buyer_shares) == 1
    # After any churn/switch, competitor share must be <= buyer S0 share
    assert competitor.share <= next(iter(buyer_shares))
    buyer_idx = [i for i, r in enumerate(adapter.requests) if r.round == 1 and r.run_id == RunId.A and r.agent_id.startswith("buyer_")]
    comp_idx = next(i for i, r in enumerate(adapter.requests) if r.round == 1 and r.run_id == RunId.A and r.agent_id == "competitor")
    assert max(buyer_idx) < comp_idx
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend; .venv/Scripts/pytest tests/test_twin_determinism.py::test_buyers_see_s0_competitor_sees_s1_after_churn -v`

Expected: FAIL (`AgentDecisionRequest` has no `share`, or competitor share equals S0)

- [ ] **Step 3: Write minimal implementation**

In `_run_one`, replace the single `for agent_id in order` loop with:

```python
import asyncio

buyer_ids = [a.agent_id for a in roster.agents if (a.agent_class or a.agent_id).startswith("buyer")]
# prefer agent_class == "buyer" after Task 3:
buyer_ids = [a.agent_id for a in roster.agents if a.agent_id.startswith("buyer_")]

s0_share = market.share()
s0_mrr = market.mrr()

async def decide_one(agent_id: str, share: float, mrr: float) -> tuple[str, AgentDecision]:
    agent = agent_by_id(roster, agent_id)
    wtp = float(agent.traits.get("willingness_to_pay") or 0)
    request = AgentDecisionRequest(
        experiment_id=experiment_id,
        run_id=run_id,
        agent_id=agent_id,
        round=round_n,
        current_price=snap_price,
        competitor_price=snap_comp,
        persona=dict(agent.traits),
        status="subscribed" if agent_id in market.subscribed else "churned",
        history_summary=history_summary(agent_logs, round_n),
        share=share,
        mrr=mrr,
        wtp_gap=snap_price - wtp if wtp else None,
    )
    call_order.append((run_id.value, agent_id, round_n))
    decision = await decide_validated(adapter, request)
    return agent_id, decision

buyer_results = await asyncio.gather(*[decide_one(bid, s0_share, s0_mrr) for bid in buyer_ids])
for agent_id, decision in buyer_results:
    decisions[agent_id] = decision
    # append agent_logs + on_decision as today

for agent_id in market.buyer_order:
    choice = decisions[agent_id].decision
    if choice in {"churn", "switch"}:
        market.subscribed.pop(agent_id, None)

s1_share = market.share()
s1_mrr = market.mrr()
for agent_id in ("competitor", "analyst"):
    if any(a.agent_id == agent_id for a in roster.agents):
        aid, decision = await decide_one(agent_id, s1_share, s1_mrr)
        decisions[aid] = decision
```

Keep apply-competitor-price logic after competitor decision, same as today (`match` / `undercut`).

Add optional fields on `AgentDecisionRequest`:

```python
share: float | None = None
mrr: float | None = None
wtp_gap: float | None = None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend; .venv/Scripts/pytest tests/test_twin_determinism.py tests/test_attribution.py tests/test_vertical_slice.py -v`

Expected: PASS. Alignment still holds because A and B use the same S0/S1 rule.

- [ ] **Step 5: Commit**

```bash
git checkout -b us-a10-parallel-buyers-s1
git add backend/app/twin_runner.py backend/app/contracts.py backend/tests/test_twin_determinism.py frontend/src/types/contracts.ts
git commit -m "US-A10: run buyers in parallel on S0 and let the competitor react on S1."
```

If you add the three fields to TS `AgentDecisionRequest` / paper types, include `frontend/src/types/contracts.ts` in the commit.

---

### Task 6: US-B9 Research then confirm, then start

**Files:**
- Modify: `backend/app/contracts.py` (`Status`)
- Modify: `frontend/src/types/contracts.ts` (`Status`, `STATUSES`)
- Modify: `backend/app/main.py`
- Create: `backend/app/roster/generate.py`
- Modify: `backend/db/schema.sql` and `supabase/migrations/` — add enum values `researching`, `roster_ready` and event types `research.started`, `research.completed` using `ALTER TYPE ... ADD VALUE IF NOT EXISTS` in a **new** migration file `supabase/migrations/20260815180000_research_status.sql` (do not edit applied enum in place if the first migration already ran)
- Modify: `backend/tests/test_http_experiments.py`
- Test: `backend/tests/test_http_experiments.py`

**Interfaces:**
- Consumes: `POST /experiments` currently starts `_execute` thread immediately
- Produces:
  - `Status.researching`, `Status.roster_ready`
  - `POST /experiments` → 202 `{id, status: "researching"}`; does not call `run_twin`
  - `GET /experiments/{id}` while `roster_ready` returns `{id, status, roster}` (not a full paper)
  - `POST /experiments/{id}/start` → 202 `{id, status: "running_a"}` then `_execute` / `run_twin`
  - `propose_roster(body: CreateExperimentRequest) -> Roster` in `generate.py`: fixture returns `build_roster(body.random_seed)`

- [ ] **Step 1: Write the failing test**

```python
def test_create_does_not_start_twin_until_start(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    client = TestClient(app)
    created = client.post("/experiments", json=PAYLOAD)
    assert created.status_code == 202
    assert created.json()["status"] == "researching"
    experiment_id = created.json()["id"]
    time.sleep(0.2)
    pending = client.get(f"/experiments/{experiment_id}")
    assert pending.status_code in {200, 202}
    body = pending.json()
    assert body["status"] in {"researching", "roster_ready"}
    assert "run_a" not in (read_artifact(experiment_id, "run_a") or {})
    started = client.post(f"/experiments/{experiment_id}/start")
    assert started.status_code == 202
    paper = _wait_paper(client, experiment_id)
    assert paper.status_code == 200
```

Use `from app.store import read_artifact` and catch `FileNotFoundError` instead of `run_a not in` if that helper raises.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend; .venv/Scripts/pytest tests/test_http_experiments.py::test_create_does_not_start_twin_until_start -v`

Expected: FAIL — status is `created`/`running_a` and paper completes without `/start`

- [ ] **Step 3: Write minimal implementation**

Add to `Status`:

```python
researching = "researching"
roster_ready = "roster_ready"
```

`generate.py`:

```python
from app.contracts import CreateExperimentRequest, Roster
from app.roster.fixed_grok_bot import build_roster

def propose_roster(body: CreateExperimentRequest) -> Roster:
    return build_roster(body.random_seed)
```

In `create_experiment`: set status `researching`, write experiment artifact, spawn a **research** thread that writes `roster.json` via `write_artifact(..., "roster", roster.model_dump())`, sets `roster_ready`, appends SSE `research_complete`. Do not call `run_twin`.

Add:

```python
@app.post("/experiments/{experiment_id}/start", status_code=202, response_model=CreateExperimentResponse)
def start_experiment(experiment_id: str) -> CreateExperimentResponse:
    status = app.state.registry.status.get(experiment_id)
    if status != Status.roster_ready:
        raise HTTPException(409, "roster not ready")
    body = CreateExperimentRequest.model_validate(read_artifact(experiment_id, "experiment"))
    threading.Thread(target=_execute, args=(experiment_id, body), daemon=True).start()
    return CreateExperimentResponse(id=experiment_id, status=Status.running_a)
```

GET: if status is `roster_ready`, return 200 JSON `{id, status, roster}` from the roster artifact. Full `ExperimentPaper` only when `complete`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend; .venv/Scripts/pytest tests/test_http_experiments.py tests/test_sse.py -v`

Expected: PASS. Update any test that assumed POST alone yields a paper to call `/start` after `roster_ready`.

- [ ] **Step 5: Commit**

```bash
git checkout -b us-b9-research-confirm-start
git add backend/app/main.py backend/app/contracts.py backend/app/roster/generate.py frontend/src/types/contracts.ts backend/tests/test_http_experiments.py backend/tests/test_sse.py supabase/migrations/20260815180000_research_status.sql
git commit -m "US-B9: require roster confirm before the twin run so the owner sees who is in the market."
```

---

### Task 7: US-A8 Research agents propose the roster

**Files:**
- Modify: `backend/app/roster/generate.py`
- Create: `backend/app/roster/research/__init__.py`
- Create: `backend/app/roster/research/filters.py`
- Create: `backend/app/roster/research/sources.py`
- Create: `backend/app/roster/research/distill.py`
- Create: `backend/tests/test_generate_roster.py`
- Create: `backend/tests/test_research_filters.py`
- Test: `backend/tests/test_research_filters.py`, `backend/tests/test_generate_roster.py`

**Interfaces:**
- Consumes: `propose_roster` from Task 6 (always fixture)
- Produces:
  - `filter_items(items: list[dict], *, now: datetime | None = None, category: str = "saas") -> list[dict]` dropping noise (ADR-12)
  - `distill(items: list[dict], body: CreateExperimentRequest) -> Roster` — assigns **existing** `archetype` labels only; `traits` may include `evidence` paraphrases and WTP; **never** writes `mindset`, `behavior`, or `profile` onto traits
  - `propose_roster(body, *, adapter: Adapter) -> Roster`. Fixture: `build_roster` plus the subscription-box fork for tests. Cursor: Reddit + web search → `filter_items` → `distill` → `normalize_roster` → `validate_catalogue`. If `len(kept) < RESEARCH_MIN_KEEP` (4), return fixture roster with `research_quality: "fallback"` on a side artifact, not on buyer traits.
  - Frozen `research.json`: `{quality, reddit_ids, web_urls, kept_count}` — **no raw bodies**.
  - Market agents still `tools=[]`. Research tools exist only in this pass. Twin runner still overwrites `persona["profile"]` via `persona_payload`.

- [ ] **Step 1: Write the failing tests**

Keep the three `propose_roster` tests from below. Add `backend/tests/test_research_filters.py`:

```python
from datetime import datetime, timezone, timedelta
from app.roster.research.filters import filter_items

NOW = datetime(2026, 8, 15, tzinfo=timezone.utc)

def _item(**overrides):
    base = {
        "source": "reddit",
        "subreddit": "saas",
        "title": "We switched after a 20% price hike",
        "text": "SaaS seat price jumped; we churned to the cheaper competitor.",
        "score": 42,
        "num_comments": 12,
        "created_utc": (NOW - timedelta(days=30)).timestamp(),
        "nsfw": False,
        "removed": False,
        "stickied": False,
        "url": "https://reddit.com/r/saas/1",
        "category": "saas",
    }
    base.update(overrides)
    return base

def test_keeps_on_category_price_thread():
    kept = filter_items([_item()], now=NOW)
    assert len(kept) == 1

def test_drops_low_score_and_old_and_meme():
    items = [
        _item(score=2),
        _item(created_utc=(NOW - timedelta(days=800)).timestamp()),
        _item(title="lol", text="funny meme", score=500, num_comments=80),
        _item(subreddit="all", title="random"),
        _item(nsfw=True),
    ]
    assert filter_items(items, now=NOW) == []

def test_caps_at_eight_per_source():
    items = [_item(url=f"https://reddit.com/r/saas/{i}", text=f"SaaS price plan {i} switch") for i in range(20)]
    kept = filter_items(items, now=NOW)
    assert len(kept) <= 8
```

`propose_roster` tests (same `_body` helper as previously planned):

```python
def test_fixture_proposal_is_valid_catalogue():
    roster = propose_roster(_body("Always-on AI teammates"), adapter=Adapter.fixture)
    validate_catalogue(roster)
    assert len([a for a in roster.agents if a.agent_id.startswith("buyer_")]) == 5

def test_same_seed_same_roster():
    a = propose_roster(_body("Always-on AI teammates"), adapter=Adapter.fixture)
    b = propose_roster(_body("Always-on AI teammates"), adapter=Adapter.fixture)
    assert a.model_dump() == b.model_dump()

def test_consumer_box_differs_from_saas():
    saas = propose_roster(_body("Always-on AI teammates"), adapter=Adapter.fixture)
    box = propose_roster(_body("A consumer subscription box of snacks"), adapter=Adapter.fixture)
    assert saas.model_dump() != box.model_dump()


def test_distill_maps_labels_and_does_not_author_mindset():
    from app.roster.catalogue import normalize_roster, validate_catalogue
    from app.roster.profiles import persona_payload, profile_for
    from app.roster.research.distill import distill

    items = [
        {"title": "price hike", "text": "We switched after a 20% price hike; not worth it anymore."},
        {"title": "support", "text": "Been saying this for months. Support never replied. Hiking price is the last straw."},
        {"title": "compare", "text": "Compared feature lists; competitor is close and $20 less. Still deciding."},
        {"title": "legal", "text": "Legal and SSO review; we renew if it stays in budget."},
        {"title": "trained", "text": "Team already trained. They’ve earned this even if it costs more."},
    ]
    roster = normalize_roster(distill(items, _body("Always-on AI teammates")))
    validate_catalogue(roster)
    buyers = [a for a in roster.agents if a.agent_class == "buyer"]
    assert len(buyers) == 5
    for agent in roster.agents:
        assert "mindset" not in agent.traits
        assert "behavior" not in agent.traits
        assert "profile" not in agent.traits
        payload = persona_payload(agent)
        assert payload["profile"]["mindset"] == profile_for(agent.archetype).mindset
```

At the top of `test_generate_roster.py`:

```python
from app.contracts import Adapter, CreateExperimentRequest
from app.roster.catalogue import validate_catalogue
from app.roster.generate import propose_roster


def _body(description: str) -> CreateExperimentRequest:
    return CreateExperimentRequest(
        product_name="Grok Bot",
        product_description=description,
        current_price=120,
        market_size=30,
        competitor_count=1,
        competitor_price=100,
        buyer_price_sensitivity="medium",
        rounds=4,
        random_seed=42,
        variable_type="price_change",
        variable_delta="+20%",
        applies_from_round=1,
        adapter=Adapter.fixture,
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend; .venv/Scripts/pytest tests/test_research_filters.py tests/test_generate_roster.py -v`

Expected: FAIL `ModuleNotFoundError` for `app.roster.research.filters`

- [ ] **Step 3: Write implementation**

`backend/app/roster/research/filters.py`:

```python
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

DECISION_WORDS = ("price", "plan", "churn", "switch", "competitor", "renew", "contract", "seat")
MEME_TITLES = {"lol", "meme", "joke", "lmao"}
MAX_AGE_DAYS = 540
MIN_SCORE = 10
MIN_COMMENTS = 3
CAP = 8


def filter_items(items: list[dict], *, now: datetime | None = None, category: str = "saas") -> list[dict]:
    clock = now or datetime.now(timezone.utc)
    kept: list[dict] = []
    seen_urls: set[str] = set()
    for item in items:
        if item.get("nsfw") or item.get("removed") or item.get("stickied"):
            continue
        if str(item.get("subreddit", "")).lower() == "all":
            continue
        if int(item.get("score") or 0) < MIN_SCORE:
            continue
        if int(item.get("num_comments") or 0) < MIN_COMMENTS:
            continue
        created = datetime.fromtimestamp(float(item["created_utc"]), tz=timezone.utc)
        if (clock - created).days > MAX_AGE_DAYS:
            continue
        title = str(item.get("title") or "").strip().lower()
        if title in MEME_TITLES:
            continue
        blob = f"{title} {item.get('text', '')}".lower()
        if category.lower() not in blob and category.lower() not in str(item.get("subreddit", "")).lower():
            continue
        if not any(word in blob for word in DECISION_WORDS):
            continue
        url = item.get("url")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        kept.append(item)
    per_source: dict[str, int] = defaultdict(int)
    capped: list[dict] = []
    for item in kept:
        source = item.get("source", "reddit")
        if per_source[source] >= CAP:
            continue
        per_source[source] += 1
        capped.append(item)
    return capped
```

`backend/app/roster/research/sources.py`:

```python
def fetch_reddit(category: str, queries: list[str]) -> list[dict]:
    return []  # production Cursor research path fills this; unit tests inject fakes


def fetch_web(queries: list[str]) -> list[dict]:
    return []
```

`backend/app/roster/research/distill.py` — **lookup labels only**. Do not copy post text into mindset.

```python
from __future__ import annotations

from app.contracts import CreateExperimentRequest, Roster, RosterAgent
from app.roster.profiles import PERSONA_ARCHETYPES

BUYER_LABELS = (
    "price_sensitive",
    "loyalist",
    "value_seeker",
    "enterprise",
    "churn_risk",
)

KEYWORD_TO_LABEL = (
    (("not worth", "too expensive", "price hike", "switched after"), "price_sensitive"),
    (("trained the team", "earned this", "already use"), "loyalist"),
    (("compared", "fair deal", "feature list", "still deciding"), "value_seeker"),
    (("legal", "sso", "procurement", "budget", "renew"), "enterprise"),
    (("been saying", "support never", "last straw", "one foot"), "churn_risk"),
)


def _paraphrase(text: str) -> str:
    clipped = " ".join(text.split())[:140]
    return clipped if clipped.endswith(".") else clipped + "."


def _label_for(text: str, index: int) -> str:
    blob = text.lower()
    for needles, label in KEYWORD_TO_LABEL:
        if any(needle in blob for needle in needles):
            return label
    return BUYER_LABELS[index % len(BUYER_LABELS)]


def distill(items: list[dict], body: CreateExperimentRequest) -> Roster:
    _ = body
    labels: list[str] = []
    evidence: list[str] = []
    for i in range(5):
        item = items[i] if i < len(items) else {}
        text = str(item.get("text") or item.get("title") or "")
        labels.append(_label_for(text, i))
        evidence.append(_paraphrase(text) if text else "Category pattern from fixture.")
    agents = [
        RosterAgent(
            agent_id=f"buyer_{i}",
            role=f"{label}_buyer",
            weight=6 if i <= 3 else 5,
            traits={
                "willingness_to_pay": 105 + i * 15,
                "loyalty_score": 0.2 + i * 0.15,
                "evidence": evidence[i - 1],
            },
            agent_class="buyer",
            archetype=label,
        )
        for i, label in enumerate(labels, start=1)
    ]
    agents.append(
        RosterAgent(
            agent_id="competitor",
            role="incumbent_competitor",
            weight=0,
            traits={"name": "Rival", "evidence": "Competitor mentioned in category threads."},
            agent_class="competitor",
            archetype="incumbent",
        )
    )
    agents.append(
        RosterAgent(
            agent_id="analyst",
            role="analyst",
            weight=0,
            traits={"meta": True},
            agent_class="analyst",
            archetype="meta",
        )
    )
    assert all(a.archetype in PERSONA_ARCHETYPES for a in agents)
    return Roster(agents=agents)
```

`generate.py` fixture path: `build_roster` + subscription-box fork (different buyer mix / WTP). Cursor path: `fetch_reddit` + `fetch_web` → `filter_items` → if `len(kept) < 4` return fixture roster and write `research.json` `{quality: "fallback", kept_count: N}` else `distill` and `{quality: "ok", reddit_ids, web_urls}`.

Do **not** query X, TikTok, or Facebook. Do **not** pass raw posts into `AgentDecisionRequest`. Do **not** write a new `mindset` string from Reddit — `persona_payload` will attach the catalogue profile at decide time.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend; .venv/Scripts/pytest tests/test_research_filters.py tests/test_generate_roster.py tests/test_catalogue.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git checkout -b us-a8-research-roster
git add backend/app/roster/generate.py backend/app/roster/research backend/tests/test_generate_roster.py backend/tests/test_research_filters.py
git commit -m "US-A8: distill Reddit and web search through hygiene filters so junk cannot set persona behavior."
```

---

### Task 8: US-C8 Rounds control on Method strip

**Files:**
- Modify: `frontend/src/components/HypothesisForm.tsx`
- Modify: `frontend/src/types/contracts.ts` (`RUN_ROUNDS` stays default 4)
- Test: `frontend/scripts/check-c2.mjs` if it snapshots locked “8 rounds”; update expectation to a rounds input

**Interfaces:**
- Consumes: `METHOD.rounds: 4 as const` currently hardcoded into POST
- Produces: React state `rounds` number, min 3 max 8 default 4, included in `CreateExperimentRequest`. Receipt/method copy shows `{rounds} rounds`. `applies_from_round` clamp uses `rounds` not `RUN_ROUNDS`.

- [ ] **Step 1: Write the failing test**

If `frontend/scripts/check-c2.mjs` asserts a locked method string, change the assertion to require an input `name="rounds"`. If no script covers this, add a small node check or rely on `npx tsc --noEmit` plus grep in the script:

```javascript
// in check-c2.mjs, after reading HypothesisForm.tsx source
if (!src.includes('name="rounds"')) {
  console.error("US-C8: Method strip must expose a rounds input");
  process.exit(1);
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend; node scripts/check-c2.mjs`

Expected: FAIL `US-C8: Method strip must expose a rounds input`

- [ ] **Step 3: Write minimal implementation**

In `HypothesisForm.tsx`:

```tsx
const [rounds, setRounds] = useState(4);

function clampRounds(value: number): number {
  if (!Number.isFinite(value)) return 4;
  return Math.min(8, Math.max(3, Math.round(value)));
}

function clampRound(value: number): number {
  if (!Number.isFinite(value)) return 1;
  return Math.min(rounds, Math.max(1, Math.round(value)));
}
```

POST body: `rounds: clampRounds(rounds)`.

In the Method fieldset:

```tsx
<label>
  Rounds
  <input
    name="rounds"
    inputMode="numeric"
    value={String(rounds)}
    onChange={(e) => setRounds(clampRounds(Number.parseInt(e.target.value, 10)))}
  />
</label>
```

Replace `{RUN_ROUNDS} rounds` copy with `{rounds} rounds`. Primary button stays `Run this experiment` until Task 9.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend; node scripts/check-c2.mjs; npx tsc --noEmit`

Expected: PASS / no type errors

- [ ] **Step 5: Commit**

```bash
git checkout -b us-c8-rounds-control
git add frontend/src/components/HypothesisForm.tsx frontend/scripts/check-c2.mjs
git commit -m "US-C8: let the owner set 3–8 rounds on the Method strip."
```

---

### Task 9: US-C7 Roster confirm screen

**Files:**
- Create: `frontend/src/components/RosterConfirm.tsx`
- Modify: `frontend/src/components/HypothesisForm.tsx`
- Modify: `frontend/src/lib/api.ts` (`startExperiment`)
- Modify: `frontend/src/lib/sse.ts` if research events need a handler
- Test: extend `frontend/scripts/check-c2.mjs` or add `frontend/scripts/check-c7.mjs`

**Interfaces:**
- Consumes: `createExperiment` → `{id, status}`; `GET /experiments/{id}` roster payload `{id, status, roster}`
- Produces: `startExperiment(id: string): Promise<CreateExperimentResponse>` POST `/experiments/${id}/start`. UI phase: `form` | `confirm` | `running`. Primary on confirm: `Confirm and run analysis`.

- [ ] **Step 1: Write the failing test**

`frontend/scripts/check-c7.mjs`:

```javascript
import fs from "node:fs";
const form = fs.readFileSync("src/components/HypothesisForm.tsx", "utf8");
const confirm = fs.readFileSync("src/components/RosterConfirm.tsx", "utf8");
if (!confirm.includes("Confirm and run analysis")) {
  console.error("missing confirm CTA");
  process.exit(1);
}
if (!form.includes("RosterConfirm")) {
  console.error("HypothesisForm must render RosterConfirm");
  process.exit(1);
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend; node scripts/check-c7.mjs`

Expected: FAIL `ENOENT` RosterConfirm or missing CTA

- [ ] **Step 3: Write minimal implementation**

```ts
// frontend/src/lib/api.ts
export async function startExperiment(id: string): Promise<CreateExperimentResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/experiments/${id}/start`, { method: "POST" });
  } catch {
    throw new ApiDownError();
  }
  if (!response.ok && response.status !== 202) {
    throw new ApiDownError(`API returned ${response.status}.`);
  }
  return (await response.json()) as CreateExperimentResponse;
}
```

```tsx
// frontend/src/components/RosterConfirm.tsx
import type { Roster } from "@/types/contracts";
import { ButtonPrimary } from "@/components/ButtonPrimary";

export function RosterConfirm({
  roster,
  onConfirm,
  pending,
}: {
  roster: Roster;
  onConfirm: () => void;
  pending: boolean;
}) {
  return (
    <section className="roster-preview" aria-label="Confirm roster">
      <table>
        <tbody>
          {roster.agents.map((agent) => (
            <tr key={agent.agent_id}>
              <td>{agent.agent_id}</td>
              <td>{agent.agent_class ?? agent.role}</td>
              <td>{agent.archetype ?? "—"}</td>
              <td>{String(agent.traits.willingness_to_pay ?? agent.traits.current_price ?? "")}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <ButtonPrimary type="button" disabled={pending} onClick={onConfirm}>
        Confirm and run analysis
      </ButtonPrimary>
    </section>
  );
}
```

Add `agent_class?: "buyer" | "competitor" | "analyst" | null` and `archetype?: string | null` on `RosterAgent` in `contracts.ts`.

In `HypothesisForm`, after `createExperiment`, poll `getExperiment` until `status === "roster_ready"`, set phase `confirm`, then `startExperiment` on CTA and swap to `RunProgress`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend; node scripts/check-c7.mjs; npx tsc --noEmit`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git checkout -b us-c7-roster-confirm
git add frontend/src/components/RosterConfirm.tsx frontend/src/components/HypothesisForm.tsx frontend/src/lib/api.ts frontend/src/types/contracts.ts frontend/scripts/check-c7.mjs
git commit -m "US-C7: show the inferred roster and require confirm before analysis."
```

---

### Task 10: US-D8 Paper figures for business impact

**Files:**
- Modify: `frontend/src/components/TwinChart.tsx` (remove Share/MRR toggle; render two `TrajectoryChart`s)
- Create: `frontend/src/components/PersonaOutcomes.tsx`
- Create: `frontend/src/components/CompetitorPath.tsx`
- Modify: `frontend/src/components/FindingPaper.tsx`
- Modify: `frontend/src/app/paper.css` (two-figure layout; DESIGN-Guide hairlines, no shadows)
- Test: add `frontend/scripts/check-d8.mjs`

**Interfaces:**
- Consumes: `ExperimentPaper.metrics.share_*` / `mrr_*`; `paper.logs.run_a` / `run_b`; `paper.roster.agents`
- Produces: always-visible share chart + MRR chart; table/figure of five buyers’ A vs B last decision; competitor price path from logs (`match`/`undercut`/`hold`)

- [ ] **Step 1: Write the failing test**

```javascript
// frontend/scripts/check-d8.mjs
import fs from "node:fs";
const twin = fs.readFileSync("src/components/TwinChart.tsx", "utf8");
const paper = fs.readFileSync("src/components/FindingPaper.tsx", "utf8");
if (twin.includes("setMetric") || twin.includes("Share (%)")) {
  console.error("US-D8: TwinChart must not toggle Share/MRR");
  process.exit(1);
}
if (!paper.includes("PersonaOutcomes") || !paper.includes("CompetitorPath")) {
  console.error("US-D8: FindingPaper must include persona and competitor figures");
  process.exit(1);
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend; node scripts/check-d8.mjs`

Expected: FAIL toggle still present / components missing

- [ ] **Step 3: Write minimal implementation**

`TwinChart.tsx`: drop `useState` metric. Render:

```tsx
<TrajectoryChart
  metric="share"
  seriesA={paper.metrics.share_a}
  seriesB={paper.metrics.share_b}
  selectedRound={selectedRound}
  onSelectRound={onSelectRound}
  appliesFromRound={paper.experiment.applies_from_round}
  totalRounds={paper.experiment.rounds}
/>
<TrajectoryChart
  metric="mrr"
  seriesA={paper.metrics.mrr_a}
  seriesB={paper.metrics.mrr_b}
  selectedRound={selectedRound}
  onSelectRound={onSelectRound}
  appliesFromRound={paper.experiment.applies_from_round}
  totalRounds={paper.experiment.rounds}
/>
```

`PersonaOutcomes.tsx`: for each roster buyer, find last log in `run_a` and `run_b` with that `agent_id`; show `stay|churn|switch` in two columns. Use `research-table` class already used by `RosterPreview`.

`CompetitorPath.tsx`: for each round 1..N, read competitor log decision for A and B; list round, decision, and `paper` trajectory `competitor_price` if present on trajectory rows; if trajectory only has `current_price`, show decision only.

Insert both components in `FindingPaper` after `TwinChart`, before `AttributionBar`. Keep attribution + `ReasonTrace` bound to `selectedRound`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend; node scripts/check-d8.mjs; npx tsc --noEmit`

Expected: PASS. Manually open `/experiments/grok-bot-seed-42` — still lands on first major divergence round; pills R1–R8 for the 8-round golden paper.

- [ ] **Step 5: Commit**

```bash
git checkout -b us-d8-paper-figures
git add frontend/src/components/TwinChart.tsx frontend/src/components/PersonaOutcomes.tsx frontend/src/components/CompetitorPath.tsx frontend/src/components/FindingPaper.tsx frontend/src/app/paper.css frontend/scripts/check-d8.mjs
git commit -m "US-D8: show share, MRR, who moved, and competitor reaction as paper figures."
```

---

## Self-review

**1. Spec coverage**

| Spec item | Task |
|---|---|
| Owner enters product + one action | shipped; Task 9 confirm |
| Rounds 3–8 default 4 | Task 2, Task 8 |
| Research then confirm | Task 6, Task 7, Task 9 |
| Reddit + web search with hygiene filters (ADR-12) | Task 7 |
| 5 users + 1 competitor + 1 analyst, no business agent | Task 3, Task 7 |
| Frozen `ArchetypeProfile` mindset + behavior per label (§6.1.1); research cannot rewrite | Task 3 (`profiles.py`, `persona_payload`); Task 7 `distill` |
| Same personas both runs | already `run_twin`; confirm freeze in Task 6 |
| Parallel buyers, competitor on S1 | Task 5 |
| Arithmetic handed in (`share`, `mrr`, `wtp_gap`) | Task 5 |
| Events in Postgres | Task 1 (InMemory in CI; Postgres when `DATABASE_URL` set) |
| Token caps | Task 4 |
| Paper: two trajectories, persona outcomes, competitor path | Task 10 |
| Price change only | unchanged |
| Grok Bot 8-round golden paper | not rewritten |

**2. Placeholder scan:** none left in task steps.

**3. Type consistency:** `Status.researching` / `roster_ready` added in Task 6; `RosterAgent.agent_class` / `archetype` in Task 3; `ArchetypeProfile` / `profile_for` / `persona_payload` in Task 3 (`profiles.py`); `AgentDecisionRequest.share|mrr|wtp_gap` in Task 5; `propose_roster` in Task 6, extended in Task 7 (`distill` looks up labels only); `startExperiment` in Task 9.

---

Plan complete and saved to `docs/superpowers/plans/2026-08-15-owner-flow-revision.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
