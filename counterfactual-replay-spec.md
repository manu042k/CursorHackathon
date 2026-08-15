# Counterfactual Replay — Causal Attribution for Business Decisions
### Technical build spec — Grok 4.6 + Cursor, one-day build

---

## 1. One-line pitch

Given a business decision under consideration (a price change, a competitor move, a spend cut), run the same set of Grok 4.6-driven agents twice — identical seed, identical starting state, exactly one variable changed — and produce a **causally attributable** account of what that one change did, down to which agent decision caused how much of the divergence.

This is not a market forecast. It is an **interactive causal paper** for decisions you cannot A/B test: fork a frozen market, change exactly one variable, and name the agents who caused the divergence. The unit of value is a decision they can take to a board, not a predicted number.

The claim that matters: this is not prediction, and it is not correlation. It is a controlled experiment. Everything held constant except one variable means any difference between Run A and Run B is caused by that variable, **by construction** — Pearl’s do-operator, not a correlation mined after the fact. Say that in the first 20 seconds. Everything else is evidence.

---

## 2. Product thesis — what must remain true

Keep these four properties even if every other feature is cut. They are the product, not the scaffolding.

| Property | Why it is load-bearing |
|---|---|
| **One variable, never more** | Multi-factor what-ifs collapse back into correlation. The constraint is the method. |
| **Generate once, freeze, reuse** | If the roster or traits differ across runs, the causal claim is false. |
| **Logged reasons are the product** | A line chart without a click-through trace is indistinguishable from a toy. |
| **The intervention receipt** | A visible “0 other variables changed” panel is the scientific method, rendered. |

### 2.1 Who it is for

SaaS pricing, competitive response, and PE diligence — anyone who currently runs a spreadsheet scenario that nobody trusts.

**Job to be done:** “Tell me what this one move does, who it hits, and why — before I ship it into a market I cannot rewind.”

**Anti-job:** not a revenue forecast, not a digital twin of the whole economy, not a chatbot that argues both sides of a strategy memo.

### 2.2 The honesty boundary (do not lie here)

Causality **inside the simulation** is real. Causality **in the customer’s market** is not — unless the agent population is calibrated to observed behavior.

An ideal product never says “this will happen.” It says “this is what happens in a market populated by these agents, under these assumptions, if you change only this.”

| Do not ship | Ship this |
|---|---|
| **Black-box oracle** — “Raise price 20% and MRR goes up.” No assumptions, no limitations, no agent reasons. Looks like every other AI forecast. Judges and CFOs both dismiss it. | **Inspectable experiment** — hypothesis, frozen method, two trajectories, named contributors, clickable reasons, explicit limitations. The output is a decision artifact, not a prediction score. |

Determinism is an engineering requirement, not a slide. Temperature 0, locked seed, byte-identical non-intervention inputs, frozen roster. If the API still jitters, disclose a variance envelope and stop saying “provably caused.” A slightly weaker claim that is true beats a strong claim a judge can falsify by hitting Run again.

### 2.3 Four product layers — only layer 1 is the hackathon

The ideal product is a direction, not day-one scope. Ship a working fixed-roster twin-run with a trace, then stop adding intelligence.

| Layer | What it does | Without it |
|---|---|---|
| **1. Twin-run engine** *(hackathon)* | Frozen roster, locked seed, one intervention, dual trajectories, decision-diff attribution, click-through reasons. | There is no product. |
| **2. Assumption studio** | WTP distributions, loyalty, switching costs, competitor aggression are first-class and editable. Every result cites its assumptions. | The sim is a black box with nicer charts. |
| **3. Calibration** | Fit the agent population to historical churn, win/loss, and price response. Then change one thing. | Causal in the toy, decorative in the real market. |
| **4. Decision export** | Board-ready narrative, segment-level attribution, robustness envelope across seeds, recommended action under constraints. | A demo people admire and do not reuse. |

Path from demo to software a CFO would run twice: today a working causal experiment you can click → next, assumptions you can edit → then, a population fitted to real churn.

### 2.4 Where Grok 4.6 has to be load-bearing

If you can delete the model and still demo the app, you built a dashboard on fake data. The model must do three jobs a rules engine cannot:

1. **Roster composition** — category research proposes 5 user personas + 1 competitor + 1 analyst. A B2B tool and a consumer box must not get the same five labels.
2. **Situated decisions** — each user reasons from a frozen reaction playbook (how that category talks about product decisions) plus WTP, loyalty, and precomputed prices/gaps — not a hardcoded threshold table.
3. **Grounded narrative** — end summary is assembled from logged reasons. If a sentence cannot be cited to an agent-round, it does not ship.

**Implementation binding:** live decisions are Cursor local agents via the Python SDK (`cursor-sdk`, `AsyncAgent.prompt`). See [`architecture.md`](architecture.md) ADR-7. The browser never holds `CURSOR_API_KEY`.

---

## 3. What we are actually building (scope for one day)

A single web app (Next.js + FastAPI backend) with:

1. A setup screen — the **business owner** defines the product and the one variable to test, and chooses **rounds** (3–8, default 4).
2. A research step — background agents propose **5 user personas, 1 competitor, 1 analyst** from category social patterns. The owner **confirms** before the twin run. There is no business-agent persona.
3. A simulation engine — confirmed roster, N rounds, twice (baseline + counterfactual), same seed. Users decide in parallel on snapshot S0; competitor decides separately on S1. Arithmetic is computed in the engine and handed in.
4. A causal attribution layer — per-round, per-agent contribution to the divergence. Every event is logged.
5. A paper — share and MRR figures, persona outcomes, competitor path, attribution bar, click-through reasons.

**Hard scope limits:**
- 5 user personas + 1 competitor + 1 analyst. Not a business agent. Not 30 live buyers.
- Rounds tunable **3–8**, default **4**. Grok Bot fixture paper stays 8.
- 1 variable changed between runs. Never more than one — this is the whole point.
- 1 real-ish product/market seed, prepared in advance (don't improvise it live).
- Token caps on every agent call. No live social fetch during rounds.

### 3.1 Must-ship vs skip without guilt

| Item | Call | Reason |
|---|---|---|
| Fixed 5+1+1 roster catalogue, tunable rounds, 1 intervention | **Must** | The causal claim needs a complete pipeline, not a richer market. |
| Divergence figures (share **and** MRR) + attribution bars | **Must** | This is the figure in the paper. No figure, no pitch. |
| Persona outcomes + competitor path | **Must** (this revision) | The owner has to see who moved and how the competitor reacted. |
| Click-through reason trace | **Must** | This is how you answer “is the model actually deciding.” |
| Intervention receipt panel | **Must** | Cheap to build, does the rhetorical work of the whole method. |
| Worked Grok Bot fixture, seed 42 | **Must** | Do not improvise live. Sanity-check the “share down, MRR up” shape before demo. |
| Research → confirm roster | **This revision** | Category playbooks, frozen once. Two products, two rosters. |
| Leave-one-out / Shapley attribution | **Skip** | Say it as the “if we had more time” answer. Decision-diff is enough today. |
| Historical calibration / live social during rounds | **Skip** | Research once. Do not pretend a CSV upload or a scrape mid-run. |
| Four intervention types live | **Skip** | One beautiful price-change demo beats four shallow ones. |

---

## 4. Inputs — exact terms to take from the user

### 4.1 Product / market setup (once, at start)

| Field | Type | Example |
|---|---|---|
| `product_name` | string | "Grok Bot" |
| `product_description` | string, 1–2 sentences | "Always-on AI teammates with their own cloud computer" |
| `current_price` | number (USD/month) | 120 |
| `market_size` | integer, total addressable buyer agents | 30 |
| `competitor_count` | integer | 1–2 |
| `competitor_price` | number | 100 |
| `buyer_price_sensitivity` | enum: low / medium / high | medium |
| `rounds` | integer 3–8, default 4 (Grok Bot fixture stays 8) | 4 |
| `random_seed` | integer, locked and reused across both runs | 42 |

### 4.2 The intervention (the one variable being tested)

| Field | Type | Example |
|---|---|---|
| `variable_type` | enum: `price_change`, `competitor_entry`, `marketing_spend`, `feature_change` | `price_change` |
| `variable_delta` | number or %, the single change applied | "+20%" |
| `applies_from_round` | integer, which round the change takes effect | 1 |

This is deliberately a small input surface. Roster composition is **researched and confirmed**, not typed by the owner. Round count **is** owner-tunable; it is not the intervened variable (both runs use the same N). Demo only `price_change`. The other enum values are product language, not day-one surface area.

---

## 5. Agent roster — researched from the category, frozen once

Don't hardcode "buyer, competitor, analyst" as opaque role strings. **Do** hardcode the **catalogue**: three classes (`buyer`, `competitor`, `analyst`) and a small set of buyer archetypes. Research fills *instances* (WTP, playbook, evidence), not new classes.

There is **no business-agent persona**. The business owner is the platform user; they pick the one action.

### 5.0 Research + confirm (runs once, before the twin simulation)

Background research agents, given `product_name` + `product_description` + prices + `market_size`, return a proposed roster:

- exactly **5 user (buyer) personas** covering at least 3 archetypes (`price_sensitive`, `loyalist`, `value_seeker`, `enterprise`, `churn_risk`)
- **1 competitor**
- **1 analyst** (meta, weight 0)

Each buyer carries a **reaction playbook**: how someone in that category on social media would react to a price hike, a cheaper competitor, a feature cut — mapped onto `stay` / `churn` / `switch`. Evidence is a short paraphrase, not a live feed.

The owner **confirms** the roster. Then it is hashed and fed identically into Run A and Run B.

**Determinism requirement (critical):** research is seeded and run once. Breaking generate-once / freeze / reuse breaks the causal claim in §6.1. Do not fetch social networks during rounds.

Within each archetype, individual trait values (exact WTP, loyalty) are sampled with the locked seed — same two-step pattern: generate once, freeze, reuse.

**Build order:** the fixed Grok Bot pipeline (§5.1) already works end to end. This revision swaps in research → confirm, then parallel users + competitor on S1. A confirmed fixture roster with a solid pipeline beats a scrape mid-run.

### 5.1 Default fixed roster (Grok Bot fixture)

| Agent | Observes each round | Decides |
|---|---|---|
| **Buyer agent(s)** — 5 weighted instances | S0: playbook, WTP, precomputed `wtp_gap`, prices, status | stay / churn / switch |
| **Competitor agent** | **S1** after users applied: your price, new share | hold / undercut / match |
| **Analyst agent** (meta, not a market participant) | full round history | flags anomalies; weight 0 |

Buyer agents run **in parallel** on S0. Competitor runs **separately** after user decisions are applied. Engine arithmetic (share, MRR, WTP gap) is handed in; agents must not recompute it. Unchanged observation fields are byte-identical across A and B.

Spread willingness-to-pay so $144 sits **inside** the distribution, not above all of it. The plot of the demo is the buyers who sit between $120 and $144.

### 5.2 Per-round agent I/O contract (this is what you code first)

**Prompt input to each buyer agent (JSON):**
```json
{
  "round": 4,
  "your_persona": {
    "class": "buyer",
    "archetype": "price_sensitive",
    "willingness_to_pay": 128,
    "loyalty_score": 0.3,
    "price_sensitivity": "high",
    "wtp_gap": 16,
    "voice": "complains in public, compares screenshots, leaves fast",
    "reaction_playbook": {
      "price_hike": "switch_if_above_wtp",
      "competitor_cheaper": "amplify_and_switch"
    }
  },
  "current_price": 144,
  "competitor_price": 100,
  "your_status": "subscribed",
  "history_summary": "Price rose from $120 to $144 at round 1."
}
```

**Required output (JSON, strict schema — enforce with a JSON mode / grammar if Grok 4.6 supports it):**
```json
{
  "decision": "churn",
  "reason": "Price now $7 above my willingness to pay of $52; competitor is $14 cheaper.",
  "confidence": 0.82
}
```

The `reason` field is not cosmetic — it is the product. It must sound like that category reacting to the product decision, stay within 40–400 characters, and remain consistent with the frozen playbook. Store every one, every round, both runs. Reject empty or template reasons (not “I decided to churn”).

---

## 6. The causal attribution mechanism (this is the actual novelty — build it carefully)

### 6.1 Why this is legitimate to call "causal"

Two runs, A (baseline) and B (counterfactual):
- Same `random_seed`.
- Same initial agent personas and starting state.
- Same prompt templates.
- Only difference: the one intervention variable, applied identically from `applies_from_round` onward.

Because nothing else differs, any divergence in outcome between A and B is attributable to the intervention **by construction** — this is the definition of a controlled experiment (a "do-operator" intervention in Pearl's causal framework), not an inferred correlation. Say this explicitly in your pitch; it's your strongest technical claim.

**Engineering requirement to make this true, not just claimed:** you must actually lock the seed and hold every agent's non-intervention inputs byte-identical across both runs. If Grok 4.6 calls have any temperature-driven nondeterminism, either set temperature to 0 for this use case or accept and disclose minor variance — do not claim "provably caused" if you haven't controlled for this. This is the one place where the engineering has to match the pitch.

### 6.2 Per-round divergence metric

For each round `r`, compute:

```
divergence(r) = market_share_A(r) - market_share_B(r)
```

(or revenue, or churn count — pick one primary metric for the headline chart; track 2–3 secondary metrics for the metric cards)

Headline the tension, not a single line: **share and MRR together**. The interesting finding is that they can move in opposite directions.

### 6.3 Per-agent causal contribution (the differentiator)

At each round where divergence changes meaningfully (Δdivergence > threshold), attribute the delta to whichever agents made a *different* decision in run B vs run A that round:

```
contribution(agent_i, r) = (agent_i's decision differed in B?)
                            × (agent_i's decision weight, e.g. 1/market_size for a buyer,
                               or a fixed weight for competitor/analyst)
```

Normalize contributions at each round to sum to 100%, so you can show: *"Round 4: 62% of the new divergence is attributable to buyer-agent churn decisions; 38% to the competitor agent matching price."*

The two lines are the hook. The stacked bars are the product. Without them this is just “two simulations diverged.”

This is deliberately simple attribution (a decision-diff weighted count), not a full Shapley-value computation — that's the right scope call for one day. If you have spare time near the end, upgrading to a leave-one-out marginal contribution (rerun with one agent's decision frozen to run-A behavior, measure the delta) is the "if we had more time" answer that sounds credible to a technical judge without you having to build it live.

---

## 7. Output — exact shape

Five frozen artifacts are the **paper export**. Supabase Postgres (`experiments` + append-only `events`) is the **live process record** — see [`architecture.md`](architecture.md) ADR-2 and §7.5. If you cannot rebuild the paper from the ledger, you do not have causality. The JSON files remain the inspectable bundle the UI and judges read; they are written at milestones, not after every agent decision.

| Stage | Input | Frozen output |
|---|---|---|
| Setup | Product, market, one intervention | `experiment.json` — variable, delta, `applies_from_round`, seed |
| Persona gen (once) | Product description + market size | `roster.json` — roles, counts, sampled traits |
| Twin runner | Identical roster + prompts; only intervention differs | `run_a.json` / `run_b.json` — per-agent decisions and reasons |
| Attribution | Aligned logs, decision diffs, metric trajectories | `attribution.json` + grounded summary (no free-standing LLM recap) |

```json
{
  "run_a": { "trajectory": [...], "agent_logs": [...] },
  "run_b": { "trajectory": [...], "agent_logs": [...] },
  "divergence_by_round": [
    { "round": 1, "delta": 0, "top_contributors": [] },
    { "round": 4, "delta": -6, "top_contributors": [
      { "agent": "buyer_3", "contribution_pct": 62, "reason": "..." },
      { "agent": "competitor", "contribution_pct": 38, "reason": "..." }
    ]}
  ],
  "summary_narrative": "1–2 sentence, generated once at the end, grounded in the logged reasons — not a free-standing LLM summary."
}
```

The sentence the dashboard should write for the worked example:

> Raising Grok Bot 20% costs 10 points of share and still adds $115 MRR, because the buyers who left were already at or below willingness-to-pay of $128–$140. Remaining customers are the loyal segment. Click round 4.

---

## 8. Display — what the dashboard actually needs

Read top to bottom like a paper. The chart is the figure. The trace is the appendix. The receipt is the methods section, kept on the first page on purpose.

**Build this as specified in [`architecture.md`](architecture.md) §10** (hypothesis sentence, round pills, land on R4, A-over-B console). Do not start from a generic dashboard.

| Surface | Job | Priority |
|---|---|---|
| Two-scenario header + receipt | Name the fork. Prove nothing else changed. Prompt hash, seed, roster hash visible. | **P0 — rhetorical spine** |
| Twin trajectories | Share **and** MRR as two small-multiple figures (not a toggle). Intervention round marked. | **P0 — visual center** |
| Persona outcomes | Five users: stay / churn / switch in A vs B. | **P1 — this revision** |
| Competitor path | Competitor price and hold/match/undercut over rounds, A vs B. | **P1 — this revision** |
| Attribution bars | Per-round contribution split. Makes it look like causal analysis. | **P0 — differentiator** |
| Click-through trace | Side-by-side reasons for the agents who actually differed. | **P0 — credibility defense** |
| Metric cards | Final share delta, MRR delta, churn count. One of them should surprise. | **P1 — polish** |
| Assumption drawer | Edit WTP / loyalty / competitor aggression; re-run. Shows the result is conditional. | **P2 — product, not demo** |
| Experiment grid | Same baseline vs +10 / +20 / +30. Still one variable per pair. | **P2 — power-user** |
| Export | One paragraph + figure + named contributors. The thing they paste into a doc. | **P2 — distribution** |

**Hackathon build order (P0 + P1 only):**

1. **Two-scenario header** — plain text, what changed, nothing else. ("Baseline $120 vs +20% → $144")
2. **Share and MRR line charts** — two figures, x = round, A vs B. This is the visual center. Do not hide MRR behind a toggle.
3. **Persona outcomes + competitor path** — who moved, how the incumbent reacted.
4. **Attribution bar under the selected round** — stacked contribution. This is the piece that makes it look like real causal analysis.
5. **Click-through trace** — side-by-side reasons for agents who differed.
6. **Metric cards** — final share delta, revenue delta, churn count.
7. **Intervention receipt** — “0 other variables changed.”

Build order: get 1–4 working (that's the whole story), 5 next (credibility), 6–7 polish. Do not start P2 (assumption drawer, experiment grid, export) until this revision's research/confirm path is green.

---

## 9. Financial / business terms to model (keep this simple)

You do not need a real financial model — you need terms that make the output legible to a business audience. Compute these from agent decisions, don't hand-roll a separate finance layer:

| Term | Formula | Why it matters |
|---|---|---|
| **Market share** | subscribed buyer agents ÷ total buyer agents | primary trajectory metric |
| **MRR (monthly recurring revenue)** | subscribed buyer agents × current price | ties agent decisions to a dollar figure judges immediately understand |
| **Churn rate (per round)** | agents who churned this round ÷ subscribed agents last round | standard SaaS term, instantly legible |
| **CAC-adjusted note (optional, skip if short on time)** | if you model marketing spend as a variable, track "new buyers acquired ÷ spend" | only include if your chosen intervention is spend-related |
| **Willingness-to-pay gap** | current_price − buyer's `willingness_to_pay` | this is literally what drives each buyer agent's decision; surfacing it in the reasoning trace makes the causal story concrete |

Report MRR and market share as your two headline numbers — they're the two any business-minded judge will look for first. The demo finding is that they disagree: share down, MRR up.

---

## 10. Worked example to build and test against

Use this exact scenario as your dev/test fixture so you're not improvising data during build or demo.

**Setup:**
- Product: "Grok Bot," always-on AI teammates, $120/seat/month (Cursor Premium Teams)
- Market: 30 buyer agents, willingness-to-pay distributed $105–$180 (spread them so the churn threshold is interesting — a few just above/below $144)
- 1 competitor agent, Claude Cowork, currently priced at $100
- Seed: 42, locked across both runs

**Intervention:** price +20% → $144, effective round 1

**Expected qualitative outcome (sanity check your simulation against this before demo day):**
- Round 1–3: minimal divergence (agents need a round or two to "notice" and act)
- Round 4–5: divergence opens up as price-sensitive agents (willingness-to-pay $128–$140) start churning
- Round 6–8: divergence stabilizes as remaining buyers are the loyal/high-willingness-to-pay segment; MRR in run B likely still higher despite lower market share (this is your "revenue up, share down" story — a genuinely interesting finding, not just "more expensive = worse")

**Illustrative trajectories to sanity-check shape** (not ground truth — your sim should rhyme with this, not match it pixel-for-pixel):

| Round | Share A ($120) | Share B ($144) | MRR A | MRR B |
|---|---|---|---|---|
| 1 | 80% | 80% | $2,880 | $3,456 |
| 2 | 80% | 78% | $2,880 | $3,370 |
| 3 | 79% | 74% | $2,844 | $3,197 |
| 4 | 78% | 69% | $2,808 | $2,981 |
| 5 | 77% | 67% | $2,772 | $2,894 |
| 6 | 76% | 66% | $2,736 | $2,851 |
| 7 | 76% | 66% | $2,736 | $2,851 |
| 8 | 76% | 66% | $2,736 | $2,851 |

Final cards the demo should be able to show: **share −10pp**, **MRR +$115**. That tension is the whole pitch.

**Illustrative attribution at the rounds that move** (decision-diff, normalized to 100%):

| Round | Price-sensitive buyers | Competitor matching | Loyal / enterprise buyers |
|---|---|---|---|
| 3 | 20% | 55% | 25% |
| 4 | 62% | 38% | 0% |
| 5 | 71% | 19% | 10% |
| 6 | 18% | 12% | 70% |

If your simulation produces something wildly different from this shape (e.g. zero divergence, or immediate total collapse), debug the agent prompts before demo day — this scenario is chosen specifically to produce a nontrivial, explainable divergence.

**Test checklist:**
- [ ] Run A and Run B produce identical trajectories up to `applies_from_round`
- [ ] Divergence appears only after the intervention round
- [ ] Every agent decision has a non-empty, specific `reason` string (not "I decided to churn")
- [ ] Attribution percentages sum to ~100% at each divergence round
- [ ] Click-through trace correctly matches chart round to logged agent reasons
- [ ] Rerunning with the same seed twice produces identical Run A trajectories (determinism check)
- [ ] End summary can be cited to stored reason strings (no ungrounded claims)

---

## 11. Build order for this revision

| Time | Task |
|---|---|
| Morning (2–3 hrs) | Agent I/O contract + single-round simulation working end to end, fixed 3-role roster, prove Grok 4.6 returns valid structured JSON |
| Late morning (1–2 hrs) | Full round loop (8 rounds), 3 fixed personas, seed-locking, run A vs run B |
| Early afternoon (1 hr) | Attribution math + divergence chart (dashboard items 1–3) |
| Early-mid afternoon (1 hr) | Click-through trace (item 4) — not optional, this is your credibility mechanism |
| Mid afternoon | §5.0 research + confirm — proposed 5+1+1 roster; owner must confirm; two products must differ |
| After that | Parallel buyers, competitor on S1, tunable rounds (default 4), extra paper figures, token caps |

**Cutoff rule:** if the fixture paper through the trace panel isn't working, skip research and demo with the fixed Grok Bot roster. A working fixed-role demo beats a half-built scrape.

---

## 12. What to say explicitly in the pitch (don't leave this implicit)

1. "This is a controlled experiment, not a prediction — same seed, same agents, one variable changed."
2. "Every agent decision has a logged reason — click any divergence point and see exactly why."
3. "Grok 4.6 is making every decision you see — remove it and there's nothing left to demo."
4. "We don't invent a business agent — you are the owner. We research five users and one competitor from how that category talks, you confirm, then we freeze them for both runs."
5. Do **not** claim this is what will happen in the real market. Claim: this is what happens in this frozen agent market, under these assumptions, if you change only this.

### 12.1 Demo script

| Beat | What they see | What you say |
|---|---|---|
| 20s | Header: Baseline $120 vs +20% → $144. Receipt: 0 other variables changed. | Controlled experiment, not a prediction. |
| 60s | Two lines diverge at R4. Share down, MRR up. | The interesting finding is the tension, not the direction. |
| 90s | Attribution bars. Click R4. Buyer_3 reason vs competitor reason. | Every decision is logged. Here is who caused the gap. |
| Optional 30s | Roster for Acme vs a consumer box, side by side. | We did not hardcode buyers. The model composed the market. |

---

## 13. Risks that falsify the pitch

| Failure | How it shows up | Fix before demo |
|---|---|---|
| **Nondeterminism** | Re-run produces a different Run A. | Temp 0, seed lock, freeze roster. If still noisy, weaken the claim. |
| **Premature collapse** | Everyone churns in round 1. | Spread WTP so $144 sits inside the distribution, not above all of it. |
| **Zero divergence** | Two lines overlap. | Make 3–5 buyers sit between $120 and $144. That band is the plot. |
| **Generic reasons** | “I decided to churn.” | Force JSON schema. Reject empty or template reasons in the runner. |
| **Ungrounded summary** | Narrative mentions a cause not in the logs. | Generate the summary only from stored reason strings. |
