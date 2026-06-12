"use client";
import Link from "next/link";
import { Button, CardShell, Pill, VerifiedNote } from "@/components/ui";
import { useWallet } from "@/components/store";
import { CATALOGUE, inr } from "@/lib/catalogue";

export default function Overview() {
  const { wallet, cards, addSampleWallet } = useWallet();
  const sampleValue = 187.5 + 250 + 187.5; // illustrative only, labelled below
  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold">Overview</h1>
          <p className="mt-2 text-muted">Your wallet, your rewards, and the next purchase — in one place.</p>
        </div>
        <Button href="/dashboard/finder">Find the best card for my purchase</Button>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-4">
        <CardShell className="p-5"><p className="text-sm text-muted">Cards added</p><p className="mt-2 text-4xl font-bold">{cards.length}</p><p className="mt-1 text-xs text-muted">of {CATALOGUE.length} in catalogue</p></CardShell>
        <CardShell dark className="p-5"><p className="text-sm text-white/60">Estimated total rewards</p><p className="mt-2 text-4xl font-bold text-lime">{cards.length ? inr(sampleValue) : "₹0"}</p><p className="mt-1 text-xs text-white/50">Illustrative sample, not a balance</p></CardShell>
        <CardShell className="p-5"><p className="text-sm text-muted">Monthly cashback</p><p className="mt-2 text-4xl font-bold">₹1,250</p><p className="mt-1 text-xs text-muted">Sample month</p></CardShell>
        <CardShell className="p-5"><p className="text-sm text-muted">Total reward points</p><p className="mt-2 text-4xl font-bold">3,240</p><p className="mt-1 text-xs text-muted">Sample points</p></CardShell>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-5">
        <CardShell className="p-6 lg:col-span-3">
          <div className="flex items-center justify-between"><h2 className="text-xl font-bold">Recent recommendations</h2><Pill>Sample</Pill></div>
          {cards.length === 0 ? (
            <div className="mt-4 rounded-[20px] border border-dashed border-line p-6 text-center">
              <p className="font-semibold">No recommendations yet.</p>
              <p className="mt-1 text-sm text-muted">Add a card, then run the finder. Nothing here is a real transaction.</p>
              <div className="mt-4 flex justify-center gap-2">
                <Button href="/dashboard/my-cards" variant="outline">Add cards</Button>
                <Button onClick={addSampleWallet}>Add sample wallet</Button>
              </div>
            </div>
          ) : (
            <ul className="mt-4 space-y-2">
              {cards.slice(0, 4).map((c) => (
                <li key={c.id} className="flex items-center justify-between rounded-[16px] bg-paper px-4 py-3 text-sm">
                  <span><strong>{c.name}</strong> <span className="text-muted">· {c.issuer}</span></span>
                  <span className="text-muted">In your wallet</span>
                </li>
              ))}
              <li className="px-4 py-2 text-sm text-muted">Run the finder to generate a real recommendation for your next purchase.</li>
            </ul>
          )}
        </CardShell>
        <CardShell dark className="p-6 lg:col-span-2">
          <h2 className="text-xl font-bold">Next best move</h2>
          <p className="mt-2 text-sm leading-relaxed text-white/70">Before a ₹5,000 Amazon purchase, check the finder. A capped 5% card can lose to an uncapped card once the cap is used — the finder applies the cap before it ranks.</p>
          <Button href="/dashboard/finder" variant="lime" className="mt-5">Open the finder</Button>
        </CardShell>
      </div>
      <div className="mt-6"><VerifiedNote /></div>
    </div>
  );
}
