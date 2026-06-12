-- CardWise MVP schema - PRD section 13 (PostgreSQL / Supabase)
-- Public card rules are kept separate from per-user usage.
-- Never overwrite a rule without inserting a row in card_rule_versions.

create table if not exists issuers (
  id text primary key, name text not null, country text default 'IN'
);
create table if not exists cards (
  id text primary key, issuer_id text references issuers(id),
  name text not null, network text, variant text,
  joining_fee_inr numeric, annual_fee_inr numeric,
  fee_waiver_conditions text, reward_currency text,
  status text default 'pending_review',
  verification_status text default 'pending_review',
  last_verified_date date
);
create table if not exists reward_rules (
  id uuid primary key default gen_random_uuid(),
  card_id text references cards(id), category text, merchant text,
  channel text default 'any', cashback_rate_pct numeric,
  points_per_block int, block_amount_inr numeric, point_value_inr numeric,
  min_transaction_inr numeric default 0,
  per_transaction_cap_inr numeric, effective_from date, effective_to date
);
create table if not exists reward_caps (
  id uuid primary key default gen_random_uuid(),
  card_id text references cards(id), scope text, -- monthly | quarterly | annual | statement_cycle
  cap_value_inr numeric, applies_to text
);
create table if not exists exclusions (
  id uuid primary key default gen_random_uuid(),
  card_id text references cards(id), category text, reason text
);
create table if not exists redemption_options (
  id uuid primary key default gen_random_uuid(),
  card_id text references cards(id), method text, point_value_inr numeric,
  min_redemption int, fee_inr numeric
);
create table if not exists merchants (id text primary key, name text not null, category text);
create table if not exists merchant_aliases (id uuid primary key default gen_random_uuid(), merchant_id text references merchants(id), alias text);
create table if not exists mcc_codes (code text primary key, description text);
create table if not exists card_sources (
  id uuid primary key default gen_random_uuid(),
  card_id text references cards(id), source_url text, document_type text, fetched_at timestamptz
);
create table if not exists card_rule_versions (
  id uuid primary key default gen_random_uuid(),
  card_id text references cards(id), rule_snapshot jsonb, changed_at timestamptz default now(), changed_by text
);
create table if not exists users (id uuid primary key default gen_random_uuid(), email text unique not null, country text default 'IN', currency text default 'INR');
create table if not exists user_cards (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id), card_id text references cards(id),
  is_custom boolean default false, statement_cycle_day int default 1,
  monthly_reward_used_inr numeric default 0, usage_known boolean default false
);
create table if not exists custom_cards (id text primary key, user_id uuid references users(id), name text, issuer text, reward_system text);
create table if not exists user_card_usage (
  id uuid primary key default gen_random_uuid(),
  user_card_id uuid references user_cards(id), cycle_start date, reward_earned_inr numeric
);
create table if not exists transactions (
  id uuid primary key default gen_random_uuid(),
  user_card_id uuid references user_cards(id), merchant text, category text,
  amount_inr numeric, channel text, occurred_at timestamptz
);
create table if not exists recommendations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id), merchant text, category text, amount_inr numeric,
  best_card_id text, best_value_inr numeric, confidence text, created_at timestamptz default now()
);
