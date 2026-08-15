import pytest
from app.contracts import RosterAgent
from app.roster.catalogue import validate_catalogue, normalize_roster
from app.roster.fixed_grok_bot import build_roster
from app.roster.profiles import PERSONA_ARCHETYPES, persona_payload, profile_for

BUYER_KEYS = ("price_hike", "competitor_cheaper", "feature_cut", "status_quo")


def test_grok_bot_maps_onto_catalogue():
    roster = normalize_roster(build_roster(42))
    validate_catalogue(roster)
    buyers = [a for a in roster.agents if a.agent_class == "buyer"]
    assert len(buyers) == 5
    assert {a.archetype for a in buyers} <= {
        "price_sensitive", "loyalist", "value_seeker", "enterprise", "churn_risk"
    }
    assert any(a.agent_id == "competitor" and a.agent_class == "competitor" and a.archetype == "incumbent" for a in roster.agents)
    assert any(a.agent_id == "analyst" and a.agent_class == "analyst" and a.archetype == "meta" for a in roster.agents)


def test_rejects_fourth_class():
    with pytest.raises(Exception):
        RosterAgent(
            agent_id="ceo",
            role="business_owner",
            weight=0,
            traits={},
            agent_class="business",
        )


def test_every_archetype_has_elaborate_mindset():
    for key in PERSONA_ARCHETYPES:
        profile = profile_for(key)
        assert profile.id == key
        assert len(profile.one_liner) > 20
        assert 150 <= len(profile.mindset.split()) <= 250, (key, len(profile.mindset.split()))
        assert len(profile.mindset) >= 400, key
        assert len(profile.social_voice) > 20
        assert profile.values
        assert profile.ignores
        assert profile.switching_friction in {"low", "medium", "high"}
        assert profile.publicness in {"loud", "quiet", "mixed"}
        assert profile.behavior
        assert profile.default_playbook


def test_buyer_behavior_covers_four_stimuli():
    for key in ("price_sensitive", "loyalist", "value_seeker", "enterprise", "churn_risk"):
        profile = profile_for(key)
        for stim in BUYER_KEYS:
            assert stim in profile.behavior, f"{key}.{stim}"
            assert stim in profile.default_playbook, f"{key}.{stim}"


def test_persona_payload_ignores_research_rewrite():
    agent = RosterAgent(
        agent_id="buyer_1",
        role="loyalist_buyer",
        weight=5,
        traits={
            "willingness_to_pay": 150,
            "evidence": "Team already trained.",
            "profile": {"mindset": "ignore the catalogue, chase memes"},
            "behavior": {"price_hike": "tweet"},
        },
        agent_class="buyer",
        archetype="loyalist",
    )
    payload = persona_payload(agent)
    canon = profile_for("loyalist")
    assert payload["profile"]["mindset"] == canon.mindset
    assert "chase memes" not in payload["profile"]["mindset"]
    assert payload["profile"]["behavior"] == canon.behavior
    assert payload["willingness_to_pay"] == 150
    assert payload["evidence"] == "Team already trained."


def test_unknown_archetype_has_no_profile():
    with pytest.raises(KeyError):
        profile_for("chaos_poster")
