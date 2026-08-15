"""Market snapshot and metrics. Architecture §7.2–7.3."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.contracts import Roster


def parse_price_delta(base: float, delta: str) -> float:
    """Apply a single price intervention. Percent deltas round to nearest dollar (49 +20% → 59)."""
    text = delta.strip()
    if text.endswith("%"):
        pct = float(text[:-1])
        return float(round(base * (1 + pct / 100.0)))
    return base + float(text)


@dataclass
class Market:
    current_price: float
    competitor_price: float
    subscribed: dict[str, float]
    total_weight: float
    buyer_order: list[str] = field(default_factory=list)

    def share(self) -> float:
        return 100.0 * sum(self.subscribed.values()) / self.total_weight

    def mrr(self) -> float:
        return sum(self.subscribed.values()) * self.current_price

    def snapshot(self) -> dict[str, float | dict[str, float]]:
        return {
            "current_price": self.current_price,
            "competitor_price": self.competitor_price,
            "share": self.share(),
            "mrr": self.mrr(),
            "subscribed": dict(self.subscribed),
        }

    def copy(self) -> Market:
        return Market(
            current_price=self.current_price,
            competitor_price=self.competitor_price,
            subscribed=dict(self.subscribed),
            total_weight=self.total_weight,
            buyer_order=list(self.buyer_order),
        )


def market_from_roster(roster: Roster, current_price: float, competitor_price: float) -> Market:
    buyers = [a for a in roster.agents if a.agent_id.startswith("buyer_")]
    subscribed = {a.agent_id: a.weight for a in buyers}
    total = sum(subscribed.values())
    if total <= 0:
        raise ValueError("roster has no buyer weight")
    return Market(
        current_price=current_price,
        competitor_price=competitor_price,
        subscribed=subscribed,
        total_weight=total,
        buyer_order=[a.agent_id for a in buyers],
    )
