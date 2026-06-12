"use client";
import { useMemo, useState } from "react";
import { Button, CardShell, Field, inputCls, Pill } from "@/components/ui";
import { CATEGORIES, calculate, inr, type CardDef } from "@/lib/catalogue";
import { useWallet } from "@/components/store";

export default function FinderForm({ cards, preset }: { cards: CardDef[]; preset?: { merchant?: string; amount?: number; category?: string } }) {
  const { wallet } = useWallet();
  const [merchant, setMerchant] = useState(preset?.merchant || "Amazon");
  const [amount, setAmount] = useState(preset?.amount || 5000);
  const [category, setCategory] = useState(preset?.category || "online_shopping");
  const [channel, setChannel] = useState<"online" | "offline">("online");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  const primeById = useMemo(() => Object.fromEntries(wallet.map((w) => [w.cardId, !!w.prime])), [wallet]);
  const usedByGroup = useMemo(() => {
    const out: Record<string, number> = {};
    wallet.forEach((w) => Object.entries(w.usedByGroup || {}).forEach(([k, v]) => { out[k] = Math.max(out[k] || 0, v); }));
    return out;
  }, [wallet]);

  // Prime is per-card (set on My Cards), so calculate per card
  // with that card's own prime flag, not one global flag.
  const out = useMemo(() => {
    if (!submitted) return null;
    const all = cards.map((c) => calculate(c, merchant, category, amount, channel, !!primeById[c.id], usedByGroup));
    const eligible = all.filter((r) => r.eligible).sort((a, b) => b.value - a.value);
    return { best: eligible[0] || null, alternatives: eligible.slice(1), excluded: all.filter((r) => !r.eligible) };
  }, [submitted, cards, merchant, category, amount, channel, primeById, usedByGroup]);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!cards.length) { setError("Add at least one card to My Cards first."); return; }
    if (!merchant.trim() || !amount || amount <= 0) { setError("Enter a merchant and an amount greater than ₹0."); return; }
    setError(""); setSubmitted(true);
  }

  return (
    <div>
      <form onSubmit={submit} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Field label="Merchant" hint="Brand alone is not proof of MCC — results stay estimated without it.">
          <input className={inputCls} value={merchant} onChange={(e) => setMerchant(e.target.value)} placeholder="e.g. Amazon" />
        </Field>
        <Field label="Purchase amount (₹)">
          <input className={inputCls} type="number" min={1} value={amount} onChange={(e) => setAmount(Number(e.target.value))} />
        </Field>
        <Field label="Category">
          <select className={inputCls} value={category} onChange={(e) => setCategory(e.target.value)}>
            {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
          </select>
        </Field>
        <Field label="Channel">
          <select className={inputCls} value={channel} onChange={(e) => setChannel(e.target.value as "online" | "offline")}>
            <option value="online">Online</option><option value="offline">In-store / POS</option>
          </select>
        </Field>
        <div className="md:col-span-2 lg:col-span-4">
          <Button type="submit">Find the best card for my purchase</Button>
          {error && <p role="alert" className="mt-3 text-sm font-medium text-red-700">{error}</p>}
          {!cards.length && <p className="mt-3 text-sm text-muted">Your wallet is empty. Add a card on the My Cards page, or use the sample wallet there.</p>}
        </div>
      </form>

      {submitted && out && (
        <div className="mt-8 space-y-5">
          {out.best ? (
            <CardShell dark className="p-6 md:p-8">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <Pill>Recommended</Pill>
                  <h3 className="mt-3 text-3xl font-bold">{out.best.card.name}</h3>
                  <p className="mt-1 text-white/70">{out.best.card.issuer} · {out.best.rateLabel}</p>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-bold text-lime">{inr(out.best.value)}</p>
                  <p className="text-sm text-white/70">estimated reward{out.best.points ? ` · ${out.best.points} points` : ""}</p>
                </div>
              </div>
              <div className="mt-5 grid gap-3 text-sm md:grid-cols-3">
                <div className="rounded-[16px] bg-white/10 p-4"><p className="text-white/60">Calculation</p><p className="mt-1 font-semibold">{out.best.rateLabel} on {inr(amount)}</p></div>
                <div className="rounded-[16px] bg-white/10 p-4"><p className="text-white/60">Confidence</p><p className="mt-1 font-semibold">Estimated — pending-review rule</p></div>
                <div className="rounded-[16px] bg-white/10 p-4"><p className="text-white/60">Source</p><p className="mt-1 font-semibold">{out.best.card.source}</p></div>
              </div>
              <p className="mt-4 text-xs leading-relaxed text-white/60">{out.best.reason} Exclusions for this card: {out.best.card.exclusions.join(", ") || "none modelled"}.</p>
            </CardShell>
          ) : (
            <CardShell className="p-6"><p className="font-semibold">No eligible card in your wallet for this purchase.</p><p className="mt-1 text-sm text-muted">That is a real answer, not an error — check the excluded list below for why.</p></CardShell>
          )}

          {out.alternatives.length > 0 && (
            <div>
              <h3 className="text-xl font-bold">Other eligible cards</h3>
              <ul className="mt-3 space-y-2">
                {out.alternatives.map((a) => (
                  <li key={a.card.id} className="flex flex-wrap items-center justify-between gap-2 rounded-[20px] border border-line bg-white px-5 py-4">
                    <span><strong>{a.card.name}</strong> <span className="text-muted">· {a.card.issuer} · {a.rateLabel}</span></span>
                    <strong>{inr(a.value)}</strong>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {out.excluded.length > 0 && (
            <div>
              <h3 className="text-xl font-bold">Excluded cards — never hidden</h3>
              <ul className="mt-3 space-y-2">
                {out.excluded.map((a) => (
                  <li key={a.card.id} className="flex flex-wrap items-center justify-between gap-2 rounded-[20px] border border-dashed border-line px-5 py-4 text-sm text-muted">
                    <span><strong className="text-ink">{a.card.name}</strong> · {a.card.issuer}</span><span>{a.reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
