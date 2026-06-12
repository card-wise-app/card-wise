-- CardWise schema v2 — additions for official-doc rule types.
-- Apply after db/schema.sql. All new columns are nullable so
-- v1 rows keep working. See data/source_registry.md for why
-- each field exists (SBI / ICICI / Axis examples).

alter table cards add column if not exists fee_waiver_spend_inr numeric;
alter table cards add column if not exists aggregate_cap_inr numeric;
alter table cards add column if not exists aggregate_cap_scope text default 'statement_cycle';
alter table cards add column if not exists posting_basis text default 'posting_date';
alter table cards add column if not exists effective_from date;
alter table cards add column if not exists source_urls text[];

alter table reward_rules add column if not exists cap_group text;
alter table reward_rules add column if not exists cap_scope text default 'statement_cycle';
alter table reward_rules add column if not exists cap_value_inr numeric;
alter table reward_rules add column if not exists cap_multiplier_of_base numeric;
alter table reward_rules add column if not exists requires_membership text;
alter table reward_rules add column if not exists redemption_type text default 'statement_credit';
alter table reward_rules add column if not exists coupon_required boolean default false;
alter table reward_rules add column if not exists min_order_inr numeric default 0;
alter table reward_rules add column if not exists transaction_fee_pct numeric;
alter table reward_rules add column if not exists transaction_fee_min_amount_inr numeric default 0;

-- Per-group cap usage per user card per cycle (SBI online/offline,
-- Axis Airtel accelerated groups). One row per user_card + group + cycle.
create table if not exists user_card_cap_usage (
  id uuid primary key default gen_random_uuid(),
  user_card_id uuid references user_cards(id),
  cap_group text not null,
  cycle_start date not null,
  reward_earned_inr numeric default 0,
  unique(user_card_id, cap_group, cycle_start)
);

-- Base cashback earned per cycle (Axis Airtel base-linked caps).
create table if not exists user_card_base_cashback (
  id uuid primary key default gen_random_uuid(),
  user_card_id uuid references user_cards(id),
  cycle_start date not null,
  base_cashback_inr numeric default 0,
  unique(user_card_id, cycle_start)
);

-- Memberships that change a rule (e.g. Amazon Prime for ICICI).
create table if not exists user_memberships (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id),
  membership_key text not null, -- amazon_prime, etc.
  is_active boolean default true,
  unique(user_id, membership_key)
);

-- Source documents: exactly the three doc types per card.
create table if not exists card_documents (
  id uuid primary key default gen_random_uuid(),
  card_id text references cards(id),
  doc_type text not null check (doc_type in ('product_page', 'cardholder_tnc', 'redemption_terms')),
  source_url text not null,
  local_path text,
  fetched_at timestamptz,
  unique(card_id, doc_type, source_url)
);
