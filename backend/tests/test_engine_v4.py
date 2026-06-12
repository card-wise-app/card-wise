"""IndusInd Pinnacle World tests (v4, 3 Nov 2026).

Official IndusInd credit-card page: 2.5 points / Rs 100 online
e-commerce. Official IndusInd blog: 1.5 / Rs 100 e-com travel.
Point value Rs 0.75 cash credit (HF range 0.75-1.88% corroborates).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.engine import UserCard
from app.seed import seed_cards


def _uc():
    card = next(c for c in seed_cards() if c.id == "indusind-pinnacle")
    return UserCard(id="u1", card=card, usage_known=True, monthly_reward_used_inr=0)


def test_pinnacle_online_10000():
    from app.engine import calculate_card
    r = calculate_card(_uc(), "Amazon", "online_shopping", 10000, "online", True)
    assert r.eligible and r.points_earned == 250 and r.reward_value_inr == 187.50, r


def test_pinnacle_travel_online_10000():
    from app.engine import calculate_card
    r = calculate_card(_uc(), "MakeMyTrip", "travel", 10000, "online", True)
    assert r.points_earned == 150 and r.reward_value_inr == 112.50, r


def test_pinnacle_general_10000():
    from app.engine import calculate_card
    r = calculate_card(_uc(), "Store", "general", 10000, "any", True)
    assert r.points_earned == 100 and r.reward_value_inr == 75.0, r


def test_pinnacle_fractional_block():
    # 2.5 points per Rs 100: Rs 500 online = 12.5 points = Rs 9.38
    # (rounded to 2dp in reward_value; points stay fractional).
    from app.engine import calculate_card
    r = calculate_card(_uc(), "Amazon", "online_shopping", 500, "online", True)
    assert r.points_earned == 12.5 and r.reward_value_inr == 9.38, r


def test_pinnacle_fuel_excluded():
    from app.engine import calculate_card
    r = calculate_card(_uc(), "Petrol", "fuel", 5000, "any", True)
    assert not r.eligible and "Excluded" in r.reason, r
