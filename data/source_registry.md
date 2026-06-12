# CardWise Source Registry — v2

**Rule: marketing pages alone never determine a calculation.**
For every card, CardWise needs all three, in this order of authority:

1. **Official product page** — headline rates, fees, fee-waiver spend
2. **Cardholder terms and conditions (T&C / MITC)** — caps, exclusions,
   statement-cycle definition, posting basis, eligibility conditions
3. **Reward redemption terms** — point value, redemption method,
   minimum redemption, expiry, fees, transfer partners

If any of the three is missing, the card stays `pending_review` and
its recommendations are labelled `estimated`. A secondary source
(HuggingFace / CardAdvisor dataset, CardAdvisor.in) is a cross-check
only — it never overrides an issuer document, and it never promotes
a rule to `verified`.

## Secondary sources actually inspected, 3 Nov 2026

### Firecrawl (cloned, not paid cloud)
- Cloned: `git clone --depth 1 https://github.com/firecrawl/firecrawl.git`
- Local copy: `tools/firecrawl/` (self-hosted / open source, see its
  `SELF_HOST.md` and `docker-compose.yaml`)
- Role in CardWise: optional extraction tool for issuer PDFs/pages
  in the ingestion pipeline. Using the paid Firecrawl Cloud API is
  NOT required and is NOT the default — the default pipeline is
  local `requests` + `BeautifulSoup` + `PyMuPDF`, per PRD section 12.
  That keeps data ingestion at ~$0.

### HuggingFace: DevchandraSah/indian-credit-card-facts
- URL: https://huggingface.co/datasets/DevchandraSah/indian-credit-card-facts
- Licence: CC BY 4.0. Version inspected: 2026-08-16 (cards as of
  2026-08-15, changes to 2026-08-13, transfers to 2026-07-02).
- Local copy: `data/raw/cards.csv` (280 cards), `changes.csv`
  (1,617 events), `transfers.csv` (153 edges), `valuations.csv`
  (234 rows). Note: the CSVs start with a `# CardAdvisor …` comment
  line — the header is line 2, not line 1.
- What it actually contains: card key, name, issuer, network, tier,
  annual/joining fee, fee-waiver spend, forex markup, APR, and a
  single `rewardRateMinPct` / `rewardRateMaxPct` range per card.
  Example: SBI Cashback 1–5%, Amazon Pay ICICI 1–5%, Axis Airtel
  1–25%, HDFC Millennia 1–5%, HDFC Regalia Gold 1.25–6.25%.
- What it does NOT contain: per-category rates, per-group caps,
  exclusions, statement-cycle rules, posting basis, Prime vs
  non-Prime splits, partner caps, or transaction fees. It is
  therefore useful for catalogue breadth, fee/waiver cross-checks
  and point valuations (typical paisa per point), but it cannot
  by itself determine a Best Card calculation. Every rate range
  must be expanded from issuer docs before use.
- Issuer coverage in the file (of the 10 target issuers): SBI 38,
  Axis 34, RBL 25, AU 23, IndusInd 23, HDFC 22, IDFC 20, ICICI 17,
  Kotak 14, Amex 7. Kotak is present; the file also includes
  BOB, YES, SC, HSBC and others outside the initial 10.

### CardAdvisor.in
- URL: https://cardadvisor.in/
- What it claims: independent, no paid placements, every number
  traces to issuer MITC documents with a visible last-updated date,
  methodology at `/methodology`, valuations typically ₹0.20–₹1.00
  per point depending on redemption.
- Role in CardWise: cross-check and methodology reference only.
  Its card pages are secondary — the issuer MITC they cite is
  the primary source. Do not copy a CardAdvisor rate into
  CardWise without the underlying issuer document in
  `data/official/`.

## Target issuers (user list, 3 Nov 2026)

| Issuer | Data to extract | Status in this build |
|---|---|---|
| SBI Card | Cashback, reward points, caps, exclusions | FAQ + T&C located, see below |
| HDFC Bank | CashPoints, cashback, redemption | Registry entry only — docs still to fetch per card |
| Axis Bank | Cashback, EDGE Rewards, merchant offers | Airtel T&C located, see below |
| ICICI Bank | Amazon Pay cashback, reward points | Amazon Pay FAQ located, see below |
| IDFC FIRST | Reward structure, point values | Registry entry only |
| Kotak | Reward points, fees, exclusions | Registry entry only |
| American Express | Membership Rewards, travel points | Registry entry only |
| AU Small Finance Bank | Cashback, reward rules | Registry entry only |
| RBL Bank | Cashback and reward benefits | Registry entry only |
| IndusInd Bank | Reward programs and fees | Registry entry only |

For each issuer, the ingestion checklist per card is in
`data/ingestion_checklist.md`. Do not mark a card `verified`
until all three doc types are filed, parsed, and the extracted
rules diff cleanly against the previous version.

## FAQ-confirmed examples (partial evidence, NOT full verification)

These three are the schema-design examples the user named.
They are filed as `pending_review` with an official source URL,
because the full T&C / redemption document has not yet been
parsed end to end for every exclusion.

### 1. SBI Cashback Card — SBI Card
- Product / FAQ: https://www.sbicard.com/en/faq/cashback-sbi-card-faq.page
- T&C PDF: https://www.sbicard.com/sbi-card-en/assets/docs/pdf/ekit-tncs/cashback-tnc-ekit.pdf
- FAQ-confirmed: 5% online, 1% offline (POS). Max online
  ₹2,000 per statement cycle, max offline ₹2,000 per statement
  cycle, aggregate max ₹4,000 per statement cycle. Cashback
  accrues on posting/settlement date, NOT transaction date.
  Example in FAQ: statement date 11 July → transactions posted
  12 June–11 July count in that cycle.
- Version note: aggregate cap was ₹5,000 before 1 Apr 2026,
  ₹4,000 from 1 Apr 2026. The engine must version this, not
  overwrite it. Previous sample in v1 (single ₹5,000 monthly
  cap) was wrong and is replaced in v2.
- Exclusions still to parse in full from the T&C: fuel (no
  cashback, 1% surcharge waiver ₹500–₹3,000, max ₹100/cycle),
  plus utilities, insurance, rent, wallets, education, jewellery
  and others named in secondary summaries — do not hard-code
  the full list until the T&C text is extracted.

### 2. Amazon Pay ICICI Bank Credit Card — ICICI Bank
- FAQ: https://www.icici.bank.in/personal-banking/cards/credit-card/amazon-pay-credit-card/faqs
- FAQ-confirmed: Prime 5% on Amazon India, non-Prime 3% on
  Amazon (except digital products and gift cards, 2%),
  2% on 100+ Amazon Pay partner merchant websites, 1% on
  all other payments. No limit on earnings. Earnings as
  Amazon Pay balance, no expiry while active.
  Lifetime free (no joining / annual fee).
- Transaction-cost note (secondary, to confirm in T&C):
  from 15 Jan 2026, 1% fee on wallet loads of ₹5,000+.
  The engine models this as a transaction fee, subtracted
  from net reward, not as a lower cashback rate.
- Exclusions to confirm in T&C: EMI, fuel, gold, rent, tax,
  non-Amazon utilities (named in secondary summaries).

### 3. Airtel Axis Bank Credit Card — Axis Bank
- Cashback T&C PDF (effective 12 Apr 2026):
  https://www.axisbank.com/docs/default-source/default-document-library/credit-cards/terms-and-conditions-for-cashback-for-airtel-axis-bank-credit-card.pdf?sfvrsn=3192829c_10
- T&C-confirmed structure: 1% base cashback, no cap, on
  other eligible spends. 25% on Airtel mobile / broadband /
  WiFi / DTH via Airtel Thanks App, capped at 2× the base
  cashback earned in the same statement cycle. 10% on other
  utility payments via Thanks App, capped at 1× base cashback
  earned in the same cycle. 10% value-back on preferred
  merchants (Zomato, Blinkit, District Movies), capped at
  ₹200 per partner per month, credited to the partner wallet
  (not statement credit), ecom/online only (UPI not eligible),
  coupon required, minimum order ₹499 for Zomato / Blinkit.
- Version note: before 12 Apr 2026 the accelerated caps were
  ₹250/month (not base-linked) and the partner benefit was
  10% on Swiggy / Zomato / BigBasket. Lounge access was
  discontinued from 12 Apr 2026. Version both.
- Why this matters for the schema: a single-transaction
  recommendation cannot know the Airtel/utility cap without
  knowing base cashback already earned this cycle. The v2
  engine therefore takes `base_cashback_earned_inr` as an
  input and labels the result `estimated` when it is unknown.

## Other 7 issuers — v3, 3 Nov 2026

All cards below remain `pending_review`. "Official T&C parsed"
means the PDF text was extracted and the headline rates/caps
below were read from that text, not from a marketing page.
Redemption documents are still the weakest link for most —
where a point value is a placeholder, it is labelled as such
in the seed, not presented as verified.

### 4. HDFC Bank — Millennia (official T&C parsed)
- T&C PDF, published 20 Jul 2026:
  https://www.hdfc.bank.in/content/dam/hdfcbankpws/in/en/personal-banking/discover-products/cards/credit-cards/millennia-credit-card/pdf/millennia-tnc-20th-jul26.pdf
  Local: `data/official/hdfc-millennia-tnc.pdf/.txt`
- Parsed: 5% on Amazon, BookMyShow, Cult.fit, Flipkart,
  Myntra, Sony LIV, Swiggy, Tata CLiQ, Uber, Zomato, max
  1,000 CashPoints per cycle. Other spends 1%, max 1,000
  per cycle, except Fuel, EMI, Wallet, Rent, Govt.
  CashPoints posted on calendar-month basis, settled
  1st–30/31st, posted 1st week next month. 1 CashPoint =
  ₹1 on statement redemption. Education via third-party
  apps and wallet/EMI do NOT earn (from 1 Sep 2024).
- Correction vs v1/v2 seed: v2 gave 5% to any online
  merchant and a single ₹1,000 monthly cap. That was
  wrong. v3 is merchant-specific for the 10 merchants,
  with two separate ₹1,000 calendar-month group caps.
- Still to confirm: statement-redemption minimum (500
  points) and fee (₹50) and 3,000/month redemption cap
  named in secondary summaries — not hard-coded yet.

### 5. HDFC Bank — Regalia Gold (secondary-sourced, to confirm)
- Base 4 points / ₹150 retail, including insurance,
  utilities, education. Accelerated 20 points / ₹150 at
  Myntra, Marks & Spencer, Nykaa, Reliance Digital.
  Redemption: statement credit ₹0.20/point, SmartBuy
  flights/hotels ₹0.50, Gold Catalogue ₹0.65, products/
  vouchers ₹0.35. Fee ₹2,500, waiver ₹4 lakh annual
  spend (secondary). Bonus caps in secondary summaries
  conflict (5,000/month across brands vs 4,000 SmartBuy
  bonus/month), so NO bonus cap is hard-coded in v3.
  Next step: fetch HDFC's official Regalia Gold T&C / MITC.

### 6. IDFC FIRST Bank — Wealth (official T&C parsed)
- Rewards T&C PDF:
  https://stage.idfcfirst.bank.in/content/dam/idfcfirstbank/pdf/Wealth-CC-Rewards-Structure-TnC-28-05-25-copy.pdf
  Local: `data/official/idfc-wealth-rewards-tnc.pdf/.txt`
- Parsed: 10 points on Dining, Travel, International.
  3 points on all other eligible spends. Only 3 points
  on Rent, Government, Wallet Load, Education. Only
  1 point on Insurance, Utilities, Railway, Fastag.
  Points per ₹200 spent, not ₹150 — v1/v2 seed was
  wrong on the block size and is fixed in v3. No points
  on fuel, EMI, cash withdrawal, fees, or transactions
  below ₹200. Dining MCCs 5812–5814, Travel MCCs
  3000–3350 etc. Points valid 24 months. 1 point = ₹0.25.
  Redemption fee ₹99+GST is a redemption cost, not a
  per-transaction fee. Bonus points on app travel
  bookings (20% hotels, 10% flights from 18 Jan 2026,
  monthly bonus cap 8,000) are not modelled yet.
- Caution: a secondary review notes international spends
  may stop earning from 26 Oct 2026. That change is NOT
  in the T&C parsed here, so it is flagged, not hard-coded.

### 7. Kotak Mahindra Bank — Cashback+ Prime (official T&C parsed)
- T&C PDF:
  https://www.kotak.bank.in/content/dam/Kotak/files/t-and-c-cb-plus-prime.pdf
  Local: `data/official/kotak-cashback-plus-prime-tnc.pdf/.txt`
- Parsed: Accelerated 5% on online food & grocery
  delivery, online entertainment, auto dealer spends,
  capped at 750 reward points per billing cycle, post-cap
  0%. Fuel 3% in the T&C example. Other eligible 0.50%
  unlimited. Insurance (MCC 6300) 0.50% up to ₹25,000
  insurance spends per billing cycle — a spend cap, not
  yet modelled as a reward cap in v2. UPI on CC (RuPay
  variant) 0.50% unlimited. Points expire 1 year from
  accrual, earned in multiples of ₹1. Excluded: rent,
  B2B, utilities, education, government, wallet, online
  skill gaming, EMI. General Kotak point value ₹0.25
  (official FAQ, BizEdge page) is a cross-check, not a
  Cashback+ Prime redemption value.

### 8. American Express — Platinum Travel (official product page)
- Product page:
  https://www.americanexpress.com/in/credit-cards/platinum-travel-credit-card/?linknav=in-amex-cardshop-details-browse-AmericanExpressPlatinumTravel
- Parsed: 1 Membership Rewards point per ₹50, except
  fuel, insurance, utilities, cash transactions and EMI
  at POS. Fee ₹5,000 + taxes. Points do not expire while
  the card is active (from 3 May 2022), forfeited 30 days
  after cancellation. Milestones: ₹4 lakh spend → 10,000
  points, ₹7 lakh → Taj voucher ₹20,000, ₹15,000 in
  90 days → 10,000 welcome points. Point value varies
  by redemption — v3 default ₹0.25 is a placeholder,
  not a verified Amex value. Correction vs v1: v1 used
  1 point / ₹100, which was wrong.

### 9. AU Small Finance Bank — CS Credit Card (official T&C parsed)
- Reward Points T&C PDF:
  https://au.bank.in/pdfs/au-cs-credit-card/AU-CS-Credit-Card-Reward-Points-Terms-and-Conditions.pdf
  Local: `data/official/au-cs-rewards-tnc.pdf/.txt`
- Parsed, MCC-based: 8 points / ₹100 dining, travel,
  tax payments, software purchase. 1 point / ₹100
  utility, telecom, insurance. 2 points / ₹100 retail.
  Exclusions: fuel, rent, wallet, cash, education &
  government, BBPS via AU 0101 app. Point value is NOT
  stated in this T&C extract — v3 default ₹0.25 is a
  placeholder. AU's general FAQ also notes rewards only
  on POS and online retail, excluding cash withdrawals
  and fuel, and that balance transfer, EMI, charges etc.
  do not accrue.

### 10. RBL Bank — Platinum Plus (official product page)
- Product page:
  https://www.rbl.bank.in:443/personal-banking/cards/credit-cards/platinum-plus-credit-card?onlineCardPayment=netBanking
- Parsed: 1 point / ₹100, 2x online capped at 1,000
  points (modelled as ₹250 reward-value cap, since
  1,000 × ₹0.25). Point value varies ₹0.11–₹0.25; the
  official page says calculations assume ₹0.25, so v3
  uses ₹0.25. Fee ₹999 + GST. Exclusions: education,
  insurance, utilities, rent, fuel, wallet, plus auto,
  quasi-cash, railways, real estate, service providers,
  government, contracted services, Bills2Pay, EMI,
  miscellaneous, cash. RBL's TVS / Patanjali pages show
  the same exclusion pattern and a ₹0.25 point value.

### 11. IndusInd Bank — Pinnacle World modelled in v4, 3 Nov 2026
- MITC downloaded: Premium MITC PDF, file dated
  27 Jun 2017 (`data/official/indusind-premium-mitc-2017.pdf/.txt`,
  6 pp). It lists Pinnacle joining ₹12,999, Nil annual
  then, forex 3.5% (Legend 1.8%), fuel surcharge 1%
  waived ₹400–₹4,000. It is OUTDATED and contains no
  earn rates — MITC alone cannot determine a calculation.
  Do not use its 2017 fees as current.
- Official product evidence used instead:
  - Credit-card page (3 Nov 2026):
    https://www.indusind.bank.in/in/en/personal/cards/credit-card.html
    — Pinnacle: 2.5 points per ₹100 online (e-commerce),
    points never expire, fuel surcharge waiver.
  - Official blog (10 Sep 2026):
    https://www.indusind.bank.in/iblogs/credit-card/best-credit-cards-for-online-shopping/
    — Pinnacle: 2.5 / ₹100 e-commerce, 1.5 / ₹100
    e-com travel and airlines.
  - Legend blog (21 Oct 2026) was also filed, for
    comparison only, not modelled: Legend 1 / ₹100
    weekdays, 2 / ₹100 weekends, ₹0.75 cash value,
    4,000 bonus points at ₹6 lakh/year, 1.8% forex.
- Modelled (still `pending_review`, NOT verified):
  2.5 / ₹100 online shopping, 1.5 / ₹100 online travel,
  1 / ₹100 general, point value ₹0.75 cash credit,
  fee ₹15,000 (HF cross-check, see below), fuel excluded.
  Engine now supports fractional points (2.5 / 1.5 per
  ₹100) — v4 change, `points_per_block` is now float.
- Point-value conflict, resolved on evidence: PerkPilot
  (Sep 2026) says ₹0.40/point, but the HF dataset row
  `indusind-pinnacle` (Aug 2026) gives a reward range
  0.75%–1.88%, which is exactly 1×₹0.75 to 2.5×₹0.75,
  and multiple secondary pages say cash credit
  1 point = ₹0.75 (KrisFlyer 2 points = 1 mile).
  Engine uses ₹0.75 for cash credit and flags the
  PerkPilot ₹0.40 figure as the outlier, not the rule.
- NOT hard-coded: a 7,500-point-per-cycle cash-credit
  REDEMPTION cap (secondary, consistent) — it caps
  redemption, not earning, so it is not an earn cap.
  Broader exclusions (rent/wallets/utility/government)
  from one secondary source are also not hard-coded;
  rent is elsewhere described as capped at 500 points
  per cycle, not excluded. A clean, current Pinnacle
  detailed-features T&C PDF is still not filed — that
  is the remaining verification gap for this card.
- Tests: `backend/tests/test_engine_v4.py`, 5 new tests,
  26 total passing. API catalogue now 12 cards.

