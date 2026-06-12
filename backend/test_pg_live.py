"""Live Postgres test for the Supabase swap (local pgserver, PG 16.2).

Run as the non-root `cardwise` user, because Postgres refuses
to run as root:
  su cardwise -c "/home/hatch/workspace/cardwise-india/backend/.venv/bin/python /home/hatch/workspace/cardwise-india/backend/test_pg_live.py"

This is a TEST script only, not part of the app. It:
1. starts/reattaches a pgserver Postgres in /tmp/cardwise-pg-test
2. runs db/schema.sql, schema_v2.sql, schema_v3.sql
3. runs app.db --check and --load-seed twice (idempotency)
4. imports the FastAPI app with DATABASE_URL set and checks
   /cards returns 12 cards from Postgres, and a Pinnacle
   recommendation returns 250 points / Rs 187.50 for Rs 10,000 online
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pgserver

srv = pgserver.get_server("/tmp/cardwise-pg-test")
uri = srv.get_uri()
print("PG URI:", uri)
os.environ["DATABASE_URL"] = uri

import psycopg

base = Path(__file__).resolve().parents[1]
with psycopg.connect(uri) as conn:
    with conn.cursor() as cur:
        for name in ("schema.sql", "schema_v2.sql", "schema_v3.sql"):
            sql = (base / "db" / name).read_text()
            cur.execute(sql)
            print("applied", name)
    conn.commit()

from app.db import load_seed
from app.postgres_store import check_connection

print("check:", check_connection(uri))
load_seed()
print("check after load:", check_connection(uri))

with psycopg.connect(uri) as conn:
    with conn.cursor() as cur:
        cur.execute("select count(*) from cards")
        cards_n = cur.fetchone()[0]
        cur.execute("select count(*) from reward_rules")
        rules_n = cur.fetchone()[0]
        cur.execute("select count(*) from exclusions")
        excl_n = cur.fetchone()[0]
print(f"cards={cards_n} rules={rules_n} exclusions={excl_n}")
assert cards_n == 12, cards_n

# Idempotency: second load must not duplicate rules.
load_seed()
with psycopg.connect(uri) as conn:
    with conn.cursor() as cur:
        cur.execute("select count(*) from reward_rules")
        rules_n2 = cur.fetchone()[0]
print(f"rules after 2nd load={rules_n2}")
assert rules_n2 == rules_n, (rules_n, rules_n2)

# API from Postgres
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
cards = c.get("/cards").json()
print("API /cards:", len(cards), [x["name"] for x in cards])
assert len(cards) == 12
pinnacle = next(x for x in cards if x["id"] == "indusind-pinnacle")
print("Pinnacle rules from PG:", pinnacle["rules"])
assert any(r["points_per_block"] == 2.5 for r in pinnacle["rules"]), pinnacle["rules"]

# Recommendation via API: add Pinnacle, then Rs 10,000 Amazon online
uc = c.post("/users/cards", json={"card_id": "indusind-pinnacle", "usage_known": True}).json()
print("user card:", uc["id"])
rec = c.post("/recommendations", json={
    "merchant": "Amazon", "category": "online_shopping", "amount_inr": 10000,
    "channel": "online", "mcc_known": True, "user_card_ids": [uc["id"]],
}).json()
print("recommendation best:", rec["best"])
assert rec["best"]["points_earned"] == 250, rec["best"]
assert rec["best"]["reward_value_inr"] == 187.5, rec["best"]
print("ALL LIVE PG CHECKS PASSED")
