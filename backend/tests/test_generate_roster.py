from app.contracts import Adapter, CreateExperimentRequest
from app.roster.catalogue import validate_catalogue
from app.roster.generate import propose_roster


def _body(description: str) -> CreateExperimentRequest:
    return CreateExperimentRequest(
        product_name="Grok Bot",
        product_description=description,
        current_price=120,
        market_size=30,
        competitor_count=1,
        competitor_price=100,
        buyer_price_sensitivity="medium",
        rounds=4,
        random_seed=42,
        variable_type="price_change",
        variable_delta="+20%",
        applies_from_round=1,
        adapter=Adapter.fixture,
    )


def test_fixture_proposal_is_valid_catalogue():
    roster = propose_roster(_body("Always-on AI teammates"), adapter=Adapter.fixture)
    validate_catalogue(roster)
    assert len([a for a in roster.agents if a.agent_id.startswith("buyer_")]) == 5


def test_same_seed_same_roster():
    a = propose_roster(_body("Always-on AI teammates"), adapter=Adapter.fixture)
    b = propose_roster(_body("Always-on AI teammates"), adapter=Adapter.fixture)
    assert a.model_dump() == b.model_dump()


def test_consumer_box_differs_from_saas():
    saas = propose_roster(_body("Always-on AI teammates"), adapter=Adapter.fixture)
    box = propose_roster(_body("A consumer subscription box of snacks"), adapter=Adapter.fixture)
    assert saas.model_dump() != box.model_dump()


def test_distill_maps_labels_and_does_not_author_mindset():
    from app.roster.catalogue import normalize_roster, validate_catalogue
    from app.roster.profiles import persona_payload, profile_for
    from app.roster.research.distill import distill

    items = [
        {"title": "price hike", "text": "We switched after a 20% price hike; not worth it anymore."},
        {"title": "support", "text": "Been saying this for months. Support never replied. Hiking price is the last straw."},
        {"title": "compare", "text": "Compared feature lists; competitor is close and $20 less. Still deciding."},
        {"title": "legal", "text": "Legal and SSO review; we renew if it stays in budget."},
        {"title": "trained", "text": "Team already trained. They’ve earned this even if it costs more."},
    ]
    roster = normalize_roster(distill(items, _body("Always-on AI teammates")))
    validate_catalogue(roster)
    buyers = [a for a in roster.agents if a.agent_class == "buyer"]
    assert len(buyers) == 5
    for agent in roster.agents:
        assert "mindset" not in agent.traits
        assert "behavior" not in agent.traits
        assert "profile" not in agent.traits
        payload = persona_payload(agent)
        assert payload["profile"]["mindset"] == profile_for(agent.archetype).mindset
