"use client";
import { useState } from "react";
import Link from "next/link";
import { ArrowUpRight, CreditCard, Search, Sparkles, ShieldCheck, FileCheck, Calculator, Wallet, TrendingUp, Check, ChevronDown } from "lucide-react";
import { Button, Pill, CardShell, Field, inputCls, VerifiedNote, Notice } from "@/components/ui";
import CardArt from "@/components/CardArt";
import { CATALOGUE, findBest, inr, CATEGORIES } from "@/lib/catalogue";

function Nav() {
  return (
    <header className="sticky top-0 z-40 border-b border-line bg-paper/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-lime text-lg font-bold">C</span>
          <span className="text-xl font-bold tracking-tight">CardWise</span>
        </Link>
        <nav className="hidden items-center gap-7 text-sm font-medium md:flex">
          <a href="#how">How it works</a><a href="#finder">Best Card Finder</a>
          <a href="#cards">My Cards</a><a href="#dashboard">Dashboard</a><a href="#faq">FAQ</a>
        </nav>
        <div className="flex items-center gap-2">
          <Button href="/dashboard" variant="outline" className="hidden sm:inline-flex">Sign in</Button>
          <Button href="/dashboard">Get started</Button>
        </div>
      </div>
    </header>
  );
}

function FinderPreview() {
  const [merchant, setMerchant] = useState("Amazon");
  const [amount, setAmount] = useState(5000);
  const [category, setCategory] = useState("online_shopping");
  const [channel, setChannel] = useState<"online" | "offline">("online");
  const [prime, setPrime] = useState(true);
  const sample = CATALOGUE.filter((c) => ["sbi-cashback", "icici-amazon-pay", "indusind-pinnacle"].includes(c.id));
  const res = findBest(sample, merchant, category, amount, channel, prime);
  return (
    <CardShell className="p-6 md:p-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div><h3 className="text-2xl font-bold">Best Card Finder — preview</h3>
        <p className="mt-1 text-sm text-muted">Illustrative example only. Real results use your wallet and pending-review rules.</p></div>
        <Pill>₹5,000 · Amazon example</Pill>
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-4">
        <Field label="Merchant"><input className={inputCls} value={merchant} onChange={(e) => setMerchant(e.target.value)} /></Field>
        <Field label="Purchase amount (₹)"><input className={inputCls} type="number" value={amount} onChange={(e) => setAmount(Number(e.target.value))} /></Field>
        <Field label="Category"><select className={inputCls} value={category} onChange={(e) => setCategory(e.target.value)}>{CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}</select></Field>
        <Field label="Channel"><select className={inputCls} value={channel} onChange={(e) => setChannel(e.target.value as "online" | "offline")}><option value="online">Online</option><option value="offline">In-store</option></select></Field>
      </div>
      <label className="mt-4 flex items-center gap-2 text-sm font-medium"><input type="checkbox" checked={prime} onChange={(e) => setPrime(e.target.checked)} /> Amazon Prime member (changes the ICICI result)</label>
      {res.best && (
        <div className="mt-6 grid gap-4 lg:grid-cols-5">
          <div className="rounded-[20px] bg-ink p-6 text-white lg:col-span-2">
            <p className="text-xs font-semibold uppercase tracking-wide text-lime">Recommended</p>
            <p className="mt-2 text-2xl font-bold">{res.best.card.name}</p>
            <p className="text-sm text-white/70">{res.best.card.issuer} · {res.best.rateLabel}</p>
            <p className="mt-4 text-4xl font-bold text-lime">{inr(res.best.value)}</p>
            <p className="mt-1 text-sm text-white/70">estimated reward · {res.best.points ? `${res.best.points} points` : "cashback"}</p>
            <p className="mt-3 text-xs leading-relaxed text-white/60">{res.best.reason}</p>
          </div>
          <div className="lg:col-span-3">
            <p className="text-sm font-semibold">Alternatives</p>
            <ul className="mt-3 space-y-2">
              {res.alternatives.map((a) => (
                <li key={a.card.id} className="flex items-center justify-between rounded-[16px] border border-line bg-paper px-4 py-3 text-sm">
                  <span><strong>{a.card.name}</strong> <span className="text-muted">· {a.rateLabel}</span></span>
                  <strong>{inr(a.value)}</strong>
                </li>
              ))}
              {res.excluded.map((a) => (
                <li key={a.card.id} className="flex items-center justify-between rounded-[16px] border border-dashed border-line px-4 py-3 text-sm text-muted">
                  <span>{a.card.name} — excluded, never hidden</span><span>{a.reason}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
      <div className="mt-6 flex flex-wrap gap-3">
        <Button href="/dashboard/finder">Try it with your cards</Button>
        <Button href="/dashboard/my-cards" variant="outline">Add your cards</Button>
      </div>
    </CardShell>
  );
}

const FAQS = [
  ["Do I need to share my card number, CVV or OTP?", "No. CardWise never asks for them. You add a card by name and issuer, and set your own cap usage and memberships."],
  ["Are the reward numbers guaranteed?", "No. Every rule in this build is pending review against official issuer terms, and results are labelled estimated when cap usage or MCC is unknown. The engine never assumes a cap is unused."],
  ["Why do two cards show different values for the same purchase?", "Rates, caps, exclusions and point values differ by issuer. A 5% headline rate capped at ₹1,000 can lose to a lower uncapped rate on a large purchase — that is exactly what the finder shows."],
  ["What happens when a bank changes its terms?", "Rules are versioned with effective dates in the backend. A changed rule is flagged for review before it replaces the old one; it is never silently overwritten."],
];

export default function Landing() {
  const [open, setOpen] = useState(0);
  return (
    <main>
      <Nav />
      {/* Hero */}
      <section className="mx-auto grid max-w-7xl items-center gap-10 px-5 py-14 md:py-20 lg:grid-cols-2">
        <div>
          <Pill>India · INR · Credit card rewards, explained</Pill>
          <h1 className="mt-5 text-5xl font-bold leading-[1.02] md:text-7xl">Your cards.<br />Your money.<br /><span className="bg-lime px-2">Your smartest move.</span></h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">Find out which of your credit cards gives you the maximum cashback and rewards on every purchase — with the cap, the exclusion and the reason shown, not hidden.</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button href="/dashboard/finder">Find my best card <ArrowUpRight className="h-4 w-4" /></Button>
            <Button href="#how" variant="outline">How it works</Button>
          </div>
          <div className="mt-8 flex flex-wrap gap-6 text-sm">
            <span className="flex items-center gap-2"><ShieldCheck className="h-4 w-4" /> No CVV or OTP, ever</span>
            <span className="flex items-center gap-2"><FileCheck className="h-4 w-4" /> Sourced from issuer terms</span>
            <span className="flex items-center gap-2"><Calculator className="h-4 w-4" /> Deterministic maths, no AI guessing</span>
          </div>
        </div>
        <div className="relative">
          <div className="absolute -right-2 top-6 rounded-full bg-lime px-4 py-2 text-sm font-bold shadow-soft">+ ₹250 on ₹5,000</div>
          <CardArt issuer="SBI Card" name="Cashback Card" art="dark" className="w-full rotate-[-2deg] shadow-soft" />
          <CardArt issuer="IndusInd Bank" name="Pinnacle World" art="lime" className="mt-[-52px] ml-auto w-[82%] rotate-[3deg] shadow-soft" />
          <div className="mt-4 flex items-center gap-3 rounded-[20px] border border-line bg-white p-4 text-sm">
            <Sparkles className="h-5 w-5 shrink-0" />
            <span><strong>Why SBI wins here:</strong> 5% online, within its ₹2,000 cycle cap. The full calculation is shown in the finder — never just a headline rate.</span>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="border-y border-line bg-white">
        <div className="mx-auto max-w-7xl px-5 py-16">
          <p className="text-sm font-bold uppercase tracking-wide">How it works</p>
          <h2 className="mt-2 max-w-2xl text-4xl font-bold">Three steps, before you tap pay.</h2>
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {[
              { icon: CreditCard, n: "01", t: "Add your cards.", d: "Search the catalogue or create a custom card with your own rates, caps and exclusions. Custom cards are always labelled unverified." },
              { icon: Search, n: "02", t: "Enter your purchase.", d: "Merchant, amount, category, online or in-store, and any membership that changes the rate — like Amazon Prime." },
              { icon: Sparkles, n: "03", t: "Find your best card.", d: "Best card first, alternatives next, excluded cards shown with the reason. Caps used, confidence, and source on every result." },
            ].map((s) => (
              <CardShell key={s.n} className="p-6 transition hover:-translate-y-1">
                <div className="flex items-center justify-between"><s.icon className="h-7 w-7" /><span className="text-4xl font-bold text-lime" style={{ WebkitTextStroke: "1px #17171C" }}>{s.n}</span></div>
                <h3 className="mt-6 text-2xl font-bold">{s.t}</h3><p className="mt-2 leading-relaxed text-muted">{s.d}</p>
              </CardShell>
            ))}
          </div>
        </div>
      </section>

      {/* Finder preview */}
      <section id="finder" className="mx-auto max-w-7xl px-5 py-16"><FinderPreview /></section>

      {/* My cards + dashboard preview */}
      <section id="cards" className="bg-ink text-white">
        <div className="mx-auto grid max-w-7xl gap-10 px-5 py-16 lg:grid-cols-2">
          <div>
            <p className="text-sm font-bold uppercase tracking-wide text-lime">My Cards</p>
            <h2 className="mt-2 text-4xl font-bold">Add once. Use before every purchase.</h2>
            <ul className="mt-6 space-y-3 text-white/80">
              {["Search by issuing bank, card name or variant.", "Add a custom card with cashback, points, caps and exclusions.", "Edit or remove a card in seconds. Your wallet lives on your device in this demo.", "Prime, partner and channel toggles that actually change the result."].map((t) => (
                <li key={t} className="flex gap-3"><Check className="mt-0.5 h-5 w-5 shrink-0 text-lime" /> {t}</li>
              ))}
            </ul>
            <div className="mt-8 flex gap-3"><Button href="/dashboard/my-cards" variant="lime">Open My Cards</Button><Button href="/dashboard" variant="outline" className="border-white/30 bg-transparent text-white">See the dashboard</Button></div>
          </div>
          <div id="dashboard" className="grid content-start gap-4">
            <CardShell dark className="p-6">
              <p className="text-sm text-white/60">Rewards dashboard — preview</p>
              <div className="mt-4 grid grid-cols-3 gap-4">
                <div><p className="text-3xl font-bold text-lime">12</p><p className="text-xs text-white/60">Cards in catalogue</p></div>
                <div><p className="text-3xl font-bold">₹1,875</p><p className="text-xs text-white/60">Illustrative monthly value</p></div>
                <div><p className="text-3xl font-bold">3,240</p><p className="text-xs text-white/60">Reward points, sample</p></div>
              </div>
              <div className="mt-5 h-24 rounded-[16px] bg-white/10 p-3">
                <svg viewBox="0 0 300 80" className="h-full w-full"><polyline points="0,60 50,45 100,52 150,30 200,38 250,18 300,10" fill="none" stroke="#C1FF72" strokeWidth="3" /></svg>
              </div>
              <p className="mt-3 text-xs text-white/50">Trend shown is illustrative sample data, not your spending.</p>
            </CardShell>
            <Notice><span className="text-ink"><strong>Trust, in one line:</strong> official issuer sources, versioned rules, clear maths — and no card number, CVV or OTP, ever.</span></Notice>
          </div>
        </div>
      </section>

      {/* Trust */}
      <section className="mx-auto max-w-7xl px-5 py-16">
        <h2 className="text-4xl font-bold">Transparent by design.</h2>
        <div className="mt-8 grid gap-5 md:grid-cols-4">
          {[
            ["Official sources", "Every published rule carries a source URL and an effective date."],
            ["Verified, or labelled", "Unverified rules never look verified. Pending review is shown on the card."],
            ["Caps, not just rates", "Monthly, statement-cycle, group and aggregate caps are applied before ranking."],
            ["Excluded, not hidden", "A card that earns zero on a purchase is shown with its exclusion reason."],
          ].map(([t, d]) => (
            <CardShell key={t} className="p-5"><h3 className="font-bold">{t}</h3><p className="mt-2 text-sm leading-relaxed text-muted">{d}</p></CardShell>
          ))}
        </div>
        <div className="mt-6"><VerifiedNote /></div>
      </section>

      {/* FAQ */}
      <section id="faq" className="border-t border-line bg-white">
        <div className="mx-auto max-w-4xl px-5 py-16">
          <h2 className="text-4xl font-bold">Questions, answered plainly.</h2>
          <div className="mt-8 space-y-3">
            {FAQS.map(([q, a], i) => (
              <div key={q} className="rounded-[20px] border border-line">
                <button onClick={() => setOpen(i)} className="flex w-full items-center justify-between px-5 py-4 text-left font-semibold">
                  {q}<ChevronDown className={`h-5 w-5 transition ${open === i ? "rotate-180" : ""}`} />
                </button>
                {open === i && <p className="px-5 pb-5 leading-relaxed text-muted">{a}</p>}
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="bg-ink text-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-start justify-between gap-8 px-5 py-12">
          <div><p className="text-2xl font-bold">CardWise</p><p className="mt-2 max-w-sm text-sm text-white/60">Add your cards once. Know which card to use before every purchase.</p></div>
          <div className="flex gap-12 text-sm">
            <div><p className="font-bold text-lime">Product</p><ul className="mt-3 space-y-2 text-white/70"><li><Link href="/dashboard/finder">Best Card Finder</Link></li><li><Link href="/dashboard/my-cards">My Cards</Link></li><li><Link href="/dashboard/rewards">Rewards</Link></li></ul></div>
            <div><p className="font-bold text-lime">Company</p><ul className="mt-3 space-y-2 text-white/70"><li><a href="#how">How it works</a></li><li><a href="#faq">FAQ</a></li><li><a href="#finder">Preview</a></li></ul></div>
          </div>
        </div>
        <p className="border-t border-white/10 px-5 py-5 text-center text-xs text-white/50">CardWise is a demo in this build. Catalogue rules are pending review, not issuer-verified. Never share a full card number, CVV or OTP with any app.</p>
      </footer>
    </main>
  );
}
