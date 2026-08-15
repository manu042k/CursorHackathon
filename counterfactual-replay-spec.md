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

1. **Roster composition** — a B2B analytics tool and a consumer subscription box produce different market participants. Show two rosters side by side.
2. **Situated decisions** — each buyer reasons from willingness-to-pay, loyalty, and the competitor’s price — not a hardcoded threshold table.
3. **Grounded narrative** — end summary is assembled from logged reasons. If a sentence cannot be cited to an agent-round, it does not ship.

---

## 3. What we are actually building (scope for one day)

A single web app (Next.js or plain React + FastAPI backend) with:

1. A setup screen — define the product/market and the one variable to test.
2. A simulation engine — N agents, run for R rounds, twice (baseline + counterfactual), same seed.
3. A causal attribution layer — per-round, per-agent contribution to the divergence.
4. A dashboard — two trajectories, a divergence chart, and a click-through reasoning trace.

**Hard scope limits (do not exceed on hackathon day):**
- 3 agent personas. Not 5, not 10.
- 8 simulation rounds.
- 1 variable changed between runs. Never more than one — this is the whole point.
- 1 real-ish product/market seed, prepared in advance (don't improvise it live).

### 3.1 Must-ship vs skip without guilt

| Item | Call | Reason |
|---|---|---|
| Fixed 3-role roster, 8 rounds, 1 intervention | **Must** | The causal claim needs a complete pipeline, not a richer market. |
| Divergence chart + attribution bars | **Must** | This is the figure in the paper. No figure, no pitch. |
| Click-through reason trace | **Must** | This is how you answer “is the model actually deciding.” |
| Intervention receipt panel | **Must** | Cheap to build, does the rhetorical work of the whole method. |
| Worked Acme fixture, seed 42 | **Must** | Do not improvise live. Sanity-check the “share down, MRR up” shape before demo. |
| Generated roster from product text | **Only if pipeline is solid** | Best differentiator after the engine works. Two products, two rosters. |
| Leave-one-out / Shapley attribution | **Skip** | Say it as the “if we had more time” answer. Decision-diff is enough today. |
| Historical calibration | **Skip** | This is the real company. Do not pretend a CSV upload on hackathon day. |
| Four intervention types live | **Skip** | One beautiful price-change demo beats four shallow ones. |

---

## 4. Inputs — exact terms to take from the user

### 4.1 Product / market setup (once, at start)

| Field | Type | Example |
|---|---|---|
| `product_name` | string | "Acme Analytics" |
| `product_description` | string, 1–2 sentences | "B2B analytics dashboard for e-commerce teams" |
| `current_price` | number (USD/month) | 49 |
| `market_size` | integer, total addressable buyer agents | 30 |
| `competitor_count` | integer | 1–2 |
| `competitor_price` | number | 45 |
| `buyer_price_sensitivity` | enum: low / medium / high | medium |
| `rounds` | integer, fixed at 8 for the demo | 8 |
| `random_seed` | integer, locked and reused across both runs | 42 |

### 4.2 The intervention (the one variable being tested)

| Field | Type | Example |
|---|---|---|
| `variable_type` | enum: `price_change`, `competitor_entry`, `marketing_spend`, `feature_change` | `price_change` |
| `variable_delta` | number or %, the single change applied | "+20%" |
| `applies_from_round` | integer, which round the change takes effect | 1 |

This is deliberately the entire input surface. Everything else (agent count, persona definitions, round count) is fixed by you ahead of time so the demo is reliable, not user-configurable live. Demo only `price_change`. The other enum values are product language, not day-one surface area.

---

## 5. Agent roster — generated from the product, not hardcoded

Don't hardcode "buyer, competitor, analyst" as fixed roles. Generate the roster from the product description itself, so a B2B SaaS tool and a consumer subscription box produce genuinely different market participants. This is a differentiator worth demoing on its own — the roster composition is evidence Grok 4.6 understood the product, before the simulation even runs.

### 5.0 Persona-generation step (runs once, before the twin simulation)

One Grok 4.6 call, given `product_name` + `product_description` + `market_size`, returns a structured roster:

```json
{
  "agent_roles": [
    { "role": "price_sensitive_buyer", "count": 12, "traits": { "willingness_to_pay_range": [35,55], "loyalty": "low" } },
    { "role": "enterprise_buyer", "count": 5, "traits": { "willingness_to_pay_range": [60,90], "loyalty": "high" } },
    { "role": "incumbent_competitor", "count": 1, "traits": { "current_price": 45 } },
    { "role": "channel_partner", "count": 1, "traits": { "influence": "medium" } }
  ]
}
```

**Determinism requirement (critical):** this call is seeded and run once at setup. Store the resulting roster as a frozen JSON artifact and feed the identical roster into both run A and run B. The dynamism is in *what gets generated per product* — not in varying between the two runs of the same product. Generate once, freeze, reuse. Breaking this rule breaks the causal claim in §6.1.

Within each role, individual agent trait values (exact willingness-to-pay, exact loyalty score) are then sampled from the role's stated range using the same locked seed — same two-step pattern as before: generate once, freeze, reuse across both runs.

**Build order for this feature:** get the fixed-role pipeline (§5.1 below) working end to end first — full twin-run, attribution, and trace all working. Only then swap the hardcoded role list for the generated one. A hardcoded roster with a solid working pipeline beats a broken dynamic-roster pipeline. Budget this as a late-addition, not a foundation.

### 5.1 Default fixed roster (build this first, 3 roles)

| Agent | Observes each round | Decides |
|---|---|---|
| **Buyer agent(s)** — instantiate 3–5 with different price-sensitivity thresholds | current price, competitor price, own "willingness to pay" | stay subscribed / churn / switch to competitor |
| **Competitor agent** | your price, market share trend | hold price / undercut / match |
| **Analyst agent** (meta-agent, not a market participant) | full round history | flags anomalies, writes the one-line causal note per divergence point |

Once §5.0 is wired in, these three roles become the *default* roster returned for a generic SaaS product — the generated roster for other product types will differ (see example above). The per-round I/O contract in §5.2 below stays identical regardless of which roles are active; only the persona content changes.

Each buyer agent is a separate Grok 4.6 call (or a batched call returning an array) with its own persona (e.g. "price-sensitive, willingness to pay $52" vs "loyal, willingness to pay $70"). This is what makes the population feel real rather than monolithic.

Spread willingness-to-pay so $59 sits **inside** the distribution, not above all of it. The plot of the demo is the 3–5 buyers who sit between $49 and $59. That band is what produces divergence instead of collapse or a flat line.

### 5.2 Per-round agent I/O contract (this is what you code first)

**Prompt input to each buyer agent (JSON):**
```json
{
  "round": 4,
  "your_persona": {
    "willingness_to_pay": 52,
    "loyalty_score": 0.3,
    "price_sensitivity": "high"
  },
  "current_price": 59,
  "competitor_price": 45,
  "your_status": "subscribed",
  "history_summary": "Price rose from $49 to $59 at round 1."
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

The `reason` field is not cosmetic — it is the product. Store every one of these, every round, both runs. This is what the click-through trace displays later. Reject empty or template reasons in the runner (not “I decided to churn”).

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

Four frozen artifacts are the scientific record. If you cannot replay from them, you do not have causality.

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

> Raising price 20% costs 10 points of share and still adds $51 MRR, because the buyers who left were already at or below willingness-to-pay of $52–$58. Remaining customers are the loyal segment. Click round 4.

---

## 8. Display — what the dashboard actually needs

Read top to bottom like a paper. The chart is the figure. The trace is the appendix. The receipt is the methods section, kept on the first page on purpose.

| Surface | Job | Priority |
|---|---|---|
| Two-scenario header + receipt | Name the fork. Prove nothing else changed. Prompt hash, seed, roster hash visible. | **P0 — rhetorical spine** |
| Twin trajectories | One primary metric (share or MRR), with the other on a toggle. Intervention round marked. | **P0 — visual center** |
| Attribution bars | Per-round contribution split. Makes it look like causal analysis. | **P0 — differentiator** |
| Click-through trace | Side-by-side reasons for the agents who actually differed. | **P0 — credibility defense** |
| Metric cards | Final share delta, MRR delta, churn count. One of them should surprise. | **P1 — polish** |
| Assumption drawer | Edit WTP / loyalty / competitor aggression; re-run. Shows the result is conditional. | **P2 — product, not demo** |
| Experiment grid | Same baseline vs +10 / +20 / +30. Still one variable per pair. | **P2 — power-user** |
| Export | One paragraph + figure + named contributors. The thing they paste into a doc. | **P2 — distribution** |

**Hackathon build order (P0 + P1 only):**

1. **Two-scenario header** — plain text, what changed, nothing else. ("Baseline $49 vs +20% → $59")
2. **Divergence line chart** — two lines (Chart.js), x = round, y = your chosen primary metric. This is the visual center of the demo.
3. **Attribution bar under the chart** — a stacked/segmented bar per round showing causal contribution split (agent colors). This is the piece that makes it look like real causal analysis, not just "two lines diverged."
4. **Click-through trace** — clicking any round on the chart opens a small panel showing each agent's actual logged `reason` string for that round, in both runs, side by side. This is your answer to "is the model actually deciding this."
5. **Metric cards** — 3 summary numbers at the top (final market share delta, revenue delta, churn count), rounded, with a colored delta indicator.
6. **Intervention log / diff view** — a small, explicit "0 other variables changed" panel. This is the receipt. Put it somewhere visible, not buried — it's doing real rhetorical work in your pitch.

Build order matters here: get 1–3 working first (that's the whole story), 4 next (that's your credibility defense), 5–6 last (polish). Do not start P2 on hackathon day.

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
- Product: "Acme Analytics," B2B SaaS, $49/month
- Market: 30 buyer agents, willingness-to-pay distributed $35–$75 (spread them so the churn threshold is interesting — a few just above/below $59)
- 1 competitor agent, currently priced at $45
- Seed: 42, locked across both runs

**Intervention:** price +20% → $59, effective round 1

**Expected qualitative outcome (sanity check your simulation against this before demo day):**
- Round 1–3: minimal divergence (agents need a round or two to "notice" and act)
- Round 4–5: divergence opens up as price-sensitive agents (willingness-to-pay $50–$58) start churning
- Round 6–8: divergence stabilizes as remaining buyers are the loyal/high-willingness-to-pay segment; MRR in run B likely still higher despite lower market share (this is your "revenue up, share down" story — a genuinely interesting finding, not just "more expensive = worse")

**Illustrative trajectories to sanity-check shape** (not ground truth — your sim should rhyme with this, not match it pixel-for-pixel):

| Round | Share A ($49) | Share B ($59) | MRR A | MRR B |
|---|---|---|---|---|
| 1 | 80% | 80% | $1,176 | $1,416 |
| 2 | 80% | 78% | $1,176 | $1,381 |
| 3 | 79% | 74% | $1,161 | $1,310 |
| 4 | 78% | 69% | $1,147 | $1,221 |
| 5 | 77% | 67% | $1,132 | $1,186 |
| 6 | 76% | 66% | $1,117 | $1,168 |
| 7 | 76% | 66% | $1,117 | $1,168 |
| 8 | 76% | 66% | $1,117 | $1,168 |

Final cards the demo should be able to show: **share −10pp**, **MRR +$51**. That tension is the whole pitch.

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

## 11. Build order for the day (suggested time-boxing)

| Time | Task |
|---|---|
| Morning (2–3 hrs) | Agent I/O contract + single-round simulation working end to end, fixed 3-role roster, prove Grok 4.6 returns valid structured JSON |
| Late morning (1–2 hrs) | Full round loop (8 rounds), 3 fixed personas, seed-locking, run A vs run B |
| Early afternoon (1 hr) | Attribution math + divergence chart (dashboard items 1–3) |
| Early-mid afternoon (1 hr) | Click-through trace (item 4) — not optional, this is your credibility mechanism |
| Mid afternoon (1–1.5 hrs, only if the above is solid) | §5.0 persona-generation step — swap hardcoded roles for a generated roster; test against 2 different product descriptions to confirm the roster genuinely differs |
| Last hour | Metric cards, intervention log panel, rehearse the demo: show roster generation on 2 products briefly, then dive into the full worked example |

**Cutoff rule:** if the fixed-role pipeline (through the trace panel) isn't fully working by early-mid afternoon, skip §5.0 entirely and demo with the fixed roster. A working fixed-role demo beats a half-built dynamic one.

---

## 12. What to say explicitly in the pitch (don't leave this implicit)

1. "This is a controlled experiment, not a prediction — same seed, same agents, one variable changed."
2. "Every agent decision has a logged reason — click any divergence point and see exactly why."
3. "Grok 4.6 is making every decision you see — remove it and there's nothing left to demo."
4. (if §5.0 shipped) "We don't hardcode buyer and competitor — Grok 4.6 reads the product and decides who actually belongs in this market." Show the roster for two different products side by side as proof.
5. Do **not** claim this is what will happen in the real market. Claim: this is what happens in this frozen agent market, under these assumptions, if you change only this.

### 12.1 Demo script

| Beat | What they see | What you say |
|---|---|---|
| 20s | Header: Baseline $49 vs +20% → $59. Receipt: 0 other variables changed. | Controlled experiment, not a prediction. |
| 60s | Two lines diverge at R4. Share down, MRR up. | The interesting finding is the tension, not the direction. |
| 90s | Attribution bars. Click R4. Buyer_3 reason vs competitor reason. | Every decision is logged. Here is who caused the gap. |
| Optional 30s | Roster for Acme vs a consumer box, side by side. | We did not hardcode buyers. The model composed the market. |

---

## 13. Risks that falsify the pitch

| Failure | How it shows up | Fix before demo |
|---|---|---|
| **Nondeterminism** | Re-run produces a different Run A. | Temp 0, seed lock, freeze roster. If still noisy, weaken the claim. |
| **Premature collapse** | Everyone churns in round 1. | Spread WTP so $59 sits inside the distribution, not above all of it. |
| **Zero divergence** | Two lines overlap. | Make 3–5 buyers sit between $49 and $59. That band is the plot. |
| **Generic reasons** | “I decided to churn.” | Force JSON schema. Reject empty or template reasons in the runner. |
| **Ungrounded summary** | Narrative mentions a cause not in the logs. | Generate the summary only from stored reason strings. |
