"""Deterministic engine tests - PRD section 15 acceptance cases."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine import Card, RewardRule, UserCard, calculate_card, recommend  # noqa: E402
from app.seed import seed_cards  # noqa: E402


def _sbi(used=0, known=True):
    card = [c for c in seed_cards() if c.id == "sbi-cashback"][0]
    return UserCard(id="u1", card=card, monthly_reward_used_inr=used, usage_known=known)


def test_prd_cashback_cap_example():
    # PRD 6.4: Rs 5,000 at 5% = Rs 250 theoretical, remaining cap Rs 100 -> Rs 100
    card = Card(id="t", issuer="Test", name="Test", monthly_cap_inr=1900)
    uc = UserCard(id="u", card=card, monthly_reward_used_inr=1800, usage_known=True)
    card.rules = [RewardRule(category="general", cashback_rate_pct=5)]
    r = calculate_card(uc, "Amazon", "general", 5000, mcc_known=True)
    assert r.reward_value_inr == 100
    assert r.confidence == "exact"


def test_points_floor_rule():
    # PRD 6.4: 5 points per Rs 150
    card = Card(id="t", issuer="Test", name="Test")
    card.rules = [RewardRule(category="general", points_per_block=5, block_amount_inr=150, point_value_inr=0.25)]
    uc = UserCard(id="u", card=card, usage_known=True)
    r = calculate_card(uc, "Store", "general", 5000, mcc_known=True)
    # floor(5000/150)=33 blocks x 5 = 165 points x 0.25 = Rs 41.25
    assert r.points_earned == 165
    assert r.reward_value_inr == 41.25


def test_unknown_cap_is_estimated_not_assumed_unused():
    uc = _sbi(used=0, known=False)
    r = calculate_card(uc, "Amazon", "online_shopping", 5000, channel="online")
    assert r.confidence == "estimated"
    assert "unknown" in r.reason.lower()


def test_excluded_card_is_shown_not_hidden():
    # v2: SBI fuel exclusion is FAQ-confirmed. Government is NOT
    # hard-coded for SBI (its full T&C list is still pending), so
    # use fuel here. Axis Airtel government exclusion is tested
    # separately via its own T&C list in the seed.
    cards = seed_cards()
    sbi = [c for c in cards if c.id == "sbi-cashback"][0]
    uc = UserCard(id="u1", card=sbi, usage_known=True)
    out = recommend([uc], "Petrol Pump", "fuel", 5000)
    assert out["best"] is None
    assert len(out["excluded"]) == 1


def test_amazon_5000_example_ranks_sbi_and_amazon_pay_top():
    cards = {c.id: c for c in seed_cards()}
    ucs = [
        UserCard(id="1", card=cards["sbi-cashback"], usage_known=True),
        UserCard(id="2", card=cards["amazon-pay-icici"], usage_known=True),
        UserCard(id="3", card=cards["hdfc-millennia"], usage_known=True),
        UserCard(id="4", card=cards["axis-airtel"], usage_known=True),
    ]
    out = recommend(ucs, "Amazon", "online_shopping", 5000, channel="online", mcc_known=True)
    assert out["best"].reward_value_inr == 250
    assert out["best"].card_name in ("SBI Cashback Card", "Amazon Pay ICICI")
    assert len(out["alternatives"]) >= 1
