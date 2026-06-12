# CardWise India - MVP (PRD v2.0, 3 Nov 2026)

**Add your cards once. Know which card to use before every purchase.**

This is a working MVP scaffold for PRD Phases 2-4, built to the PRD's
non-negotiables:

- Deterministic rewards math in code, never an LLM (`backend/app/engine.py`)
- Caps, exclusions, points-per-block rounding, and unknown-cap = estimated
- Excluded cards are shown, never hidden
- Unverified rules are labelled `pending_review` / `user_defined`, never verified
- No full card number, CVV or OTP is ever collected

## What is built

- `backend/` - FastAPI + Pydantic API (PRD section 14, MVP subset)
  - `GET /cards`, `GET /cards/search`, `GET /cards/{id}`
  - `POST /users/cards`, `DELETE /users/cards/{id}`
  - `POST /users/custom-cards`, `PATCH /users/custom-cards/{id}`
  - `POST /recommendations`, `GET /users/recommendations`
  - `POST /users/cards/{id}/usage`, `GET /users/rewards`
  - Engine tests in `backend/tests/test_engine.py` - PRD 6.4 cap example,
    points floor, unknown-cap estimate, excluded-card visibility,
    and the PRD 6.3 Rs 5,000 Amazon example.
- `frontend/` - Next.js 14 + TypeScript app: My Cards, Add a Card,
  Find My Best Card with best / alternatives / excluded.
- `db/schema.sql` - PostgreSQL tables from PRD section 13.
  The demo API currently uses in-memory storage; wire this schema
  in before production, and add real email auth (the API currently
  uses a single demo user - see the TODO in `backend/app/main.py`).

## Run the backend

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/test_engine.py -v
.venv/bin/uvicorn app.main:app --reload --port 8000
```

## Run the frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
# open http://localhost:3000
```

Try: add SBI Cashback, Amazon Pay ICICI, HDFC Millennia and Axis Airtel,
then Find My Best Card for Amazon, online_shopping, Rs 5,000.

## Cost: almost $0

- Database: local Postgres via `docker-compose.yml` ($0), or
  Supabase Free / Neon Free hosted Postgres ($0 tier) by setting
  `DATABASE_URL`. No paid database tier is required for the MVP.
- Extraction: local `requests` + BeautifulSoup + PyMuPDF ($0).
  Firecrawl is cloned self-hosted in `tools/firecrawl/` — do not
  use Firecrawl Cloud (paid) without explicit approval.
- Frontend hosting: Vercel Free tier. Analytics: self-hosted
  or none in the MVP, not a paid plan.

## Data sources (v2)

See `data/source_registry.md`. In short: the HuggingFace
dataset (280 cards, Aug 2026, CC BY 4.0) and CardAdvisor.in
are cross-checks only — they give fee and rate ranges, not
caps, exclusions or posting rules. What CardWise calculates
must come from issuer documents: product page + cardholder
T&C + redemption terms, per card, per issuer. SBI, ICICI
Amazon Pay and Axis Airtel are now modelled from their
official FAQ / T&C (see registry), but remain
`pending_review` until the full T&C and redemption documents
are parsed end to end.

## CRITICAL: data is sample only

All 8 seed cards are `pending_review` with sample rules in
`backend/app/seed.py`. Phase 1 work still to do before launch:

1. Verify each rule against the official issuer product page / terms
2. Add `source_url`, `last_verified_date`, effective dates
3. Record the change in `card_rule_versions`
4. Only then flip `verification_status` to `verified`

Do not publish the seed rules as verified, and do not use card
quantity as a quality metric - PRD section 16 is explicit on this.

## Next decisions needed from you

1. Real card verification first, or demo first? (recommended: verify
   the 15-20 Phase 1 cards before any public use)
2. Auth + database hosting: Supabase (per PRD) or self-hosted Postgres?
3. Deploy target: Vercel for frontend + where for FastAPI?
4. Do you want guest mode (PRD 6.1) in the next build, or login-only?
