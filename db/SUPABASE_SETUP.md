# Supabase Postgres setup — CardWise (free tier, ~$0)

> Live-test note, 3 Nov 2026: the full swap path (schema.sql +
> schema_v2.sql + schema_v3.sql, `--load-seed` twice, API reading
> the catalogue from Postgres, Pinnacle ₹10,000 online = 250 points
> / ₹187.50) was verified against a local PostgreSQL 16.2
> (pgserver, non-root user — Postgres refuses to run as root).
> Result: 12 cards, 58 rules, 47 exclusions, 10 issuers, reload
> idempotent, API fallback to seed verified with no / bad
> DATABASE_URL. That proves the code and SQL, not a Supabase
> project — a Supabase project still needs your sign-in (Step 1).
> One live-test bug was fixed in schema_v3: a unique index on
> reward_rules (card, category, merchant, channel) broke ICICI,
> which legitimately has Prime 5% and non-Prime 3% rules with
> those same values. Rules idempotency is now DELETE + re-insert.

## What this does and does not do

- Moves the **catalogue** (cards, reward rules, exclusions, sources)
  from the in-memory seed into Postgres. The API reads it from
  Postgres at startup when `DATABASE_URL` is set.
- Does **not** yet move per-user cards or recommendation history
  into Postgres — those stay in memory until real auth exists.
  That is deliberate: user rows without auth would be orphaned.
- Does **not** create a Supabase project for you. Creating a
  project needs your Supabase login (GitHub / email). No password
  or key is stored in this repo.

## Step 1 — Create the free project (about 5 minutes)

1. Go to https://supabase.com/dashboard and sign in (or create
   a free account).
2. New project: pick any name (e.g. `cardwise-india`), a database
   password (save it in your password manager, not in git),
   and the closest region (for India users, Mumbai / ap-south-1
   if offered, otherwise Singapore).
3. Wait for the project to finish provisioning (usually 1–2 min).
4. Free tier limits to know: 500 MB database, 2 GB bandwidth,
   and the project pauses after 7 days of inactivity — it
   restores on next visit. That is fine for an MVP; it is not
   a production SLA.

## Step 2 — Run the schema, in this order

In the Supabase dashboard: SQL Editor -> New query, paste one
file, Run, then repeat for the next. Order matters:

1. `db/schema.sql`
2. `db/schema_v2.sql`
3. `db/schema_v3.sql` (new: fractional points 2.5/1.5, plus
   `reward_system` / `source_url` columns and idempotency indexes)

If a file says "already exists" on a re-run, that is expected —
every statement is `IF NOT EXISTS` / idempotent.

Do NOT turn on Row Level Security for these tables yet. The API
connects as the Postgres user (which bypasses RLS), and turning
RLS on before auth exists would only confuse the next step.

## Step 3 — Get the connection string

Project Settings -> Database -> Connection string -> **Transaction
pooler** (port 6543). It looks like:

```
postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

Replace `[YOUR-PASSWORD]` with the database password from Step 1.
Use the pooler (6543) for the API, not the direct 5432 URL —
Supabase counts direct connections and the pooler survives
hosted-API restarts better. Append `?sslmode=require` if it is
not already there; the code adds it automatically for non-local
hosts, but being explicit in the URL is clearer.

## Step 4 — Load the seed catalogue

From `backend/`:

```bash
pip install -r requirements.txt   # includes psycopg[binary]
export DATABASE_URL='postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@...:6543/postgres?sslmode=require'
python -m app.db --check
python -m app.db --load-seed
```

Expected `--check` output: a Postgres version and counts,
with `cards: 0` before loading. Expected `--load-seed` output:

```
Loaded 12 seed cards (pending_review) into Postgres.
```

Re-running `--load-seed` is safe: rules and exclusions for each
card are replaced, not duplicated. All 12 cards stay
`pending_review` — loading into Postgres does not verify them.

## Step 5 — Run the API against Postgres

With the same `DATABASE_URL` set:

```bash
uvicorn app.main:app --reload --port 8000
```

Startup should print:

```
Catalogue loaded from Postgres: 12 cards.
```

Then `GET http://127.0.0.1:8000/cards` should return 12 cards,
including IndusInd Pinnacle World. If Postgres is unreachable,
the API prints the error and falls back to the seed cards —
it never serves an empty catalogue silently. Check the startup
log to know which source is actually in use.

## Step 6 — Verify one calculation end to end

```bash
# Add Pinnacle to My Cards, then recommend for Rs 10,000 online:
curl -X POST http://127.0.0.1:8000/users/cards \
  -H 'Content-Type: application/json' \
  -d '{"card_id": "indusind-pinnacle", "usage_known": true}'
# (copy the returned id, then:)
curl -X POST http://127.0.0.1:8000/recommendations \
  -H 'Content-Type: application/json' \
  -d '{"merchant": "Amazon", "category": "online_shopping", "amount_inr": 10000, "channel": "online", "mcc_known": true}'
```

Expected: 250 points, ₹187.50. If you get a different number,
the Postgres rules differ from the seed — diff them with
`python -m app.db --load-seed` again, then re-check.

## Troubleshooting

- `password authentication failed`: the pooler username is
  `postgres.[PROJECT-REF]`, not just `postgres`. Copy the full
  string from Supabase, don't type it.
- `SSL error` / `sslmode`: use `?sslmode=require` on the pooler URL.
- `relation "cards" does not exist`: Step 2 was skipped or ran
  in the wrong project. Run the three schema files again.
- `points_per_block` errors on old data: you ran `schema.sql`
  but not `schema_v3.sql` — the int column cannot hold 2.5.
- Project paused: open the Supabase dashboard, restore it, and
  restart the API. Data is kept; only the connection was paused.

## Security checklist

- `DATABASE_URL` lives in an environment variable / host secret
  only. It is not in git, not in `.env` (which is gitignored
  via `.env.example`), and never pasted into chat.
- The API never uses the Supabase anon key. Direct Postgres
  access is server-side only; the frontend talks to the API,
  not to Supabase directly.
- No card numbers, CVV or OTP are stored in any table.
