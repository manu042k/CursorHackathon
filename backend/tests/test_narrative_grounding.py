"""US-B6: grounded template narrative, required citations, receipt hashes."""

import pytest

from app.contracts import (
    CreateExperimentRequest,
    MetricSeries,
    NarrativeCitation,
    Roster,
    RosterAgent,
    RunId,
)
from app.narrative import (
    DECISION_PROMPT_TEMPLATE,
    NarrativeGroundingError,
    build_receipt,
    canonical_hash,
    grounded_narrative,
    validate_narrative,
)


def _experiment() -> CreateExperimentRequest:
    return CreateExperimentRequest.model_validate(
        {
            "product_name": "Acme Analytics",
            "product_description": "B2B analytics",
            "current_price": 49,
            "market_size": 30,
            "competitor_count": 1,
            "competitor_price": 45,
            "buyer_price_sensitivity": "medium",
            "rounds": 8,
            "random_seed": 42,
            "variable_type": "price_change",
            "variable_delta": "+20%",
            "applies_from_round": 1,
            "adapter": "fixture",
        }
    )


def _logs() -> tuple[dict, dict]:
    log = {
        "round": 4,
        "agent_id": "buyer_3",
        "run_id": "B",
        "decision": "churn",
        "reason": "Price $59 is at my willingness to pay of $55; I leave for $45.",
        "confidence": 0.8,
    }
    run_b = {"agent_logs": [log], "trajectory": []}
    run_a = {
        "agent_logs": [{**log, "run_id": "A", "decision": "stay"}],
        "trajectory": [],
    }
    return run_a, run_b


def test_template_narrative_requires_citations():
    run_a, run_b = _logs()
    metrics = MetricSeries(
        share_a=[80, 76],
        share_b=[80, 66],
        mrr_a=[1176, 1117],
        mrr_b=[1416, 1168],
        final_share_delta_pp=-10,
        final_mrr_delta=51,
        final_churn_count_b=2,
    )
    divergence = [
        {
            "round": 4,
            "delta": 9,
            "top_contributors": [
                {
                    "agent_id": "buyer_3",
                    "contribution_pct": 62,
                    "reason": "Price $59 is at my willingness to pay of $55; I leave for $45.",
                }
            ],
        }
    ]
    narrative = grounded_narrative(_experiment(), metrics, divergence, run_a, run_b)
    assert narrative.citations
    assert narrative.citations[0].agent_id == "buyer_3"
    assert narrative.citations[0].round == 4
    assert "Raising price +20%" in narrative.text
    assert "buyer_3" in narrative.text
    assert "round 4" in narrative.text


def test_receipt_includes_hashes_and_zero_other_variables():
    roster = Roster(agents=[RosterAgent(agent_id="buyer_1", role="buyer", weight=8, traits={})])
    receipt = build_receipt(_experiment(), roster)
    assert receipt.random_seed == 42
    assert receipt.prompt_hash == canonical_hash(DECISION_PROMPT_TEMPLATE)
    assert receipt.roster_hash.startswith("sha256:")
    assert len(receipt.roster_hash) == 71
    assert receipt.other_variables_changed == 0
    assert receipt.adapter.value == "fixture"
    assert receipt.runtime.value == "local"
    assert receipt.model == "fixture"
    assert receipt.tools == []


def test_narrative_mentioning_agent_not_in_logs_is_rejected():
    run_a, run_b = _logs()
    citations = [NarrativeCitation(agent_id="buyer_3", round=4, run_id=RunId.B)]
    with pytest.raises(NarrativeGroundingError, match="not in logs"):
        validate_narrative(
            "buyer_99 caused the gap at round 4.",
            citations,
            run_a,
            run_b,
        )
