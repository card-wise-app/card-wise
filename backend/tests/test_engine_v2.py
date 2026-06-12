"""v2 engine tests — SBI group+aggregate caps, ICICI Prime split,
Axis Airtel base-linked caps and partner value-back."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine import calculate_card  # noqa: E402
from app.seed import seed_cards  # noqa: E402
from app.engine import UserCard  # noqa: E402


def _get(cid):
    return [c for c in seed_cards() if c.id == cid][0]


def test_sbi_online_group_cap_and_aggregate():
    # Rs 50,000 online at 5% = Rs 2,500 gross, online group cap Rs 2,000
    uc = UserCard(id="u", card=_get("sbi-cashback"), monthly_reward_used_inr=0,
                  usage_known=True, cap_usage_by_group={"online": 0, "offline": 0})
    r = calculate_card(uc, "Amazon", "online_shopping", 50000, channel="online", mcc_known=True)
    assert r.reward_value_inr == 2000
    assert r.confidence == "exact"


def test_sbi_aggregate_cap_binds():
    # Already earned Rs 3,900 this cycle, new Rs 5,000 online = Rs 250 gross,
    # aggregate remaining is only Rs 100
    uc = UserCard(id="u", card=_get("sbi-cashback"), monthly_reward_used_inr=3900,
                  usage_known=True, cap_usage_by_group={"online": 1900, "offline": 2000})
    r = calculate_card(uc, "Amazon", "online_shopping", 5000, channel="online", mcc_known=True)
    assert r.reward_value_inr == 100


def test_sbi_unknown_group_usage_is_estimated():
    uc = UserCard(id="u", card=_get("sbi-cashback"), usage_known=False)
    r = calculate_card(uc, "Amazon", "online_shopping", 5000, channel="online")
    assert r.confidence == "estimated"


def test_icici_prime_vs_nonprime():
    prime = UserCard(id="p", card=_get("amazon-pay-icici"), usage_known=True,
                     memberships={"amazon_prime": True})
    non = UserCard(id="n", card=_get("amazon-pay-icici"), usage_known=True,
                   memberships={"amazon_prime": False})
    rp = calculate_card(prime, "Amazon", "online_shopping", 5000, mcc_known=True)
    rn = calculate_card(non, "Amazon", "online_shopping", 5000, mcc_known=True)
    assert rp.reward_value_inr == 250
    assert rn.reward_value_inr == 150
    assert rp.redemption_type == "amazon_pay_balance"


def test_axis_airtel_base_linked_cap():
    # Base earned Rs 100 this cycle -> Airtel 25% cap is 2x = Rs 200
    uc = UserCard(id="u", card=_get("axis-airtel"), usage_known=True,
                  base_cashback_earned_inr=100, base_cashback_known=True)
    r = calculate_card(uc, "Airtel", "airtel_bill", 5000, mcc_known=True)
    # 25% of 5000 = 1250, capped at 200
    assert r.reward_value_inr == 200


def test_axis_airtel_unknown_base_is_estimated():
    uc = UserCard(id="u", card=_get("axis-airtel"), usage_known=True,
                  base_cashback_known=False)
    r = calculate_card(uc, "Airtel", "airtel_bill", 5000, mcc_known=True)
    assert r.confidence == "estimated"


def test_axis_partner_value_back_is_not_statement_credit():
    uc = UserCard(id="u", card=_get("axis-airtel"), usage_known=True)
    r = calculate_card(uc, "Zomato", "food_delivery", 1000, channel="online", mcc_known=True)
    assert r.reward_value_inr == 100  # 10% of 1000, under Rs 200 partner cap
    assert r.redemption_type == "partner_wallet"
    assert "partner wallet" in r.reason


def test_axis_partner_min_order():
    uc = UserCard(id="u", card=_get("axis-airtel"), usage_known=True)
    r = calculate_card(uc, "Zomato", "food_delivery", 300, channel="online", mcc_known=True)
    assert not r.eligible
