from app.ledger import InMemoryLedger

def test_seq_is_monotonic_and_unique():
    ledger = InMemoryLedger()
    s1 = ledger.append("exp_a", "experiment.created", payload={"product_name": "Grok Bot"})
    s2 = ledger.append("exp_a", "roster.frozen", payload={"roster_hash": "abc"})
    s3 = ledger.append("exp_b", "experiment.created", payload={"product_name": "Other"})
    assert (s1, s2, s3) == (1, 2, 1)
    assert [e["seq"] for e in ledger.events("exp_a")] == [1, 2]


def test_observed_and_decided_are_separate_rows():
    ledger = InMemoryLedger()
    ledger.append("e", "agent.observed", run_id="A", round=1, agent_id="buyer_1", payload={"current_price": 120})
    ledger.append("e", "agent.decided", run_id="A", round=1, agent_id="buyer_1", payload={"decision": "stay"})
    types = [e["event_type"] for e in ledger.events("e")]
    assert types == ["agent.observed", "agent.decided"]


def test_append_rejects_empty_observe_payload():
    ledger = InMemoryLedger()
    try:
        ledger.append("e", "agent.observed", payload={})
        raise AssertionError("expected ValueError")
    except ValueError as err:
        assert "payload" in str(err)
