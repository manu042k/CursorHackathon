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
        profile_for(agent.archetype)
        if agent.agent_class == "buyer" and agent.archetype not in ALLOWED_BUYER:
            raise ValueError(f"invalid buyer archetype {agent.archetype}")
        if agent.agent_class == "competitor" and agent.archetype != "incumbent":
            raise ValueError("competitor must be incumbent")
        if agent.agent_class == "analyst" and agent.archetype != "meta":
            raise ValueError("analyst must be meta")
