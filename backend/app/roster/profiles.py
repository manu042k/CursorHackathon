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
            "which price. They never propose an intervention of their own, even when asked."
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
