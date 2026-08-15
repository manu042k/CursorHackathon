"""US-X2: golden Acme artifacts exist and match the paper contract / spec §10 shape."""

from pathlib import Path

from app.contracts import ExperimentPaper

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "data" / "experiments" / "acme-seed-42"
FRONTEND_PAPER = ROOT / "frontend" / "src" / "data" / "acme-seed-42.json"


def test_five_artifacts_present():
    for name in ("experiment.json", "roster.json", "run_a.json", "run_b.json", "attribution.json"):
        path = GOLDEN / name
        assert path.is_file(), path
        assert path.stat().st_size > 0


def test_frontend_paper_validates_and_matches_spec_shape():
    paper = ExperimentPaper.model_validate_json(FRONTEND_PAPER.read_text())
    assert paper.id == "acme-seed-42"
    assert paper.status.value == "complete"
    assert paper.receipt.adapter.value == "fixture"
    assert paper.receipt.other_variables_changed == 0
    assert paper.metrics.final_share_delta_pp == -10
    assert paper.metrics.final_mrr_delta == 51
    assert paper.metrics.share_a[-1] == 76
    assert paper.metrics.share_b[-1] == 66
    assert paper.metrics.mrr_b[-1] > paper.metrics.mrr_a[-1]
    # divergence opens around round 4
    assert paper.metrics.share_a[3] - paper.metrics.share_b[3] >= 8
    r4 = next(d for d in paper.divergence_by_round if d.round == 4)
    assert abs(sum(c.contribution_pct for c in r4.top_contributors) - 100) < 0.01
    assert any(c.agent_id == "buyer_3" for c in r4.top_contributors)
    cited = {(c.agent_id, c.round, c.run_id.value) for c in paper.summary_narrative.citations}
    assert ("buyer_3", 4, "B") in cited
    b3 = next(
        log
        for log in paper.logs.run_b
        if log.round == 4 and log.agent_id == "buyer_3"
    )
    assert "willingness to pay" in b3.reason.lower() or "WTP" in b3.reason
    assert len(b3.reason) >= 40
