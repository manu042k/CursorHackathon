"""Fixed Grok Bot roster. Seeded for identity, values frozen for the demo band."""

from __future__ import annotations

from app.contracts import AgentRole, Roster, RosterAgent

PRODUCT_NAME = "Grok Bot"
PRODUCT_DESCRIPTION = (
    "Always-on AI teammates with their own cloud computer. They sign into your "
    "tools, finish jobs end to end, and only come back for approval."
)
LIST_PRICE = 120.0
COMPETITOR_NAME = "Claude Cowork"
COMPETITOR_PRICE = 100.0
FORK_PRICE = 144.0
MARKET_SIZE = 30

# buyer_id, role, weight, WTP, loyalty, sensitivity
# $144 sits inside the band: buyer_2 ($128) and buyer_3 ($140) are the plot.
BUYER_SPECS: tuple[tuple[str, str, float, float, float, str], ...] = (
    ("buyer_1", "price_sensitive_buyer", 8, 105.0, 0.15, "high"),
    ("buyer_2", "price_sensitive_buyer", 6, 128.0, 0.30, "high"),
    ("buyer_3", "price_sensitive_buyer", 5, 140.0, 0.35, "high"),
    ("buyer_4", "enterprise_buyer", 6, 155.0, 0.70, "medium"),
    ("buyer_5", "enterprise_buyer", 5, 180.0, 0.85, "low"),
)


def build_roster(seed: int = 42) -> Roster:
    """Return the frozen Grok Bot roster. Same seed → identical JSON."""
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
            agent_class="buyer",
            archetype="price_sensitive" if "price_sensitive" in role else "enterprise",
        )
        for agent_id, role, weight, wtp, loyalty, sensitivity in BUYER_SPECS
    ]
    agents.append(
        RosterAgent(
            agent_id="competitor",
            role="incumbent_competitor",
            weight=0,
            traits={"name": COMPETITOR_NAME, "current_price": COMPETITOR_PRICE},
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
    return Roster(
        agent_roles=[
            AgentRole(
                role="price_sensitive_buyer",
                count=3,
                traits={"willingness_to_pay_range": [105, 140], "loyalty": "low"},
            ),
            AgentRole(
                role="enterprise_buyer",
                count=2,
                traits={"willingness_to_pay_range": [155, 180], "loyalty": "high"},
            ),
            AgentRole(
                role="incumbent_competitor",
                count=1,
                traits={"name": COMPETITOR_NAME, "current_price": COMPETITOR_PRICE},
            ),
            AgentRole(role="analyst", count=1, traits={"meta": True}),
        ],
        agents=agents,
    )
