"""CardWise MVP API - FastAPI + Pydantic.

Endpoints implemented (PRD section 14, MVP subset):
  GET  /cards, /cards/search, /cards/{id}
  POST /users/cards, DELETE /users/cards/{id}
  POST /users/custom-cards, PATCH /users/custom-cards/{id}
  POST /recommendations, GET /users/recommendations
  POST /users/cards/{id}/usage, GET /users/rewards

Auth is intentionally stubbed for the MVP: a single demo user
("demo-user") is used, with a TODO to replace it with real
email auth + per-user authorisation before launch. No card
numbers, CVV or OTP are ever accepted - see models.
"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .engine import Card, RewardRule, UserCard, calculate_card, recommend
from .postgres_store import get_database_url, load_cards_from_postgres
from .seed import SAMPLE_NOTICE, seed_cards

app = FastAPI(title="CardWise India MVP", version="0.3.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:3000"],
    allow_methods=["*"], allow_headers=["*"],
)


def _load_catalogue() -> dict[str, Card]:
    """Postgres when DATABASE_URL is set and has cards, else seed.

    The fallback is intentional and logged to stdout: a failed
    Postgres connection must not take the API down, and must
    not silently serve an empty catalogue. Without DATABASE_URL
    this is just the in-memory MVP store, as before.
    """
    url = get_database_url()
    if url:
        try:
            cards = load_cards_from_postgres(url)
            if cards:
                print(f"Catalogue loaded from Postgres: {len(cards)} cards.")
                return {c.id: c for c in cards}
            print("Postgres catalogue is empty, falling back to seed cards.")
        except Exception as exc:  # noqa: BLE001 - startup fallback
            print(f"Postgres catalogue load failed ({exc}), "
                  "falling back to seed cards.")
    return {c.id: c for c in seed_cards()}


CATALOGUE: dict[str, Card] = _load_catalogue()
# User cards / recommendations are still in-memory in this step.
# The catalogue swap above is the Supabase step; per-user
# persistence (user_cards table) is the next step, once auth exists.
USER_CARDS: dict[str, UserCard] = {}
CUSTOM_CARDS: dict[str, Card] = {}
RECOMMENDATION_HISTORY: list[dict] = []


def card_to_dict(c: Card) -> dict:
    return {
        "id": c.id, "issuer": c.issuer, "name": c.name, "network": c.network,
        "variant": c.variant, "annual_fee_inr": c.annual_fee_inr,
        "reward_system": c.reward_system,
        "verification_status": c.verification_status,
        "source_url": c.source_url, "source_urls": c.source_urls,
        "last_verified_date": c.last_verified_date,
        "effective_from": c.effective_from,
        "monthly_cap_inr": c.monthly_cap_inr,
        "aggregate_cap_inr": c.aggregate_cap_inr,
        "aggregate_cap_scope": c.aggregate_cap_scope,
        "posting_basis": c.posting_basis,
        "fee_waiver_spend_inr": c.fee_waiver_spend_inr,
        "exclusions": c.exclusions,
        "sample_notice": SAMPLE_NOTICE if c.verification_status == "pending_review" else None,
        "rules": [
            {"category": r.category, "merchant": r.merchant, "channel": r.channel,
             "cashback_rate_pct": r.cashback_rate_pct,
             "points_per_block": r.points_per_block,
             "block_amount_inr": r.block_amount_inr,
             "point_value_inr": r.point_value_inr,
             "min_transaction_inr": r.min_transaction_inr,
             "min_order_inr": r.min_order_inr,
             "per_transaction_cap_inr": r.per_transaction_cap_inr,
             "cap_group": r.cap_group, "cap_scope": r.cap_scope,
             "cap_value_inr": r.cap_value_inr,
             "cap_multiplier_of_base": r.cap_multiplier_of_base,
             "requires_membership": r.requires_membership,
             "redemption_type": r.redemption_type,
             "coupon_required": r.coupon_required,
             "transaction_fee_pct": r.transaction_fee_pct}
            for r in c.rules
        ],
    }


def result_to_dict(r) -> dict:
    return {
        "user_card_id": r.user_card_id, "card_name": r.card_name, "issuer": r.issuer,
        "eligible": r.eligible, "reward_value_inr": r.reward_value_inr,
        "cashback_inr": r.cashback_inr, "points_earned": r.points_earned,
        "point_value_inr": r.point_value_inr, "applied_rate": r.applied_rate,
        "cap_applied_inr": r.cap_applied_inr, "remaining_cap_inr": r.remaining_cap_inr,
        "confidence": r.confidence, "reason": r.reason,
        "net_reward_inr": r.net_reward_inr,
        "transaction_fee_inr": r.transaction_fee_inr,
        "redemption_type": r.redemption_type,
        "posting_basis": r.posting_basis,
    }


@app.get("/health")
def health():
    return {"status": "ok", "cards": len(CATALOGUE)}


@app.get("/cards")
def list_cards():
    return [card_to_dict(c) for c in CATALOGUE.values()] + [
        card_to_dict(c) for c in CUSTOM_CARDS.values()
    ]


@app.get("/cards/search")
def search_cards(q: str = ""):
    ql = q.lower()
    return [card_to_dict(c) for c in CATALOGUE.values()
            if ql in c.name.lower() or ql in c.issuer.lower()]


@app.get("/cards/{card_id}")
def get_card(card_id: str):
    c = CATALOGUE.get(card_id) or CUSTOM_CARDS.get(card_id)
    if not c:
        raise HTTPException(404, "Card not found")
    return card_to_dict(c)


class AddCardRequest(BaseModel):
    card_id: str
    monthly_reward_used_inr: float = 0
    usage_known: bool = False
    statement_cycle_day: int = 1
    cap_usage_by_group: dict = Field(default_factory=dict)
    base_cashback_earned_inr: float = 0
    base_cashback_known: bool = False
    memberships: dict = Field(default_factory=dict)


@app.get("/users/cards")
def list_user_cards():
    return [{"id": uc.id, "card": card_to_dict(uc.card),
             "monthly_reward_used_inr": uc.monthly_reward_used_inr,
             "usage_known": uc.usage_known,
             "statement_cycle_day": uc.statement_cycle_day,
             "cap_usage_by_group": uc.cap_usage_by_group,
             "base_cashback_earned_inr": uc.base_cashback_earned_inr,
             "base_cashback_known": uc.base_cashback_known,
             "memberships": uc.memberships}
            for uc in USER_CARDS.values()]


@app.post("/users/cards")
def add_user_card(req: AddCardRequest):
    card = CATALOGUE.get(req.card_id) or CUSTOM_CARDS.get(req.card_id)
    if not card:
        raise HTTPException(404, "Card not found in catalogue")
    uc = UserCard(id=str(uuid.uuid4())[:8], card=card,
                  monthly_reward_used_inr=req.monthly_reward_used_inr,
                  usage_known=req.usage_known,
                  statement_cycle_day=req.statement_cycle_day,
                  cap_usage_by_group=req.cap_usage_by_group,
                  base_cashback_earned_inr=req.base_cashback_earned_inr,
                  base_cashback_known=req.base_cashback_known,
                  memberships=req.memberships)
    USER_CARDS[uc.id] = uc
    return {"id": uc.id, "card": card_to_dict(card)}


@app.delete("/users/cards/{user_card_id}")
def remove_user_card(user_card_id: str):
    if user_card_id not in USER_CARDS:
        raise HTTPException(404, "User card not found")
    del USER_CARDS[user_card_id]
    return {"deleted": True}


class CustomCardRequest(BaseModel):
    name: str
    issuer: str = ""
    network: str = ""
    variant: str = ""
    annual_fee_inr: float = 0
    reward_system: str = "cashback"
    cashback_rate_pct: Optional[float] = None
    points_per_block: Optional[int] = None
    block_amount_inr: Optional[float] = None
    point_value_inr: float = 0.25
    monthly_cap_inr: Optional[float] = None
    exclusions: list[str] = Field(default_factory=list)
    eligible_categories: list[str] = Field(default_factory=list)


@app.post("/users/custom-cards")
def create_custom_card(req: CustomCardRequest):
    cid = f"custom-{str(uuid.uuid4())[:8]}"
    rules = []
    for cat in (req.eligible_categories or ["general"]):
        rules.append(RewardRule(category=cat, cashback_rate_pct=req.cashback_rate_pct,
                                points_per_block=req.points_per_block,
                                block_amount_inr=req.block_amount_inr,
                                point_value_inr=req.point_value_inr))
    card = Card(id=cid, issuer=req.issuer, name=req.name, network=req.network,
                variant=req.variant, annual_fee_inr=req.annual_fee_inr,
                reward_system=req.reward_system, verification_status="user_defined",
                monthly_cap_inr=req.monthly_cap_inr, exclusions=req.exclusions, rules=rules)
    CUSTOM_CARDS[cid] = card
    return card_to_dict(card)


@app.patch("/users/custom-cards/{card_id}")
def edit_custom_card(card_id: str, req: CustomCardRequest):
    if card_id not in CUSTOM_CARDS:
        raise HTTPException(404, "Custom card not found")
    c = CUSTOM_CARDS[card_id]
    c.name, c.issuer, c.annual_fee_inr = req.name, req.issuer, req.annual_fee_inr
    c.monthly_cap_inr, c.exclusions = req.monthly_cap_inr, req.exclusions
    return card_to_dict(c)


class UsageRequest(BaseModel):
    monthly_reward_used_inr: float
    usage_known: bool = True
    cap_usage_by_group: dict = Field(default_factory=dict)
    base_cashback_earned_inr: Optional[float] = None
    base_cashback_known: Optional[bool] = None


@app.post("/users/cards/{user_card_id}/usage")
def update_usage(user_card_id: str, req: UsageRequest):
    if user_card_id not in USER_CARDS:
        raise HTTPException(404, "User card not found")
    uc = USER_CARDS[user_card_id]
    uc.monthly_reward_used_inr = req.monthly_reward_used_inr
    uc.usage_known = req.usage_known
    if req.cap_usage_by_group:
        uc.cap_usage_by_group = req.cap_usage_by_group
    if req.base_cashback_earned_inr is not None:
        uc.base_cashback_earned_inr = req.base_cashback_earned_inr
    if req.base_cashback_known is not None:
        uc.base_cashback_known = req.base_cashback_known
    return {"id": uc.id, "monthly_reward_used_inr": uc.monthly_reward_used_inr,
            "usage_known": uc.usage_known,
            "cap_usage_by_group": uc.cap_usage_by_group,
            "base_cashback_earned_inr": uc.base_cashback_earned_inr,
            "base_cashback_known": uc.base_cashback_known}


class RecommendRequest(BaseModel):
    merchant: str
    category: str = "general"
    amount_inr: float
    channel: str = "any"
    mcc_known: bool = False
    user_card_ids: Optional[list[str]] = None  # None = all my cards


@app.post("/recommendations")
def create_recommendation(req: RecommendRequest):
    ucs = [uc for uc in USER_CARDS.values()
           if req.user_card_ids is None or uc.id in req.user_card_ids]
    if not ucs:
        raise HTTPException(400, "Add at least one card to My Cards first")
    out = recommend(ucs, req.merchant, req.category, req.amount_inr,
                    req.channel, req.mcc_known)
    record = {
        "merchant": req.merchant, "category": req.category,
        "amount_inr": req.amount_inr,
        "best": result_to_dict(out["best"]) if out["best"] else None,
        "alternatives": [result_to_dict(r) for r in out["alternatives"]],
        "excluded": [result_to_dict(r) for r in out["excluded"]],
    }
    RECOMMENDATION_HISTORY.append(record)
    return record


@app.get("/users/recommendations")
def recommendation_history():
    return RECOMMENDATION_HISTORY


@app.get("/users/rewards")
def rewards_dashboard():
    # MVP: totals from recommendation history + current cap usage.
    total = sum((r["best"]["reward_value_inr"] if r["best"] else 0)
                for r in RECOMMENDATION_HISTORY)
    return {
        "total_estimated_reward_value_inr": round(total, 2),
        "recommendations_count": len(RECOMMENDATION_HISTORY),
        "cards": [{"card_name": uc.card.name,
                   "monthly_reward_used_inr": uc.monthly_reward_used_inr,
                   "usage_known": uc.usage_known,
                   "monthly_cap_inr": uc.card.monthly_cap_inr,
                   "remaining_cap_inr": (uc.card.monthly_cap_inr - uc.monthly_reward_used_inr)
                   if uc.card.monthly_cap_inr is not None and uc.usage_known else None}
                  for uc in USER_CARDS.values()],
    }
