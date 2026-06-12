"""CardWise deterministic rewards engine — v2.

PRD rule: Do NOT use an LLM to calculate financial rewards.
All monetary calculations here are plain code, with explicit
cap, exclusion, rounding and confidence handling.

v2 additions (from official SBI / ICICI / Axis docs, 3 Nov 2026):
- Per-group statement-cycle caps (e.g. SBI online Rs 2,000
  separate from offline Rs 2,000) plus an aggregate cycle cap
  (SBI Rs 4,000). The old single monthly_cap is kept for
  backward compatibility, but v2 cards use group + aggregate.
- Posting basis: "posting_date" vs "transaction_date".
  SBI accrues on posting/settlement date, not transaction date.
  The engine records this; a pre-purchase recommendation is
  therefore an estimate unless the posting date is known to
  fall in the same cycle.
- Membership-conditioned rules: ICICI Amazon Pay Prime 5%
  vs non-Prime 3% (digital/gift 2%), partner merchants 2%.
- Base-linked caps: Axis Airtel accelerated cashback is
  capped at 2x (Airtel) / 1x (utility) the base cashback
  earned in the same cycle. That cap cannot be known from
  one transaction alone — it needs base_cashback_earned_inr.
- Partner value-back: credited to a partner wallet, not
  statement credit, with its own per-partner cap.
- Transaction fees: subtracted from net reward only when
  directly tied to that transaction (e.g. ICICI wallet-load
  fee from 15 Jan 2026), never an annual fee spread across
  transactions (PRD 6.4).

Confidence:
- "exact" only when every applicable cap usage is known
  AND MCC is known.
- "estimated" otherwise — including when cap usage,
  base cashback, MCC, or posting cycle is unknown.
  The engine never assumes a cap is unused.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RewardRule:
    category: str = "general"
    merchant: Optional[str] = None
    channel: str = "any"  # any | online | offline
    cashback_rate_pct: Optional[float] = None
    # float, not int: IndusInd Pinnacle earns 2.5 / 1.5 points
    # per Rs 100, which cannot be represented as an int.
    points_per_block: Optional[float] = None
    block_amount_inr: Optional[float] = None
    point_value_inr: float = 0.25
    min_transaction_inr: float = 0
    min_order_inr: float = 0
    per_transaction_cap_inr: Optional[float] = None
    # v2: group cap
    cap_group: Optional[str] = None
    cap_scope: str = "statement_cycle"  # statement_cycle | monthly | quarterly | annual
    cap_value_inr: Optional[float] = None
    # v2: base-linked cap, e.g. Axis Airtel 2.0 / 1.0
    cap_multiplier_of_base: Optional[float] = None
    # v2: membership condition: "prime" | "non_prime" | None
    requires_membership: Optional[str] = None
    # v2: statement_credit | amazon_pay_balance | partner_wallet | points
    redemption_type: str = "statement_credit"
    coupon_required: bool = False
    # v2: transaction-specific fee, subtracted from net reward
    transaction_fee_pct: Optional[float] = None
    transaction_fee_min_amount_inr: float = 0


@dataclass
class Card:
    id: str
    issuer: str
    name: str
    network: str = ""
    variant: str = ""
    annual_fee_inr: float = 0
    fee_waiver_spend_inr: Optional[float] = None
    reward_system: str = "cashback"
    verification_status: str = "pending_review"
    source_url: Optional[str] = None
    source_urls: list[str] = field(default_factory=list)
    last_verified_date: Optional[str] = None
    effective_from: Optional[str] = None
    monthly_cap_inr: Optional[float] = None  # legacy single cap
    aggregate_cap_inr: Optional[float] = None
    aggregate_cap_scope: str = "statement_cycle"
    posting_basis: str = "posting_date"  # posting_date | transaction_date
    exclusions: list[str] = field(default_factory=list)
    rules: list[RewardRule] = field(default_factory=list)


@dataclass
class UserCard:
    id: str
    card: Card
    monthly_reward_used_inr: float = 0
    usage_known: bool = False
    statement_cycle_day: int = 1
    # v2
    cap_usage_by_group: dict = field(default_factory=dict)
    base_cashback_earned_inr: float = 0
    base_cashback_known: bool = False
    memberships: dict = field(default_factory=dict)  # e.g. {"amazon_prime": True}


@dataclass
class CardResult:
    user_card_id: str
    card_name: str
    issuer: str
    eligible: bool
    reward_value_inr: float
    cashback_inr: float = 0
    points_earned: float = 0
    point_value_inr: float = 0
    applied_rate: str = ""
    cap_applied_inr: Optional[float] = None
    remaining_cap_inr: Optional[float] = None
    confidence: str = "estimated"
    reason: str = ""
    net_reward_inr: float = 0
    transaction_fee_inr: float = 0
    redemption_type: str = "statement_credit"
    posting_basis: str = "posting_date"


def _membership_ok(rule: RewardRule, memberships: dict) -> bool:
    if rule.requires_membership == "prime":
        return bool(memberships.get("amazon_prime"))
    if rule.requires_membership == "non_prime":
        return not bool(memberships.get("amazon_prime"))
    return True


def _match_rule(card: Card, merchant: str, category: str, channel: str, memberships: dict) -> Optional[RewardRule]:
    merchant_l = (merchant or "").strip().lower()
    candidates = [
        r for r in card.rules
        if (r.channel in ("any", channel) or channel in ("any", ""))
        and _membership_ok(r, memberships)
    ]
    # Score: merchant match + membership-specific + category specificity
    def score(r: RewardRule) -> int:
        s = 0
        if r.merchant and r.merchant.lower() == merchant_l:
            s += 10
        if r.requires_membership:
            s += 5
        if r.category == category:
            s += 3
        elif r.category == "general":
            s += 1
        return s

    # A merchant-specific rule only applies to that merchant.
    # Otherwise a listed-merchant 5% rule would leak to every
    # merchant in the same category (HDFC Millennia bug, v3).
    scored = [(score(r), r) for r in candidates
              if (r.merchant is None and (r.category == category or r.category == "general"))
              or (r.merchant and r.merchant.lower() == merchant_l)]
    if not scored:
        return None
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]


def calculate_card(
    user_card: UserCard,
    merchant: str,
    category: str,
    amount_inr: float,
    channel: str = "any",
    mcc_known: bool = False,
) -> CardResult:
    card = user_card.card
    base = CardResult(
        user_card_id=user_card.id, card_name=card.name, issuer=card.issuer,
        eligible=False, reward_value_inr=0,
        posting_basis=card.posting_basis,
    )

    if category in card.exclusions:
        base.reason = f"Excluded: {category} is excluded for this card."
        base.confidence = "exact"
        return base

    rule = _match_rule(card, merchant, category, channel, user_card.memberships)
    if rule is None:
        base.reason = "No eligible reward rule for this merchant/category."
        base.confidence = "exact"
        return base

    if amount_inr < rule.min_transaction_inr or amount_inr < rule.min_order_inr:
        need = max(rule.min_transaction_inr, rule.min_order_inr)
        base.reason = f"Below minimum of Rs {need:,.0f}."
        base.confidence = "exact"
        return base

    # --- deterministic gross calculation ---
    points = 0
    if rule.cashback_rate_pct is not None:
        value = amount_inr * rule.cashback_rate_pct / 100.0
        applied = f"{rule.cashback_rate_pct:g}% cashback"
    elif rule.points_per_block is not None and rule.block_amount_inr:
        points = math.floor(amount_inr / rule.block_amount_inr) * rule.points_per_block
        value = points * rule.point_value_inr
        applied = (
            f"{rule.points_per_block} points per Rs {rule.block_amount_inr:,.0f}, "
            f"valued at Rs {rule.point_value_inr} per point"
        )
    else:
        base.reason = "Reward rule has no cashback rate or points rule."
        return base

    # Transaction-specific fee (net reward, PRD 6.4)
    fee = 0.0
    if rule.transaction_fee_pct is not None and amount_inr >= rule.transaction_fee_min_amount_inr:
        fee = amount_inr * rule.transaction_fee_pct / 100.0

    cap_applied = None
    remaining = None
    unknown_caps: list[str] = []

    # Per-transaction cap
    if rule.per_transaction_cap_inr is not None:
        value = min(value, rule.per_transaction_cap_inr)
        cap_applied = rule.per_transaction_cap_inr

    # Group cap (statement-cycle, e.g. SBI online / offline)
    if rule.cap_value_inr is not None:
        group = rule.cap_group or rule.category
        if user_card.usage_known:
            used = user_card.cap_usage_by_group.get(group, 0)
            rem = max(0.0, rule.cap_value_inr - used)
            value = min(value, rem)
            remaining = rem
            cap_applied = rem if cap_applied is None else min(cap_applied, rem)
        else:
            unknown_caps.append(f"{group} cap usage")

    # Base-linked cap (Axis Airtel)
    if rule.cap_multiplier_of_base is not None:
        if user_card.base_cashback_known:
            rem = rule.cap_multiplier_of_base * user_card.base_cashback_earned_inr
            value = min(value, rem)
            cap_applied = rem if cap_applied is None else min(cap_applied, rem)
        else:
            unknown_caps.append("base cashback earned this cycle")

    # Legacy single monthly cap
    if card.monthly_cap_inr is not None:
        if user_card.usage_known:
            rem = max(0.0, card.monthly_cap_inr - user_card.monthly_reward_used_inr)
            value = min(value, rem)
            remaining = rem
            cap_applied = rem if cap_applied is None else min(cap_applied, rem)
        else:
            unknown_caps.append("monthly cap usage")

    # Aggregate cap (SBI Rs 4,000)
    if card.aggregate_cap_inr is not None:
        if user_card.usage_known:
            rem = max(0.0, card.aggregate_cap_inr - user_card.monthly_reward_used_inr)
            value = min(value, rem)
            cap_applied = rem if cap_applied is None else min(cap_applied, rem)
        else:
            unknown_caps.append("aggregate cap usage")

    net = max(0.0, value - fee)

    if points:
        base.points_earned = points
        base.point_value_inr = rule.point_value_inr
    else:
        base.cashback_inr = round(value, 2)

    base.eligible = True
    base.reward_value_inr = round(value, 2)
    base.net_reward_inr = round(net, 2)
    base.transaction_fee_inr = round(fee, 2)
    base.applied_rate = applied
    base.cap_applied_inr = cap_applied
    base.remaining_cap_inr = remaining
    base.redemption_type = rule.redemption_type

    notes: list[str] = []
    if rule.redemption_type == "partner_wallet":
        notes.append("Value-back to partner wallet, not statement credit.")
    if rule.coupon_required:
        notes.append("Coupon must be applied at checkout.")
    if card.posting_basis == "posting_date":
        notes.append("Accrues on posting date, not transaction date.")

    if unknown_caps:
        base.confidence = "estimated"
        base.reason = "Estimate: " + ", ".join(unknown_caps) + " unknown, cap not assumed unused."
        if notes:
            base.reason += " " + " ".join(notes)
    elif not mcc_known:
        base.confidence = "estimated"
        base.reason = "Estimate: MCC not supplied, issuer classification may differ."
        if notes:
            base.reason += " " + " ".join(notes)
    else:
        base.confidence = "exact"
        base.reason = " ".join(notes)
    return base


def recommend(
    user_cards: list[UserCard],
    merchant: str,
    category: str,
    amount_inr: float,
    channel: str = "any",
    mcc_known: bool = False,
) -> dict:
    results = [
        calculate_card(uc, merchant, category, amount_inr, channel, mcc_known)
        for uc in user_cards
    ]
    # Rank by NET reward, not gross — fees matter (PRD 6.4)
    eligible = sorted(
        [r for r in results if r.eligible],
        key=lambda r: r.net_reward_inr, reverse=True,
    )
    excluded = [r for r in results if not r.eligible]
    best = eligible[0] if eligible else None
    return {
        "merchant": merchant,
        "category": category,
        "amount_inr": amount_inr,
        "best": best,
        "alternatives": eligible[1:],
        "excluded": excluded,
        "all": results,
    }
