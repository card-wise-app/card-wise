"""Generate db/seed.sql from app.seed.seed_cards(), mirroring app.db.load_seed() exactly.

Run:  python generate_seed_sql.py   (from backend/)
Output: ../db/seed.sql
Idempotent: issuers/cards use ON CONFLICT upsert, rules/exclusions are
deleted per card before re-insert, card_sources use ON CONFLICT DO NOTHING.
No card numbers, CVV or OTP are in the seed.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app.seed import seed_cards  # noqa: E402


def lit(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def arr_str(values):
    if not values:
        return "NULL"
    return "ARRAY[" + ",".join(lit(v) for v in values) + "]"


def main():
    cards = seed_cards()
    out = []
    out.append("-- CardWise seed catalogue — generated from backend/app/seed.py")
    out.append("-- DO NOT hand-edit: regenerate with backend/generate_seed_sql.py")
    out.append("-- All cards are pending_review, NOT issuer verified.")
    out.append("-- Idempotent: re-running replaces each card's rules/exclusions.")
    out.append("begin;")
    n_rules = n_ex = n_src = 0
    for c in cards:
        out.append(f"insert into issuers (id, name) values ({lit(c.issuer)}, {lit(c.issuer)}) on conflict (id) do nothing;")
        out.append(
            "insert into cards (id, issuer_id, name, network, annual_fee_inr, fee_waiver_spend_inr, status, "
            "verification_status, reward_system, aggregate_cap_inr, posting_basis, effective_from, source_url, source_urls) "
            f"values ({lit(c.id)}, {lit(c.issuer)}, {lit(c.name)}, {lit(c.network)}, {lit(c.annual_fee_inr)}, "
            f"{lit(c.fee_waiver_spend_inr)}, 'pending_review', 'pending_review', {lit(c.reward_system)}, "
            f"{lit(c.aggregate_cap_inr)}, {lit(c.posting_basis)}, {lit(c.effective_from)}, {lit(c.source_url)}, {arr_str(c.source_urls)}) "
            "on conflict (id) do update set annual_fee_inr = excluded.annual_fee_inr, "
            "fee_waiver_spend_inr = excluded.fee_waiver_spend_inr, reward_system = excluded.reward_system, "
            "aggregate_cap_inr = excluded.aggregate_cap_inr, posting_basis = excluded.posting_basis, "
            "effective_from = excluded.effective_from, source_url = excluded.source_url, source_urls = excluded.source_urls;"
        )
        out.append(f"delete from reward_rules where card_id = {lit(c.id)};")
        out.append(f"delete from exclusions where card_id = {lit(c.id)};")
        for r in c.rules:
            n_rules += 1
            out.append(
                "insert into reward_rules (card_id, category, merchant, channel, cashback_rate_pct, "
                "points_per_block, block_amount_inr, point_value_inr, min_transaction_inr, min_order_inr, "
                "per_transaction_cap_inr, cap_group, cap_scope, cap_value_inr, cap_multiplier_of_base, "
                "requires_membership, redemption_type, coupon_required, transaction_fee_pct, "
                "transaction_fee_min_amount_inr) "
                f"values ({lit(c.id)}, {lit(r.category)}, {lit(r.merchant)}, {lit(r.channel)}, "
                f"{lit(r.cashback_rate_pct)}, {lit(r.points_per_block)}, {lit(r.block_amount_inr)}, "
                f"{lit(r.point_value_inr)}, {lit(r.min_transaction_inr)}, {lit(r.min_order_inr)}, "
                f"{lit(r.per_transaction_cap_inr)}, {lit(r.cap_group)}, {lit(r.cap_scope)}, {lit(r.cap_value_inr)}, "
                f"{lit(r.cap_multiplier_of_base)}, {lit(r.requires_membership)}, {lit(r.redemption_type)}, "
                f"{lit(r.coupon_required)}, {lit(r.transaction_fee_pct)}, {lit(r.transaction_fee_min_amount_inr)});"
            )
        for ex in c.exclusions:
            n_ex += 1
            out.append(f"insert into exclusions (card_id, category) values ({lit(c.id)}, {lit(ex)}) on conflict do nothing;")
        srcs = c.source_urls or ([c.source_url] if c.source_url else [])
        for src in srcs:
            n_src += 1
            out.append(f"insert into card_sources (card_id, source_url) values ({lit(c.id)}, {lit(src)}) on conflict (card_id, source_url) do nothing;")
    out.append("commit;")
    out.append(f"-- counts: cards={len(cards)} rules={n_rules} exclusions={n_ex} card_sources={n_src}")
    dest = Path(__file__).parent.parent / "db" / "seed.sql"
    dest.write_text("\n".join(out) + "\n")
    print(f"Wrote {dest}: cards={len(cards)} rules={n_rules} exclusions={n_ex} card_sources={n_src}")


if __name__ == "__main__":
    main()
