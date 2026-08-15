"""US-A4: canned Acme decisions. Pitch-quality reasons, 8×2×agents."""

from __future__ import annotations

from app.contracts import AgentDecision, AgentDecisionRequest, RunId
from app.roster.fixed_acme import BUYER_SPECS, build_roster

CHURN_A = {"buyer_1": 3, "buyer_2": None, "buyer_3": None, "buyer_4": None, "buyer_5": None}
CHURN_B = {"buyer_1": 2, "buyer_2": 4, "buyer_3": 4, "buyer_4": None, "buyer_5": None}
WTP = {row[0]: row[3] for row in BUYER_SPECS}


class FixtureAdapter:
    def __init__(self) -> None:
        self.roster = build_roster(42)
        self._ids = [a.agent_id for a in self.roster.agents]

    def agent_ids(self) -> list[str]:
        return list(self._ids)

    async def decide(self, request: AgentDecisionRequest) -> AgentDecision:
        if request.agent_id.startswith("buyer_"):
            return self._buyer(request)
        if request.agent_id == "competitor":
            return self._competitor(request)
        if request.agent_id == "analyst":
            return self._analyst(request)
        raise KeyError(f"unknown agent {request.agent_id}")

    def _buyer(self, request: AgentDecisionRequest) -> AgentDecision:
        wtp = float(request.persona.get("willingness_to_pay", WTP[request.agent_id]))
        price = request.current_price
        churn_map = CHURN_B if price >= 59 else CHURN_A
        churn_round = churn_map[request.agent_id]
        if churn_round and request.round >= churn_round:
            if price > wtp + 5:
                return AgentDecision(
                    decision="churn",
                    reason=(
                        f"Price now ${price:.0f} is ${price - wtp:.0f} above my willingness "
                        f"to pay of ${wtp:.0f}; competitor is ${request.competitor_price:.0f}. I leave."
                    ),
                    confidence=0.84,
                )
            return AgentDecision(
                decision="switch",
                reason=(
                    f"Price ${price:.0f} sits on my willingness to pay of ${wtp:.0f}; "
                    f"I switch to the competitor at ${request.competitor_price:.0f}."
                ),
                confidence=0.8,
            )
        gap = price - wtp
        if gap <= 0:
            reason = (
                f"Price ${price:.0f} is ${abs(gap):.0f} under my willingness to pay of "
                f"${wtp:.0f}; I stay subscribed."
            )
        else:
            reason = (
                f"Price ${price:.0f} is ${gap:.0f} over my willingness to pay of ${wtp:.0f}, "
                f"but I stay subscribed this round."
            )
        return AgentDecision(decision="stay", reason=reason, confidence=0.7)

    def _competitor(self, request: AgentDecisionRequest) -> AgentDecision:
        if request.current_price >= 59 and request.round >= 4:
            return AgentDecision(
                decision="match",
                reason=(
                    f"Your price is ${request.current_price:.0f} and share is slipping; "
                    f"I match ${request.current_price:.0f} to stop further loss."
                ),
                confidence=0.76,
            )
        return AgentDecision(
            decision="hold",
            reason=(
                f"I hold competitor price at ${request.competitor_price:.0f} while "
                f"your list price is ${request.current_price:.0f} this round."
            ),
            confidence=0.72,
        )

    def _analyst(self, request: AgentDecisionRequest) -> AgentDecision:
        if request.current_price >= 59 and request.round == 4:
            return AgentDecision(
                decision="note",
                reason=(
                    "Divergence opens at round 4: price-sensitive buyers near WTP $52–$55 "
                    "churn; the competitor matches price."
                ),
                confidence=0.9,
            )
        return AgentDecision(
            decision="note",
            reason=(
                f"Run {request.run_id.value} round {request.round}: price "
                f"${request.current_price:.0f}, watching share."
            ),
            confidence=0.85,
        )
