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
