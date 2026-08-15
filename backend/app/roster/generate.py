from __future__ import annotations

from pathlib import Path

from app.contracts import Adapter, CreateExperimentRequest, Roster, RosterAgent
from app.roster.catalogue import normalize_roster, validate_catalogue
from app.roster.fixed_grok_bot import build_roster
from app.roster.research.distill import distill
from app.roster.research.filters import filter_items
from app.roster.research.sources import fetch_reddit, fetch_web
from app.store import experiment_dir, write_json
from app import settings

BOX_ARCHETYPES = (
    "loyalist",
    "value_seeker",
    "churn_risk",
    "enterprise",
    "price_sensitive",
)


def _category(body: CreateExperimentRequest) -> str:
    text = f"{body.product_name} {body.product_description}".lower()
    if "subscription box" in text or "snack" in text:
        return "snacks"
    return "saas"


def _fixture_proposal(body: CreateExperimentRequest) -> Roster:
    roster = build_roster(body.random_seed)
    if "subscription box" not in body.product_description.lower():
        return roster
    agents: list[RosterAgent] = []
    buyer_i = 0
    for agent in roster.agents:
        data = agent.model_dump()
        if agent.agent_id.startswith("buyer_"):
            arch = BOX_ARCHETYPES[buyer_i]
            buyer_i += 1
            data["archetype"] = arch
            data["role"] = f"{arch}_buyer"
            data["agent_class"] = "buyer"
            traits = dict(data["traits"])
            traits["willingness_to_pay"] = float(traits.get("willingness_to_pay") or 100) + 37
            data["traits"] = traits
        agents.append(RosterAgent.model_validate(data))
    return Roster(agent_roles=roster.agent_roles, agents=agents)


def _write_research(
    experiment_id: str | None,
    *,
    quality: str,
    kept: list[dict],
    root: Path | None,
) -> None:
    if not experiment_id:
        return
    write_json(
        experiment_dir(experiment_id, root) / "research.json",
        {
            "quality": quality,
            "reddit_ids": [item.get("id") for item in kept if item.get("source") == "reddit"],
            "web_urls": [item.get("url") for item in kept if item.get("source") == "web"],
            "kept_count": len(kept),
        },
    )


def propose_roster(
    body: CreateExperimentRequest,
    *,
    adapter: Adapter | None = None,
    experiment_id: str | None = None,
    root: Path | None = None,
) -> Roster:
    chosen = adapter or body.adapter
    if chosen == Adapter.fixture:
        roster = normalize_roster(_fixture_proposal(body))
        validate_catalogue(roster)
        _write_research(experiment_id, quality="fixture", kept=[], root=root)
        return roster

    category = _category(body)
    items = fetch_reddit(category, [category, body.product_name]) + fetch_web(
        [body.product_name, body.product_description[:80]]
    )
    kept = filter_items(items, category=category)
    if len(kept) < settings.RESEARCH_MIN_KEEP:
        roster = normalize_roster(_fixture_proposal(body))
        validate_catalogue(roster)
        _write_research(experiment_id, quality="fallback", kept=kept, root=root)
        return roster

    roster = normalize_roster(distill(kept, body))
    validate_catalogue(roster)
    _write_research(experiment_id, quality="ok", kept=kept, root=root)
    return roster
