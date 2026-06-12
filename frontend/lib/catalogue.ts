// CardWise catalogue + deterministic finder logic (browser layer).
//
// HONESTY CONTRACT — read before reusing these numbers:
// - Every card below is `pending_review` in the backend seed.
//   None is issuer-verified, and none may be presented as verified.
// - The rules are the headline rules modelled from official issuer
//   pages / T&Cs in data/source_registry.md (see backend seed.py
//   for full notes, caps and exclusions). This file mirrors the
//   simplified headline rule per category; the FastAPI engine in
//   backend/app/engine.py is the authoritative calculation and
//   handles group caps, base-linked caps and posting basis.
// - If you connect the FastAPI backend (NEXT_PUBLIC_API_URL),
//   use it for calculations. This browser layer exists so the
//   demo works with no backend, and every result it produces is
//   labelled "Estimated — pending review" unless the user has
//   supplied cap usage and MCC, in which case it is still an
//   estimate from pending-review rules.
// - Never ask for a full card number, CVV or OTP. This layer
//   stores only card ids, cap usage and membership flags, in
//   localStorage on the user's own device.

export type Rule = {
  category: string;
  channel?: "any" | "online" | "offline";
  cashbackPct?: number;
  pointsPer100?: number;
  pointValue?: number;
  capInr?: number;
  capGroup?: string;
  note?: string;
};

export type CardDef = {
  id: string;
  issuer: string;
  name: string;
  network: string;
  rewardSystem: "cashback" | "points";
  annualFeeInr: number;
  verification: "pending_review";
  source: string;
  exclusions: string[];
  rules: Rule[];
  blurb: string;
  art: "lime" | "dark" | "white";
};

export const CATEGORIES = [
  { value: "online_shopping", label: "Online shopping" },
  { value: "travel", label: "Travel" },
  { value: "food_delivery", label: "Food delivery" },
  { value: "groceries", label: "Groceries" },
  { value: "fuel", label: "Fuel" },
  { value: "utilities", label: "Utilities" },
  { value: "general", label: "General / other" },
] as const;

export const CATALOGUE: CardDef[] = [
  {
    id: "sbi-cashback", issuer: "SBI Card", name: "SBI Cashback Card", network: "Visa",
    rewardSystem: "cashback", annualFeeInr: 999, verification: "pending_review",
    source: "SBI Card FAQ + Cashback T&C (see source registry)",
    exclusions: ["fuel"], blurb: "5% online, 1% offline. Separate ₹2,000 cycle caps, ₹4,000 aggregate from 1 Apr 2026.",
    art: "dark",
    rules: [
      { category: "online_shopping", channel: "online", cashbackPct: 5, capInr: 2000, capGroup: "online" },
      { category: "general", channel: "offline", cashbackPct: 1, capInr: 2000, capGroup: "offline" },
      { category: "general", cashbackPct: 1 },
    ],
  },
  {
    id: "icici-amazon-pay", issuer: "ICICI Bank", name: "Amazon Pay ICICI", network: "Visa",
    rewardSystem: "cashback", annualFeeInr: 0, verification: "pending_review",
    source: "ICICI Amazon Pay FAQ",
    exclusions: [], blurb: "Prime 5% on Amazon, non-Prime 3%, partner merchants 2%, everything else 1%. As Amazon Pay balance.",
    art: "white",
    rules: [
      { category: "online_shopping", channel: "online", cashbackPct: 5, note: "Prime only — see membership toggle" },
      { category: "general", cashbackPct: 1 },
    ],
  },
  {
    id: "hdfc-millennia", issuer: "HDFC Bank", name: "HDFC Millennia", network: "Visa",
    rewardSystem: "points", annualFeeInr: 1000, verification: "pending_review",
    source: "HDFC Millennia T&C, 20 Jul 2026",
    exclusions: ["fuel", "rent", "government"],
    blurb: "5% (as CashPoints) on 10 listed merchants only, 1% elsewhere. Two separate 1,000-point cycle caps.",
    art: "lime",
    rules: [
      { category: "online_shopping", channel: "online", pointsPer100: 5, pointValue: 1, capInr: 1000, capGroup: "accelerated" },
      { category: "general", pointsPer100: 1, pointValue: 1, capInr: 1000, capGroup: "other" },
    ],
  },
  {
    id: "axis-airtel", issuer: "Axis Bank", name: "Axis Airtel", network: "Visa",
    rewardSystem: "cashback", annualFeeInr: 500, verification: "pending_review",
    source: "Axis Airtel Cashback T&C, effective 12 Apr 2026",
    exclusions: ["fuel", "rent"],
    blurb: "1% base, 25% on Airtel via Thanks App capped at 2× base earned. Partner value-back goes to partner wallet, not statement.",
    art: "dark",
    rules: [
      { category: "utilities", channel: "online", cashbackPct: 10, note: "Via Airtel Thanks App; cap is base-linked — see backend engine" },
      { category: "general", cashbackPct: 1 },
    ],
  },
  {
    id: "indusind-pinnacle", issuer: "IndusInd Bank", name: "IndusInd Pinnacle World", network: "Mastercard",
    rewardSystem: "points", annualFeeInr: 15000, verification: "pending_review",
    source: "IndusInd credit-card page + official blog (MITC filed is 2017, outdated)",
    exclusions: ["fuel"], blurb: "2.5 points / ₹100 online e-commerce, 1.5 / ₹100 online travel, 1 / ₹100 other. 1 point = ₹0.75 cash credit.",
    art: "lime",
    rules: [
      { category: "online_shopping", channel: "online", pointsPer100: 2.5, pointValue: 0.75 },
      { category: "travel", channel: "online", pointsPer100: 1.5, pointValue: 0.75 },
      { category: "general", pointsPer100: 1, pointValue: 0.75 },
    ],
  },
  {
    id: "idfc-wealth", issuer: "IDFC FIRST Bank", name: "IDFC FIRST Wealth", network: "Visa",
    rewardSystem: "points", annualFeeInr: 0, verification: "pending_review",
    source: "IDFC FIRST Wealth Rewards T&C",
    exclusions: ["fuel"],
    blurb: "10 points / ₹200 dining, travel, international; 3 / ₹200 other; 1 / ₹200 insurance, utilities, rail, Fastag. 1 point = ₹0.25.",
    art: "white",
    rules: [
      { category: "travel", pointsPer100: 5, pointValue: 0.25 },
      { category: "general", pointsPer100: 1.5, pointValue: 0.25 },
    ],
  },
  {
    id: "kotak-cashback-plus", issuer: "Kotak", name: "Kotak Cashback+ Prime", network: "Visa",
    rewardSystem: "points", annualFeeInr: 0, verification: "pending_review",
    source: "Kotak Cashback+ Prime T&C",
    exclusions: ["rent", "utilities"],
    blurb: "5% accelerated on online food, grocery, entertainment, capped at 750 points / cycle. Fuel 3%, other 0.50%.",
    art: "dark",
    rules: [
      { category: "food_delivery", channel: "online", cashbackPct: 5, capInr: 187.5, note: "Accelerated cap is 750 points / cycle (≈ ₹187.50 at ₹0.25)" },
      { category: "fuel", cashbackPct: 3 },
      { category: "general", cashbackPct: 0.5 },
    ],
  },
  {
    id: "amex-platinum-travel", issuer: "American Express", name: "Amex Platinum Travel", network: "Amex",
    rewardSystem: "points", annualFeeInr: 5000, verification: "pending_review",
    source: "Amex India product page",
    exclusions: ["fuel", "insurance", "utilities"],
    blurb: "1 Membership Rewards point / ₹50, except fuel, insurance, utilities, cash, EMI at POS. Point value varies by redemption.",
    art: "white",
    rules: [{ category: "general", pointsPer100: 2, pointValue: 0.25, note: "₹0.25 is a placeholder, not a verified Amex value" }],
  },
];

export type FinderResult = {
  card: CardDef;
  eligible: boolean;
  value: number;
  points: number;
  rateLabel: string;
  reason: string;
  confidence: "estimated";
};

function pickRule(card: CardDef, category: string, channel: string): Rule | null {
  const exact = card.rules.find((r) => r.category === category && (r.channel === "any" || !r.channel || r.channel === channel));
  if (exact) return exact;
  return card.rules.find((r) => r.category === "general") || null;
}

export function calculate(
  card: CardDef, merchant: string, category: string, amount: number,
  channel: "online" | "offline" | "any", prime: boolean, usedByGroup: Record<string, number> = {},
): FinderResult {
  const base: FinderResult = { card, eligible: false, value: 0, points: 0, rateLabel: "", reason: "", confidence: "estimated" };
  if (card.exclusions.includes(category)) {
    return { ...base, reason: `Excluded: ${category} earns nothing on this card.` };
  }
  const rule = pickRule(card, category, channel === "any" ? "online" : channel);
  if (!rule) return { ...base, reason: "No eligible reward rule for this category." };
  // ICICI Prime split, the one membership rule in this browser layer.
  let cb = rule.cashbackPct ?? 0;
  if (card.id === "icici-amazon-pay" && category === "online_shopping" && channel !== "offline") {
    cb = prime ? 5 : 3;
  }
  let value = 0, points = 0, label = "";
  if (rule.cashbackPct !== undefined) {
    value = (amount * cb) / 100;
    label = `${cb}% cashback`;
  } else if (rule.pointsPer100 !== undefined) {
    points = Math.floor(amount / 100) * rule.pointsPer100;
    value = points * (rule.pointValue ?? 0.25);
    label = `${rule.pointsPer100} points / ₹100 at ₹${rule.pointValue ?? 0.25} per point`;
  }
  if (rule.capInr !== undefined && rule.capGroup) {
    const used = usedByGroup[rule.capGroup] || 0;
    const remaining = Math.max(0, rule.capInr - used);
    value = Math.min(value, remaining);
  }
  const notes = [rule.note, "Estimated — rule is pending review, not issuer-verified."].filter(Boolean).join(" ");
  return { card, eligible: true, value: Math.round(value * 100) / 100, points, rateLabel: label, reason: notes, confidence: "estimated" };
}

export function findBest(
  cards: CardDef[], merchant: string, category: string, amount: number,
  channel: "online" | "offline" | "any", prime: boolean, usedByGroup: Record<string, number> = {},
) {
  const all = cards.map((c) => calculate(c, merchant, category, amount, channel, prime, usedByGroup));
  const eligible = all.filter((r) => r.eligible).sort((a, b) => b.value - a.value);
  return { best: eligible[0] || null, alternatives: eligible.slice(1), excluded: all.filter((r) => !r.eligible), all };
}

export function inr(n: number) {
  return "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 2, minimumFractionDigits: n % 1 ? 2 : 0 });
}
