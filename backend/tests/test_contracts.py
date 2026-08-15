"""US-X1: frozen field names and enums match architecture.md §9 and §11."""

from app.contracts import (
    Adapter,
    BuyerDecision,
    CompetitorDecision,
    CreateExperimentRequest,
    ExperimentPaper,
    RunId,
    Status,
    VariableType,
)

SECTION_9_1 = {
    "product_name": "Acme Analytics",
    "product_description": "B2B analytics dashboard for e-commerce teams",
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
    "adapter": "cursor",
}


def test_create_request_accepts_section_9_1_payload():
    req = CreateExperimentRequest.model_validate(SECTION_9_1)
    dumped = req.model_dump(mode="json")
    assert dumped["variable_type"] == "price_change"
    assert dumped["adapter"] == "cursor"
    assert dumped["rounds"] == 8
    assert set(dumped) == set(SECTION_9_1)


def test_adapter_status_and_decision_enums():
    assert {m.value for m in Adapter} == {"cursor", "fixture"}
    assert {m.value for m in VariableType} == {"price_change"}
    assert {m.value for m in RunId} == {"A", "B"}
    assert {m.value for m in BuyerDecision} == {"stay", "churn", "switch"}
    assert {m.value for m in CompetitorDecision} == {"hold", "undercut", "match"}
    assert {m.value for m in Status} == {
        "created",
        "running_a",
        "running_b",
        "attributing",
        "complete",
        "failed",
    }


def test_experiment_paper_round_trips_section_9_2_shape():
    paper = ExperimentPaper.model_validate(
        {
            "id": "exp_acme",
            "status": "complete",
            "experiment": SECTION_9_1,
            "roster": {"agent_roles": [], "agents": []},
            "receipt": {
                "random_seed": 42,
                "prompt_hash": "sha256:abc",
                "roster_hash": "sha256:def",
                "other_variables_changed": 0,
                "adapter": "cursor",
                "runtime": "local",
                "model": "composer-2.5",
                "tools": [],
            },
            "metrics": {
                "share_a": [80],
                "share_b": [80],
                "mrr_a": [1176],
                "mrr_b": [1416],
                "final_share_delta_pp": -10,
                "final_mrr_delta": 51,
                "final_churn_count_b": 4,
            },
            "divergence_by_round": [],
            "summary_narrative": {
                "text": "Raising price +20% changed share.",
                "citations": [{"agent_id": "buyer_3", "round": 4, "run_id": "B"}],
            },
            "logs": {"run_a": [], "run_b": []},
        }
    )
    dumped = paper.model_dump(mode="json")
    assert dumped["receipt"]["other_variables_changed"] == 0
    assert dumped["receipt"]["runtime"] == "local"
    assert set(dumped) == {
        "id",
        "status",
        "experiment",
        "roster",
        "receipt",
        "metrics",
        "divergence_by_round",
        "summary_narrative",
        "logs",
    }
