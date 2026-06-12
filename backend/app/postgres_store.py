"""Load the CardWise catalogue from Postgres (Supabase / Neon / local).

This is the read side of the Postgres swap. It is deliberately
boring: one SELECT per table, Decimal -> float conversion, and
no fallback guessing. If DATABASE_URL is not set, or the tables
are empty, the caller falls back to the in-memory seed — it
never invents a card.

Supabase connection notes:
- Use the Transaction pooler URL (port 6543) for the API, with
  sslmode=require appended if it is not already there.
- The direct URL (port 5432) also works; the pooler is preferred
  for a hosted API because Supabase counts direct connections.
- Never put this URL in git, in MEMORY.md, or in a chat reply.
  Set it as an environment variable (or a host secret) only.
"""
from __future__ import annotations

import os
from decimal import Decimal

from .engine import Card, RewardRule


def _f(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    return float(v)


def normalise_database_url(url: str) -> str:
    """Append sslmode=require for hosted Postgres unless present.

    Local Postgres (localhost / 127.0.0.1) does not need SSL and
    may reject it, so leave local URLs untouched.
    """
    if not url:
        return url
    low = url.lower()
    if "sslmode=" in low:
        return url
    if "localhost" in low or "127.0.0.1" in low:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}sslmode=require"


def load_cards_from_postgres(database_url: str) -> list[Card]:
    import psycopg

    url = normalise_database_url(database_url)
    cards: dict[str, Card] = {}
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select id, issuer_id, name, network, variant, "
                "annual_fee_inr, fee_waiver_spend_inr, reward_system, "
                "verification_status, aggregate_cap_inr, "
                "aggregate_cap_scope, posting_basis, effective_from, "
                "source_url, source_urls from cards order by id"
            )
            for row in cur.fetchall():
                (cid, issuer_id, name, network, variant, annual_fee,
                 waiver, reward_system, verification, agg_cap,
                 agg_scope, posting, effective_from, source_url,
                 source_urls) = row
                cards[cid] = Card(
                    id=cid, issuer=issuer_id or "", name=name,
                    network=network or "", variant=variant or "",
                    annual_fee_inr=_f(annual_fee) or 0,
                    fee_waiver_spend_inr=_f(waiver),
                    reward_system=reward_system or "cashback",
                    verification_status=verification or "pending_review",
                    source_url=source_url,
                    source_urls=list(source_urls or []),
                    effective_from=str(effective_from) if effective_from else None,
                    aggregate_cap_inr=_f(agg_cap),
                    aggregate_cap_scope=agg_scope or "statement_cycle",
                    posting_basis=posting or "posting_date",
                    exclusions=[], rules=[],
                )
            if not cards:
                return []
            cur.execute(
                "select card_id, category, merchant, channel, "
                "cashback_rate_pct, points_per_block, block_amount_inr, "
                "point_value_inr, min_transaction_inr, min_order_inr, "
                "per_transaction_cap_inr, cap_group, cap_scope, "
                "cap_value_inr, cap_multiplier_of_base, "
                "requires_membership, redemption_type, coupon_required, "
                "transaction_fee_pct, transaction_fee_min_amount_inr "
                "from reward_rules order by card_id, category"
            )
            for row in cur.fetchall():
                (cid, category, merchant, channel, cb, ppb, block, pv,
                 min_tx, min_order, per_tx_cap, cap_group, cap_scope,
                 cap_value, cap_mult, membership, redemption, coupon,
                 fee_pct, fee_min) = row
                card = cards.get(cid)
                if card is None:
                    continue
                card.rules.append(RewardRule(
                    category=category or "general", merchant=merchant,
                    channel=channel or "any",
                    cashback_rate_pct=_f(cb), points_per_block=_f(ppb),
                    block_amount_inr=_f(block),
                    point_value_inr=_f(pv) if pv is not None else 0.25,
                    min_transaction_inr=_f(min_tx) or 0,
                    min_order_inr=_f(min_order) or 0,
                    per_transaction_cap_inr=_f(per_tx_cap),
                    cap_group=cap_group, cap_scope=cap_scope or "statement_cycle",
                    cap_value_inr=_f(cap_value),
                    cap_multiplier_of_base=_f(cap_mult),
                    requires_membership=membership,
                    redemption_type=redemption or "statement_credit",
                    coupon_required=bool(coupon),
                    transaction_fee_pct=_f(fee_pct),
                    transaction_fee_min_amount_inr=_f(fee_min) or 0,
                ))
            cur.execute("select card_id, category from exclusions order by card_id")
            for cid, category in cur.fetchall():
                card = cards.get(cid)
                if card is not None and category not in card.exclusions:
                    card.exclusions.append(category)
    return list(cards.values())


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", "").strip()


def check_connection(database_url: str) -> dict:
    """Return a safe summary: never returns the URL or password."""
    import psycopg

    url = normalise_database_url(database_url)
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("select version()")
            version = cur.fetchone()[0]
            counts = {}
            for table in ("cards", "reward_rules", "exclusions", "issuers"):
                try:
                    cur.execute(f"select count(*) from {table}")
                    counts[table] = cur.fetchone()[0]
                except Exception:
                    conn.rollback()
                    counts[table] = "missing"
    return {"postgres_version": version, "counts": counts}
