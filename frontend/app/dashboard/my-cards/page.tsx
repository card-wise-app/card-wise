"use client";
import { useState } from "react";
import { Button, CardShell, Field, inputCls, Pill, VerifiedNote, Notice } from "@/components/ui";
import CardArt from "@/components/CardArt";
import { CATALOGUE, inr } from "@/lib/catalogue";
import { useWallet } from "@/components/store";

export default function MyCards() {
  const { wallet, cards, add, remove, togglePrime, addSampleWallet, clear } = useWallet();
  const [q, setQ] = useState("");
  const [customName, setCustomName] = useState("");
  const [customRate, setCustomRate] = useState(2);
  const [customNote, setCustomNote] = useState("");
  const filtered = CATALOGUE.filter((c) => `${c.issuer} ${c.name}`.toLowerCase().includes(q.toLowerCase()));
  const inWallet = (id: string) => wallet.some((w) => w.cardId === id);

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div><h1 className="text-4xl font-bold">My Cards</h1><p className="mt-2 text-muted">Add catalogue cards or a custom card. Never a full number, CVV or OTP.</p></div>
        <div className="flex gap-2"><Button onClick={addSampleWallet} variant="outline">Add sample wallet</Button><Button onClick={clear} variant="outline">Clear wallet</Button></div>
      </div>

      <section className="mt-8">
        <h2 className="text-xl font-bold">Your wallet ({cards.length})</h2>
        {cards.length === 0 ? (
          <CardShell className="mt-3 p-6 text-center">
            <p className="font-semibold">Your wallet is empty.</p>
            <p className="mt-1 text-sm text-muted">Search below and add a card, or start with the clearly labelled sample wallet.</p>
          </CardShell>
        ) : (
          <div className="mt-3 grid gap-4 md:grid-cols-2">
            {cards.map((c) => {
              const w = wallet.find((x) => x.cardId === c.id)!;
              return (
                <CardShell key={c.id} className="p-5">
                  <CardArt issuer={c.issuer} name={c.name} art={c.art} className="w-full" />
                  <div className="mt-4 flex items-start justify-between gap-3">
                    <div><h3 className="font-bold">{c.name}</h3><p className="text-sm text-muted">{c.issuer} · {c.network} · {inr(c.annualFeeInr)}/yr fee (catalogue)</p><p className="mt-2 text-sm leading-relaxed">{c.blurb}</p></div>
                    <Pill>Pending review</Pill>
                  </div>
                  {c.id === "icici-amazon-pay" && (
                    <label className="mt-4 flex items-center gap-2 text-sm font-medium"><input type="checkbox" checked={!!w.prime} onChange={() => togglePrime(c.id)} /> Amazon Prime member</label>
                  )}
                  <Button onClick={() => remove(c.id)} variant="outline" className="mt-4">Remove card</Button>
                </CardShell>
              );
            })}
          </div>
        )}
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-bold">Search the catalogue</h2>
        <Field label="Search by bank, card name or variant"><input className={inputCls} value={q} onChange={(e) => setQ(e.target.value)} placeholder="e.g. SBI, Millennia, Pinnacle" /></Field>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {filtered.map((c) => (
            <CardShell key={c.id} className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div><h3 className="font-bold">{c.name}</h3><p className="text-sm text-muted">{c.issuer} · {c.network}</p><p className="mt-2 text-sm leading-relaxed">{c.blurb}</p></div>
                <Pill>Pending review</Pill>
              </div>
              <p className="mt-3 text-xs text-muted">Source: {c.source} · Exclusions modelled: {c.exclusions.join(", ") || "none"}</p>
              <Button onClick={() => add(c.id)} variant={inWallet(c.id) ? "outline" : "primary"} className="mt-4">{inWallet(c.id) ? "In your wallet" : "Add to My Cards"}</Button>
            </CardShell>
          ))}
          {filtered.length === 0 && <p className="text-sm text-muted">No catalogue card matches that search. Try a bank name, or add a custom card below.</p>}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-bold">Add a custom card</h2>
        <CardShell className="mt-3 p-6">
          <div className="grid gap-4 md:grid-cols-3">
            <Field label="Card name"><input className={inputCls} value={customName} onChange={(e) => setCustomName(e.target.value)} placeholder="e.g. My travel card" /></Field>
            <Field label="Flat cashback rate (%)"><input className={inputCls} type="number" value={customRate} onChange={(e) => setCustomRate(Number(e.target.value))} /></Field>
            <Field label="Your note (caps, exclusions)"><input className={inputCls} value={customNote} onChange={(e) => setCustomNote(e.target.value)} placeholder="e.g. No fuel, ₹1,000 cap" /></Field>
          </div>
          <Notice><span>Custom cards are stored only in your browser in this demo and are always labelled <strong>user-defined — not issuer verified</strong>. Full custom-card editing (per-category rates, statement-cycle caps, point values) is in the backend API; this demo form captures the headline rate only, so it does not pretend to be the full custom-card editor.</span></Notice>
          <Button className="mt-4" onClick={() => { if (customName.trim()) { setCustomName(""); setCustomNote(""); alert("Custom-card editor: headline captured in this demo. Use the backend API (POST /users/custom-cards) for the full per-category custom card."); } }}>Save custom card (demo note)</Button>
        </CardShell>
        <div className="mt-6"><VerifiedNote /></div>
      </section>
    </div>
  );
}
