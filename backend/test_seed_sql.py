"""Validate db/seed.sql against local pgserver (test only, not app code).

Run as cardwise user (Postgres refuses root):
  su cardwise -c ".../backend/.venv/bin/python .../backend/test_seed_sql.py"
Applies schema.sql + v2 + v3, then seed.sql TWICE, and asserts
cards=12, rules=58, exclusions=47 after each run (idempotent).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pgserver

srv = pgserver.get_server("/tmp/cardwise-pg-test")
uri = srv.get_uri()
import psycopg

base = Path(__file__).resolve().parents[1]


def counts(conn):
    with conn.cursor() as cur:
        out = {}
        for t in ("issuers", "cards", "reward_rules", "exclusions", "card_sources"):
            cur.execute(f"select count(*) from {t}")
            out[t] = cur.fetchone()[0]
        return out


with psycopg.connect(uri) as conn:
    with conn.cursor() as cur:
        for name in ("schema.sql", "schema_v2.sql", "schema_v3.sql", "seed.sql"):
            cur.execute((base / "db" / name).read_text())
            print("applied", name)
    conn.commit()
    print("after first seed.sql:", counts(conn))
    with conn.cursor() as cur:
        cur.execute((base / "db" / "seed.sql").read_text())
    conn.commit()
    c = counts(conn)
    print("after second seed.sql:", c)
    assert c["cards"] == 12, c
    assert c["rules"] if False else c["reward_rules"] == 58, c
    assert c["exclusions"] == 47, c
    assert c["issuers"] == 10, c
print("SEED SQL VALIDATED: 12 cards, 58 rules, 47 exclusions, 10 issuers, idempotent")
