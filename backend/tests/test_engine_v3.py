"""v3 tests — HDFC Millennia merchant-specific caps, IDFC per-Rs200,
Kotak accelerated cap, Amex per-Rs50, AU CS and RBL."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine import UserCard, calculate_card  # noqa: E402
from app.seed import seed_cards  # noqa: E402


def _get(cid):
    return [c for c in seed_cards() if c.id == cid][0]


def _uc(cid, **kw):
    return UserCard(id="u", card=_get(cid), usage_known=True, **kw)


def test_hdfc_millennia_listed_merchant_5pct_capped():
    uc = _uc("hdfc-millennia", cap_usage_by_group={"accelerated": 0, "other": 0})
    r = calculate_card(uc, "Amazon", "online_shopping", 30000, channel="online", mcc_known=True)
    assert r.reward_value_inr == 1000  # 5% = 1500, capped at 1000


def test_hdfc_millennia_unlisted_merchant_gets_1pct_not_5():
    uc = _uc("hdfc-millennia", cap_usage_by_group={"accelerated": 0, "other": 0})
    r = calculate_card(uc, "SomeOtherStore", "online_shopping", 10000, channel="online", mcc_known=True)
    assert r.reward_value_inr == 100


def test_idfc_wealth_per_200_not_150():
    uc = _uc("idfc-wealth")
    r = calculate_card(uc, "Restaurant", "food_delivery", 5000, mcc_known=True)
    # floor(5000/200)=25 blocks x 10 = 250 points x 0.25 = Rs 62.50
    assert r.points_earned == 250
    assert r.reward_value_inr == 62.5


def test_idfc_wealth_below_200_gets_nothing():
    uc = _uc("idfc-wealth")
    r = calculate_card(uc, "Store", "general", 150, mcc_known=True)
    assert not r.eligible


def test_kotak_accelerated_cap_750():
    uc = _uc("kotak-cashback-plus-prime", cap_usage_by_group={"accelerated": 0})
    r = calculate_card(uc, "Swiggy", "food_delivery", 20000, mcc_known=True)
    assert r.reward_value_inr == 750  # 5% = 1000, capped at 750


def test_amex_per_50():
    uc = _uc("amex-platinum-travel")
    r = calculate_card(uc, "Store", "general", 5000, mcc_known=True)
    assert r.points_earned == 100  # 5000/50


def test_au_cs_dining_8_per_100():
    uc = _uc("au-cs")
    r = calculate_card(uc, "Restaurant", "food_delivery", 1000, mcc_known=True)
    assert r.points_earned == 80


def test_rbl_online_2x_capped_at_250_value():
    uc = _uc("rbl-platinum-plus", cap_usage_by_group={"online_bonus": 0})
    r = calculate_card(uc, "Store", "online_shopping", 20000, channel="online", mcc_known=True)
    # 2 points/100 = 400 points x 0.25 = Rs 100, under Rs 250 cap
    assert r.reward_value_inr == 100
    r2 = calculate_card(_uc("rbl-platinum-plus", cap_usage_by_group={"online_bonus": 0}),
                        "Store", "online_shopping", 100000, channel="online", mcc_known=True)
    assert r2.reward_value_inr == 250
