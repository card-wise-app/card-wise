-- CardWise schema v3 — Supabase-ready fixes. Apply after
-- db/schema.sql and db/schema_v2.sql, in the Supabase SQL editor
-- (or with psql). All statements are idempotent (IF NOT EXISTS /
-- OR REPLACE style where Postgres allows it).
--
-- 1. Fractional points: IndusInd Pinnacle earns 2.5 / 1.5 points
--    per Rs 100. The v1 column was int, which cannot hold 2.5.
--    (Postgres: ALTER COLUMN ... TYPE numeric USING ... works
--    even when rows exist, because int -> numeric is safe.)
alter table reward_rules
  alter column points_per_block type numeric using points_per_block::numeric;

-- 2. Card fields the engine actually uses but v1 did not store.
alter table cards add column if not exists reward_system text default 'cashback';
alter table cards add column if not exists source_url text;

-- 3. Make re-running the seed loader idempotent instead of
--    duplicating exclusions/sources. These unique indexes let
--    the loader use ON CONFLICT ... DO NOTHING safely.
--    NOTE (live-test fix, 3 Nov 2026): do NOT put a unique index
--    on reward_rules (card_id, category, merchant, channel).
--    A card legitimately has several rules with those same
--    values that differ only by membership (ICICI Amazon Pay:
--    Prime 5% vs non-Prime 3% on Amazon) or by cap group.
--    Rules idempotency is instead the loader's DELETE of a
--    card's old rules before inserting its new ones.
--    Drop the index if an earlier v3 run created it.
drop index if exists reward_rules_card_category_merchant_idx;
create unique index if not exists exclusions_card_category_idx
  on exclusions (card_id, category);
create unique index if not exists card_sources_card_url_idx
  on card_sources (card_id, source_url);

-- 4. Supabase note: tables created in the SQL editor are owned
--    by postgres, which bypasses Row Level Security. Do NOT turn
--    RLS on for these tables until real user auth exists, or the
--    API's direct Postgres connection will get empty results.
--    The API never uses the anon key; it uses the Postgres
--    connection string (pooler, sslmode=require) only.
