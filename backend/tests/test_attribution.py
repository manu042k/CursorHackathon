"""US-B4: decision-diff attribution with a 2-round known-percentage fixture."""

from app.attribution import METHOD, attribute_runs
from app.contracts import Roster, RosterAgent


def _roster() -> Roster:
    return Roster(
        agents=[
            RosterAgent(agent_id="buyer_a", role="buyer", weight=3, traits={}),
            RosterAgent(agent_id="buyer_b", role="buyer", weight=1, traits={}),
            RosterAgent(agent_id="competitor", role="incumbent_competitor", weight=0, traits={}),
            RosterAgent(agent_id="analyst", role="analyst", weight=99, traits={"meta": True}),
        ]
    )


def _log(round_n: int, agent_id: str, run_id: str, decision: str, reason: str = "x" * 40) -> dict:
    return {
        "round": round_n,
        "agent_id": agent_id,
        "run_id": run_id,
        "decision": decision,
        "reason": reason,
        "confidence": 0.8,
    }


def _run(shares: list[float], logs: list[dict]) -> dict:
    return {
        "trajectory": [
            {"round": i + 1, "share": share, "mrr": 0, "current_price": 49, "competitor_price": 45}
            for i, share in enumerate(shares)
        ],
        "agent_logs": logs,
    }


def test_only_differing_decisions_get_mass_and_known_percentages():
    run_a = _run(
        [80, 80],
        [
            _log(1, "buyer_a", "A", "stay"),
            _log(1, "buyer_b", "A", "stay"),
            _log(1, "competitor", "A", "hold"),
            _log(1, "analyst", "A", "note"),
            _log(2, "buyer_a", "A", "stay"),
            _log(2, "buyer_b", "A", "stay"),
            _log(2, "competitor", "A", "hold"),
            _log(2, "analyst", "A", "note"),
        ],
    )
    run_b = _run(
        [80, 70],
        [
            _log(1, "buyer_a", "B", "stay"),
            _log(1, "buyer_b", "B", "stay"),
            _log(1, "competitor", "B", "hold"),
            _log(1, "analyst", "B", "note"),
            _log(2, "buyer_a", "B", "churn"),
            _log(2, "buyer_b", "B", "stay"),
            _log(2, "competitor", "B", "match"),
            _log(2, "analyst", "B", "flag"),
        ],
    )
    result = attribute_runs(run_a, run_b, _roster())
    assert result["method"] == METHOD == "decision_diff_v1"
    assert result["analyst_weight"] == 0
    round_1 = result["divergence_by_round"][0]
    round_2 = result["divergence_by_round"][1]
    assert round_1["top_contributors"] == []
    agents = {row["agent_id"]: row["contribution_pct"] for row in round_2["top_contributors"]}
    assert set(agents) == {"buyer_a", "competitor"}
    assert "analyst" not in agents
    assert "buyer_b" not in agents
    assert agents["buyer_a"] == 75
    assert agents["competitor"] == 25
    assert abs(sum(agents.values()) - 100) < 1e-9
    assert result["unattributed"] is False


def test_unattributed_when_metrics_move_without_decision_diff():
    run_a = _run(
        [80, 80],
        [_log(1, "buyer_a", "A", "stay"), _log(2, "buyer_a", "A", "stay")],
    )
    run_b = _run(
        [80, 70],
        [_log(1, "buyer_a", "B", "stay"), _log(2, "buyer_a", "B", "stay")],
    )
    result = attribute_runs(run_a, run_b, _roster())
    assert result["unattributed"] is True
    assert result["divergence_by_round"][1]["top_contributors"] == []
    assert result["divergence_by_round"][1]["unattributed"] is True
    assert result["method"] == "decision_diff_v1"
