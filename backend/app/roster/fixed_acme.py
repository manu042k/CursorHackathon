"""Fixed Acme Analytics roster. Seeded for identity, values frozen for the demo band."""

from __future__ import annotations

from app.contracts import AgentRole, Roster, RosterAgent

BUYER_SPECS: tuple[tuple[str, str, float, float, float, str], ...] = (
    ("buyer_1", "price_sensitive_buyer", 8, 51.0, 0.15, "high"),
    ("buyer_2", "price_sensitive_buyer", 6, 52.0, 0.30, "high"),
    ("buyer_3", "price_sensitive_buyer", 5, 55.0, 0.35, "high"),
    ("buyer_4", "enterprise_buyer", 6, 62.0, 0.70, "medium"),
    ("buyer_5", "enterprise_buyer", 5, 72.0, 0.85, "low"),
)

MARKET_SIZE = 30


def build_roster(seed: int = 42) -> Roster:
    """Return the frozen Acme roster. Same seed → identical JSON."""
    _ = seed
    agents = [
        RosterAgent(
            agent_id=agent_id,
            role=role,
            weight=weight,
            traits={
                "willingness_to_pay": wtp,
                "loyalty_score": loyalty,
                "price_sensitivity": sensitivity,
            },
        )
        for agent_id, role, weight, wtp, loyalty, sensitivity in BUYER_SPECS
    ]
    agents.append(
        RosterAgent(
            agent_id="competitor",
            role="incumbent_competitor",
            weight=0,
            traits={"current_price": 45},
        )
    )
    agents.append(
        RosterAgent(
            agent_id="analyst",
            role="analyst",
            weight=0,
            traits={"meta": True},
        )
    )
    return Roster(
        agent_roles=[
            AgentRole(
                role="price_sensitive_buyer",
                count=3,
                traits={"willingness_to_pay_range": [50, 58], "loyalty": "low"},
            ),
            AgentRole(
                role="enterprise_buyer",
                count=2,
                traits={"willingness_to_pay_range": [60, 90], "loyalty": "high"},
            ),
            AgentRole(role="incumbent_competitor", count=1, traits={"current_price": 45}),
            AgentRole(role="analyst", count=1, traits={"meta": True}),
        ],
        agents=agents,
    )
