"""Postgres store — v3 (Supabase-ready).

Usage:
  # 1. In Supabase: create a free project, open its SQL editor,
  #    paste db/schema.sql, then db/schema_v2.sql, then
  #    db/schema_v3.sql, and Run each in order.
  # 2. Copy the Transaction pooler connection string from
  #    Project Settings -> Database, set it as DATABASE_URL
  #    (never commit it to git).
  # 3. Run:  python -m app.db --load-seed
  #    Re-running is safe: rules for each card are deleted and
  #    re-inserted, exclusions/sources use ON CONFLICT DO NOTHING
  #    (requires schema_v3 indexes for the latter two).
  # 4. Check without loading:  python -m app.db --check
  # 5. Start the API with the same DATABASE_URL and it loads
  #    the catalogue from Postgres instead of the in-memory
  #    seed. Without DATABASE_URL it falls back to the seed.

No card numbers, CVV or OTP are ever stored here.
"""
from __future__ import annotations

import os
import sys

from .postgres_store import check_connection, normalise_database_url

DATABASE_URL = os.environ.get("DATABASE_URL", "")


def load_seed() -> None:
    if not DATABASE_URL:
        print("DATABASE_URL is not set. Create a free Supabase "
              "Postgres, run db/schema.sql + schema_v2.sql + "
              "schema_v3.sql, then set DATABASE_URL and re-run.")
        return
    try:
        import psycopg
    except ImportError:
        print("pip install 'psycopg[binary]' first.")
        return
    from .seed import seed_cards

    cards = seed_cards()
    url = normalise_database_url(DATABASE_URL)
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            for c in cards:
                cur.execute(
                    "insert into issuers (id, name) values (%s, %s) "
                    "on conflict (id) do nothing",
                    (c.issuer, c.issuer),
                )
                cur.execute(
                    "insert into cards (id, issuer_id, name, network, "
                    "annual_fee_inr, fee_waiver_spend_inr, status, "
                    "verification_status, reward_system, "
                    "aggregate_cap_inr, posting_basis, effective_from, "
                    "source_url, source_urls) "
                    "values (%s,%s,%s,%s,%s,%s,'pending_review',"
                    "'pending_review',%s,%s,%s,%s,%s,%s) "
                    "on conflict (id) do update set "
                    "annual_fee_inr = excluded.annual_fee_inr, "
                    "fee_waiver_spend_inr = excluded.fee_waiver_spend_inr, "
                    "reward_system = excluded.reward_system, "
                    "aggregate_cap_inr = excluded.aggregate_cap_inr, "
                    "posting_basis = excluded.posting_basis, "
                    "effective_from = excluded.effective_from, "
                    "source_url = excluded.source_url, "
                    "source_urls = excluded.source_urls",
                    (c.id, c.issuer, c.name, c.network, c.annual_fee_inr,
                     c.fee_waiver_spend_inr, c.reward_system,
                     c.aggregate_cap_inr, c.posting_basis,
                     c.effective_from, c.source_url, c.source_urls),
                )
                # Replace, don't duplicate, on re-run.
                cur.execute("delete from reward_rules where card_id = %s", (c.id,))
                cur.execute("delete from exclusions where card_id = %s", (c.id,))
                for r in c.rules:
                    cur.execute(
                        "insert into reward_rules (card_id, category, "
                        "merchant, channel, cashback_rate_pct, "
                        "points_per_block, block_amount_inr, "
                        "point_value_inr, min_transaction_inr, "
                        "min_order_inr, per_transaction_cap_inr, "
                        "cap_group, cap_scope, cap_value_inr, "
                        "cap_multiplier_of_base, requires_membership, "
                        "redemption_type, coupon_required, "
                        "transaction_fee_pct, "
                        "transaction_fee_min_amount_inr) "
                        "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (c.id, r.category, r.merchant, r.channel,
                         r.cashback_rate_pct, r.points_per_block,
                         r.block_amount_inr, r.point_value_inr,
                         r.min_transaction_inr, r.min_order_inr,
                         r.per_transaction_cap_inr,
                         r.cap_group, r.cap_scope, r.cap_value_inr,
                         r.cap_multiplier_of_base, r.requires_membership,
                         r.redemption_type, r.coupon_required,
                         r.transaction_fee_pct,
                         r.transaction_fee_min_amount_inr),
                    )
                for ex in c.exclusions:
                    cur.execute(
                        "insert into exclusions (card_id, category) "
                        "values (%s,%s) on conflict do nothing",
                        (c.id, ex),
                    )
                for src in (c.source_urls or ([c.source_url] if c.source_url else [])):
                    # document_type left blank: source_urls mix
                    # product pages and blogs, and mislabelling
                    # one as the other would be worse than blank.
                    cur.execute(
                        "insert into card_sources (card_id, source_url) "
                        "values (%s,%s) "
                        "on conflict (card_id, source_url) do nothing",
                        (c.id, src),
                    )
        conn.commit()
    print(f"Loaded {len(cards)} seed cards (pending_review) into Postgres.")


if __name__ == "__main__":
    if "--load-seed" in sys.argv:
        load_seed()
    elif "--check" in sys.argv:
        if not DATABASE_URL:
            print("DATABASE_URL is not set.")
        else:
            print(check_connection(DATABASE_URL))
    else:
        print("Usage: python -m app.db --load-seed | --check")
