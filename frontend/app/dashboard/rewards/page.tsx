import { CardShell, Pill, VerifiedNote } from "@/components/ui";

export default function Rewards() {
  return (
    <div>
      <h1 className="text-4xl font-bold">Rewards</h1>
      <p className="mt-2 text-muted">Estimated rewards, caps remaining, and trends — all from pending-review rules, so treat them as estimates.</p>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        <CardShell className="p-6"><p className="text-sm text-muted">Total estimated rewards</p><p className="mt-2 text-4xl font-bold">₹1,875</p><p className="mt-1 text-xs text-muted">Sample month · illustrative</p></CardShell>
        <CardShell dark className="p-6"><p className="text-sm text-white/60">Cashback earned (sample)</p><p className="mt-2 text-4xl font-bold text-lime">₹1,250</p><p className="mt-1 text-xs text-white/50">From SBI + ICICI sample rules</p></CardShell>
        <CardShell className="p-6"><p className="text-sm text-muted">Reward points (sample)</p><p className="mt-2 text-4xl font-bold">3,240</p><p className="mt-1 text-xs text-muted">Across points cards in the sample wallet</p></CardShell>
      </div>
      <CardShell className="mt-6 p-6">
        <div className="flex items-center justify-between"><h2 className="text-xl font-bold">Remaining reward limits</h2><Pill>Sample</Pill></div>
        <ul className="mt-4 space-y-3 text-sm">
          <li className="flex justify-between gap-4"><span>SBI Cashback — online cycle cap</span><strong>₹2,000 remaining (sample: ₹0 used)</strong></li>
          <li className="flex justify-between gap-4"><span>SBI Cashback — aggregate cycle cap</span><strong>₹4,000 remaining (sample: ₹0 used)</strong></li>
          <li className="flex justify-between gap-4"><span>HDFC Millennia — accelerated cap</span><strong>1,000 CashPoints remaining (sample)</strong></li>
          <li className="flex justify-between gap-4"><span>Axis Airtel — partner value-back</span><strong>₹200 / partner / month (sample)</strong></li>
        </ul>
        <p className="mt-4 text-sm text-muted">In the full product, cap usage is entered per card (see My Cards / backend usage endpoint) and the finder subtracts it before ranking. If usage is unknown, the result is labelled estimated and the cap is never assumed unused.</p>
      </CardShell>
      <div className="mt-6"><VerifiedNote /></div>
    </div>
  );
}
