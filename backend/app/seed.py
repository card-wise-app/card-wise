"""Seed catalogue for the MVP demo — v2.

Status policy (unchanged from v1):
Every card below is verification_status="pending_review".
The three cards with official source URLs below (SBI Cashback,
Amazon Pay ICICI, Axis Airtel) have FAQ / T&C-confirmed
headline rates and caps, filed in data/source_registry.md,
but their full exclusion lists and redemption documents have
NOT yet been parsed end to end, so they are NOT marked
"verified". All other cards are sample / placeholder rules
for engine testing only.

Replace / promote a card to "verified" only after:
  product page + T&C + redemption terms are filed in
  data/official/, parsed, and diffed against the previous
  version, with source_url, last_verified_date and
  effective_from set.
"""
from .engine import Card, RewardRule

SAMPLE_NOTICE = "Sample rule for MVP testing only - not issuer verified"


def seed_cards() -> list[Card]:
    return [
        # --- SBI Cashback: FAQ-confirmed, effective 1 Apr 2026 ---
        Card(
            id="sbi-cashback", issuer="SBI Card", name="SBI Cashback Card",
            network="Visa", reward_system="cashback",
            annual_fee_inr=999, fee_waiver_spend_inr=200000,
            aggregate_cap_inr=4000, aggregate_cap_scope="statement_cycle",
            posting_basis="posting_date",
            source_url="https://www.sbicard.com/en/faq/cashback-sbi-card-faq.page",
            source_urls=[
                "https://www.sbicard.com/en/faq/cashback-sbi-card-faq.page",
                "https://www.sbicard.com/sbi-card-en/assets/docs/pdf/ekit-tncs/cashback-tnc-ekit.pdf",
            ],
            effective_from="2026-04-01",
            # FAQ-confirmed only: fuel. Full cardholder T&C exclusion
            # list is still to be parsed — do not copy secondary lists here.
            exclusions=["fuel"],
            rules=[
                RewardRule(category="online_shopping", channel="online",
                           cashback_rate_pct=5, cap_group="online",
                           cap_scope="statement_cycle", cap_value_inr=2000),
                RewardRule(category="general", channel="offline",
                           cashback_rate_pct=1, cap_group="offline",
                           cap_scope="statement_cycle", cap_value_inr=2000),
                RewardRule(category="general", cashback_rate_pct=1,
                           cap_group="offline", cap_scope="statement_cycle",
                           cap_value_inr=2000),
            ],
        ),
        # --- Amazon Pay ICICI: FAQ-confirmed ---
        Card(
            id="amazon-pay-icici", issuer="ICICI Bank", name="Amazon Pay ICICI",
            network="Visa", reward_system="cashback",
            annual_fee_inr=0,
            posting_basis="posting_date",
            source_url="https://www.icici.bank.in/personal-banking/cards/credit-card/amazon-pay-credit-card/faqs",
            source_urls=["https://www.icici.bank.in/personal-banking/cards/credit-card/amazon-pay-credit-card/faqs"],
            # Exclusion list still to be confirmed from Amazon Pay T&C;
            # secondary summaries name EMI, fuel, gold, rent, tax and
            # non-Amazon utilities, but those are not hard-coded here
            # until the T&C text is extracted.
            exclusions=[],
            rules=[
                RewardRule(category="online_shopping", merchant="Amazon",
                           cashback_rate_pct=5, requires_membership="prime",
                           redemption_type="amazon_pay_balance"),
                RewardRule(category="online_shopping", merchant="Amazon",
                           cashback_rate_pct=3, requires_membership="non_prime",
                           redemption_type="amazon_pay_balance"),
                RewardRule(category="digital_products", merchant="Amazon",
                           cashback_rate_pct=2, requires_membership="non_prime",
                           redemption_type="amazon_pay_balance"),
                RewardRule(category="amazon_pay_partner",
                           cashback_rate_pct=2, redemption_type="amazon_pay_balance"),
                RewardRule(category="general", cashback_rate_pct=1,
                           redemption_type="amazon_pay_balance"),
            ],
        ),
        # --- HDFC Millennia: T&C 20 Jul 2026, calendar-month caps ---
        Card(
            id="hdfc-millennia", issuer="HDFC Bank", name="HDFC Millennia",
            network="Visa", reward_system="cashback",
            annual_fee_inr=1000, fee_waiver_spend_inr=100000,
            posting_basis="posting_date",
            source_url="https://www.hdfc.bank.in/content/dam/hdfcbankpws/in/en/personal-banking/discover-products/cards/credit-cards/millennia-credit-card/pdf/millennia-tnc-20th-jul26.pdf",
            source_urls=["https://www.hdfc.bank.in/content/dam/hdfcbankpws/in/en/personal-banking/discover-products/cards/credit-cards/millennia-credit-card/pdf/millennia-tnc-20th-jul26.pdf"],
            effective_from="2026-07-20",
            # T&C: other spends except Fuel, EMI, Wallet, Rent, Govt.
            # CashPoints posted on calendar-month basis, settled
            # 1st-30/31st, posted 1st week next month. 1 CashPoint = Rs 1
            # on statement redemption. Redemption fee / minimum balance
            # are not modelled in the engine yet — see registry.
            exclusions=["fuel", "emi", "wallet", "rent", "government"],
            rules=[
                # 10 merchants, merchant-specific so a non-listed
                # online merchant does NOT get 5% by mistake.
                RewardRule(category="online_shopping", merchant="Amazon",
                           cashback_rate_pct=5, cap_group="accelerated",
                           cap_scope="monthly", cap_value_inr=1000),
                RewardRule(category="online_shopping", merchant="Flipkart",
                           cashback_rate_pct=5, cap_group="accelerated",
                           cap_scope="monthly", cap_value_inr=1000),
                RewardRule(category="online_shopping", merchant="Swiggy",
                           cashback_rate_pct=5, cap_group="accelerated",
                           cap_scope="monthly", cap_value_inr=1000),
                RewardRule(category="food_delivery", merchant="Zomato",
                           cashback_rate_pct=5, cap_group="accelerated",
                           cap_scope="monthly", cap_value_inr=1000),
                RewardRule(category="online_shopping", merchant="Myntra",
                           cashback_rate_pct=5, cap_group="accelerated",
                           cap_scope="monthly", cap_value_inr=1000),
                RewardRule(category="online_shopping", merchant="Tata CLiQ",
                           cashback_rate_pct=5, cap_group="accelerated",
                           cap_scope="monthly", cap_value_inr=1000),
                RewardRule(category="transport", merchant="Uber",
                           cashback_rate_pct=5, cap_group="accelerated",
                           cap_scope="monthly", cap_value_inr=1000),
                RewardRule(category="entertainment", merchant="BookMyShow",
                           cashback_rate_pct=5, cap_group="accelerated",
                           cap_scope="monthly", cap_value_inr=1000),
                RewardRule(category="entertainment", merchant="Sony LIV",
                           cashback_rate_pct=5, cap_group="accelerated",
                           cap_scope="monthly", cap_value_inr=1000),
                RewardRule(category="entertainment", merchant="Cult.fit",
                           cashback_rate_pct=5, cap_group="accelerated",
                           cap_scope="monthly", cap_value_inr=1000),
                RewardRule(category="general", cashback_rate_pct=1,
                           cap_group="other", cap_scope="monthly",
                           cap_value_inr=1000),
            ],
        ),
        # --- Axis Airtel: T&C effective 12 Apr 2026 ---
        Card(
            id="axis-airtel", issuer="Axis Bank", name="Axis Airtel",
            network="Visa", reward_system="cashback",
            annual_fee_inr=500, fee_waiver_spend_inr=200000,
            posting_basis="posting_date",
            source_url="https://www.axisbank.com/docs/default-source/default-document-library/credit-cards/terms-and-conditions-for-cashback-for-airtel-axis-bank-credit-card.pdf?sfvrsn=3192829c_10",
            source_urls=["https://www.axisbank.com/docs/default-source/default-document-library/credit-cards/terms-and-conditions-for-cashback-for-airtel-axis-bank-credit-card.pdf?sfvrsn=3192829c_10"],
            effective_from="2026-04-12",
            # Exclusions confirmed in the Axis T&C PDF itself, p. "Other
            # Cashback Terms": EMI, cash advances, fuel, rent, wallet
            # recharge, jewellery, insurance, education, government,
            # utility/telecom outside Thanks App, gift cards, tolls.
            exclusions=["fuel", "rent", "wallet_recharge", "jewellery",
                        "insurance", "education", "government",
                        "gift_cards", "tolls", "cash_advance", "emi"],
            rules=[
                RewardRule(category="airtel_bill", merchant="Airtel",
                           cashback_rate_pct=25, cap_multiplier_of_base=2.0,
                           cap_group="airtel_accelerated"),
                RewardRule(category="utilities",
                           cashback_rate_pct=10, cap_multiplier_of_base=1.0,
                           cap_group="utility_accelerated"),
                RewardRule(category="food_delivery", merchant="Zomato",
                           cashback_rate_pct=10, per_transaction_cap_inr=200,
                           redemption_type="partner_wallet", coupon_required=True,
                           min_order_inr=499),
                RewardRule(category="groceries", merchant="Blinkit",
                           cashback_rate_pct=10, per_transaction_cap_inr=200,
                           redemption_type="partner_wallet", coupon_required=True,
                           min_order_inr=499),
                RewardRule(category="entertainment", merchant="District Movies",
                           cashback_rate_pct=10, per_transaction_cap_inr=200,
                           redemption_type="partner_wallet", coupon_required=True),
                RewardRule(category="general", cashback_rate_pct=1),
            ],
        ),
        Card(
            id="axis-flipkart", issuer="Axis Bank", name="Axis Flipkart",
            network="Visa", reward_system="cashback",
            rules=[
                RewardRule(category="online_shopping", merchant="Flipkart", cashback_rate_pct=5),
                RewardRule(category="general", cashback_rate_pct=1),
            ],
        ),
        # --- IDFC FIRST Wealth: Rewards T&C (per Rs 200, not Rs 150) ---
        Card(
            id="idfc-wealth", issuer="IDFC FIRST Bank", name="IDFC FIRST Wealth",
            network="Visa", reward_system="points",
            posting_basis="posting_date",
            source_url="https://stage.idfcfirst.bank.in/content/dam/idfcfirstbank/pdf/Wealth-CC-Rewards-Structure-TnC-28-05-25-copy.pdf",
            source_urls=["https://stage.idfcfirst.bank.in/content/dam/idfcfirstbank/pdf/Wealth-CC-Rewards-Structure-TnC-28-05-25-copy.pdf"],
            # No points on fuel, EMI, cash withdrawal, fees, or
            # transactions below Rs 200. Points valid 24 months.
            # 1 point = Rs 0.25. Redemption fee Rs 99+GST is a
            # redemption cost, not a transaction fee, so it is not
            # subtracted per transaction in the engine.
            exclusions=["fuel", "emi", "cash_advance"],
            rules=[
                RewardRule(category="food_delivery", points_per_block=10, block_amount_inr=200, point_value_inr=0.25, min_transaction_inr=200),
                RewardRule(category="travel", points_per_block=10, block_amount_inr=200, point_value_inr=0.25, min_transaction_inr=200),
                RewardRule(category="rent", points_per_block=3, block_amount_inr=200, point_value_inr=0.25, min_transaction_inr=200),
                RewardRule(category="government", points_per_block=3, block_amount_inr=200, point_value_inr=0.25, min_transaction_inr=200),
                RewardRule(category="wallet", points_per_block=3, block_amount_inr=200, point_value_inr=0.25, min_transaction_inr=200),
                RewardRule(category="education", points_per_block=3, block_amount_inr=200, point_value_inr=0.25, min_transaction_inr=200),
                RewardRule(category="insurance", points_per_block=1, block_amount_inr=200, point_value_inr=0.25, min_transaction_inr=200),
                RewardRule(category="utilities", points_per_block=1, block_amount_inr=200, point_value_inr=0.25, min_transaction_inr=200),
                RewardRule(category="transport", points_per_block=1, block_amount_inr=200, point_value_inr=0.25, min_transaction_inr=200),
                RewardRule(category="general", points_per_block=3, block_amount_inr=200, point_value_inr=0.25, min_transaction_inr=200),
            ],
        ),
        # --- HDFC Regalia Gold: base confirmed across sources, ---
        # --- redemption values are secondary-sourced, to confirm ---
        # --- from HDFC's official product page / MITC. ---
        Card(
            id="hdfc-regalia-gold", issuer="HDFC Bank", name="HDFC Regalia Gold",
            network="Visa", reward_system="points",
            annual_fee_inr=2500, fee_waiver_spend_inr=400000,
            posting_basis="posting_date",
            # 4 points / Rs 150 retail (including insurance, utilities,
            # education); 20 points / Rs 150 at Myntra, Marks & Spencer,
            # Nykaa, Reliance Digital. Statement credit Rs 0.20/point,
            # SmartBuy flights/hotels Rs 0.50, Gold Catalogue Rs 0.65.
            # Engine default uses statement-credit value Rs 0.20.
            # Bonus caps (5,000/month across brands, 4,000 SmartBuy
            # bonus/month in secondary summaries) conflict, so no
            # bonus cap is hard-coded until the official T&C is parsed.
            rules=[
                RewardRule(category="online_shopping", merchant="Myntra", points_per_block=20, block_amount_inr=150, point_value_inr=0.20),
                RewardRule(category="online_shopping", merchant="Nykaa", points_per_block=20, block_amount_inr=150, point_value_inr=0.20),
                RewardRule(category="online_shopping", merchant="Reliance Digital", points_per_block=20, block_amount_inr=150, point_value_inr=0.20),
                RewardRule(category="general", points_per_block=4, block_amount_inr=150, point_value_inr=0.20),
            ],
        ),
        # --- Amex Platinum Travel: official product page ---
        Card(
            id="amex-platinum-travel", issuer="American Express", name="American Express Platinum Travel",
            network="American Express", reward_system="points",
            annual_fee_inr=5000,
            posting_basis="posting_date",
            source_url="https://www.americanexpress.com/in/credit-cards/platinum-travel-credit-card/?linknav=in-amex-cardshop-details-browse-AmericanExpressPlatinumTravel",
            source_urls=["https://www.americanexpress.com/in/credit-cards/platinum-travel-credit-card/?linknav=in-amex-cardshop-details-browse-AmericanExpressPlatinumTravel"],
            # 1 point / Rs 50, except fuel, insurance, utilities,
            # cash transactions and EMI at POS. Points do not expire
            # while the card is active (from 3 May 2022), forfeited
            # 30 days after cancellation. Point value varies by
            # redemption (travel collection etc.) — engine default
            # Rs 0.25 is a placeholder, not a verified Amex value.
            exclusions=["fuel", "insurance", "utilities", "cash_advance", "emi"],
            rules=[
                RewardRule(category="general", points_per_block=1, block_amount_inr=50, point_value_inr=0.25),
            ],
        ),
        # --- Kotak Cashback+ Prime: official T&C ---
        Card(
            id="kotak-cashback-plus-prime", issuer="Kotak Mahindra Bank", name="Kotak Cashback+ Prime",
            network="Visa", reward_system="cashback",
            posting_basis="posting_date",
            source_url="https://www.kotak.bank.in/content/dam/Kotak/files/t-and-c-cb-plus-prime.pdf",
            source_urls=["https://www.kotak.bank.in/content/dam/Kotak/files/t-and-c-cb-plus-prime.pdf"],
            # Accelerated 5% capped at 750 reward points / billing
            # cycle, post-cap 0%. Fuel 3% in the T&C example.
            # Other eligible 0.50% unlimited. Insurance 0.50% up to
            # Rs 25,000 insurance spends / billing cycle (spend cap,
            # not modelled as a reward cap in v2 — see registry).
            # Points expire 1 year from accrual, earned in multiples
            # of Rs 1. Excluded: rent, B2B, utilities, education,
            # government, wallet, online skill gaming, EMI.
            exclusions=["rent", "utilities", "education", "government", "wallet", "emi"],
            rules=[
                RewardRule(category="food_delivery", cashback_rate_pct=5, cap_group="accelerated", cap_scope="statement_cycle", cap_value_inr=750),
                RewardRule(category="groceries", cashback_rate_pct=5, cap_group="accelerated", cap_scope="statement_cycle", cap_value_inr=750),
                RewardRule(category="entertainment", cashback_rate_pct=5, cap_group="accelerated", cap_scope="statement_cycle", cap_value_inr=750),
                RewardRule(category="fuel", cashback_rate_pct=3),
                RewardRule(category="insurance", cashback_rate_pct=0.5),
                RewardRule(category="general", cashback_rate_pct=0.5),
            ],
        ),
        # --- AU CS: official Reward Points T&C (MCC-based) ---
        Card(
            id="au-cs", issuer="AU Small Finance Bank", name="AU CS Credit Card",
            network="Visa", reward_system="points",
            posting_basis="posting_date",
            source_url="https://au.bank.in/pdfs/au-cs-credit-card/AU-CS-Credit-Card-Reward-Points-Terms-and-Conditions.pdf",
            source_urls=["https://au.bank.in/pdfs/au-cs-credit-card/AU-CS-Credit-Card-Reward-Points-Terms-and-Conditions.pdf"],
            # 8 points / Rs 100 dining, travel, tax, software.
            # 1 point / Rs 100 utility, telecom, insurance.
            # 2 points / Rs 100 retail. Exclusions: fuel, rent,
            # wallet, cash, education & government, BBPS via AU 0101.
            # Point value is NOT stated in this T&C extract — engine
            # default Rs 0.25 is a placeholder, not verified.
            exclusions=["fuel", "rent", "wallet", "cash_advance", "education", "government"],
            rules=[
                RewardRule(category="food_delivery", points_per_block=8, block_amount_inr=100, point_value_inr=0.25),
                RewardRule(category="travel", points_per_block=8, block_amount_inr=100, point_value_inr=0.25),
                RewardRule(category="utilities", points_per_block=1, block_amount_inr=100, point_value_inr=0.25),
                RewardRule(category="insurance", points_per_block=1, block_amount_inr=100, point_value_inr=0.25),
                RewardRule(category="general", points_per_block=2, block_amount_inr=100, point_value_inr=0.25),
            ],
        ),
        # --- IndusInd Pinnacle World: official IndusInd pages ---
        Card(
            id="indusind-pinnacle", issuer="IndusInd Bank", name="IndusInd Pinnacle World",
            network="Mastercard", reward_system="points",
            annual_fee_inr=15000,
            posting_basis="posting_date",
            source_url="https://www.indusind.bank.in/in/en/personal/cards/credit-card.html",
            source_urls=[
                "https://www.indusind.bank.in/in/en/personal/cards/credit-card.html",
                "https://www.indusind.bank.in/iblogs/credit-card/best-credit-cards-for-online-shopping/",
            ],
            # Official IndusInd credit-card page: 2.5 points per
            # Rs 100 online (e-commerce). Official IndusInd blog:
            # 1.5 points per Rs 100 e-com travel / airlines.
            # Base 1 point per Rs 100 other spends: consistent
            # across secondary product pages; HF cross-check
            # (indusind-pinnacle, Aug 2026) gives reward range
            # 0.75%-1.88%, which is exactly 1 x Rs 0.75 to
            # 2.5 x Rs 0.75, corroborating the Rs 0.75 point value.
            # Point value conflict, flagged not hidden: PerkPilot
            # (Sep 2026, citing the product page) says Rs 0.40
            # per point; multiple other sources and the HF
            # 0.75-1.88% range say Rs 0.75 cash credit. Engine
            # uses Rs 0.75 for cash credit; KrisFlyer is 2 points
            # = 1 mile (secondary), a different redemption value.
            # Cash-credit redemption cap 7,500 points per
            # statement cycle (secondary, consistent) is a
            # REDEMPTION cap, not an earn cap, so it is not
            # coded as an earn cap here.
            # MITC: the Premium MITC PDF found is dated 2017
            # (Pinnacle joining Rs 12,999, Nil annual then) and
            # is outdated; current fee Rs 15,000 is HF + secondary.
            # Points never expire (official credit-card page).
            # Exclusions: fuel only is consistently confirmed
            # (no points on fuel). Broader exclusions in one
            # secondary source (rent/wallets/utility/government)
            # are NOT hard-coded, as rent is elsewhere said to
            # be capped at 500 points/cycle, not excluded.
            exclusions=["fuel"],
            rules=[
                RewardRule(category="online_shopping", channel="online", points_per_block=2.5, block_amount_inr=100, point_value_inr=0.75),
                RewardRule(category="travel", channel="online", points_per_block=1.5, block_amount_inr=100, point_value_inr=0.75),
                RewardRule(category="general", points_per_block=1, block_amount_inr=100, point_value_inr=0.75),
            ],
        ),
        # --- RBL Platinum Plus: official product page ---
        Card(
            id="rbl-platinum-plus", issuer="RBL Bank", name="RBL Platinum Plus",
            network="Visa", reward_system="points",
            annual_fee_inr=999,
            posting_basis="posting_date",
            source_url="https://www.rbl.bank.in:443/personal-banking/cards/credit-cards/platinum-plus-credit-card?onlineCardPayment=netBanking",
            source_urls=["https://www.rbl.bank.in:443/personal-banking/cards/credit-cards/platinum-plus-credit-card?onlineCardPayment=netBanking"],
            # 1 point / Rs 100, 2x online capped at 1,000 points.
            # Point value varies Rs 0.11-0.25; official page says
            # calculations assume Rs 0.25, so engine uses Rs 0.25.
            # Exclusions: education, insurance, utilities, rent,
            # fuel, wallet, plus auto, quasi-cash, railways, real
            # estate, service providers, government, contracted,
            # Bills2Pay, EMI, miscellaneous, cash.
            exclusions=["education", "insurance", "utilities", "rent", "fuel", "wallet", "government", "emi", "cash_advance"],
            rules=[
                # Engine caps are in Rs value, not points: 1,000 points
                # x Rs 0.25 = Rs 250 reward-value cap for the online 2x.
                RewardRule(category="online_shopping", channel="online", points_per_block=2, block_amount_inr=100, point_value_inr=0.25, cap_group="online_bonus", cap_value_inr=250),
                RewardRule(category="general", points_per_block=1, block_amount_inr=100, point_value_inr=0.25),
            ],
        ),
    ]
