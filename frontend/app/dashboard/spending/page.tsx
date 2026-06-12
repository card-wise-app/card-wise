import { CardShell, VerifiedNote } from "@/components/ui";

const ROWS = [
  { merchant: "Amazon", category: "Online shopping", amount: 5000, best: "SBI Cashback Card", value: 250 },
  { merchant: "Swiggy", category: "Food delivery", amount: 1200, best: "HDFC Millennia", value: 60 },
  { merchant: "Airtel bill", category: "Utilities", amount: 800, best: "Axis Airtel", value: 8 },
];

export default function Spending() {
  return (
    <div>
      <h1 className="text-4xl font-bold">Spending</h1>
      <p className="mt-2 text-muted">Monthly spending by category, with the card that would have won each purchase. Sample rows only — no statement import in this build.</p>
      <CardShell className="mt-8 overflow-x-auto p-0">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead><tr className="border-b border-line text-muted"><th className="px-5 py-4">Merchant</th><th className="px-5 py-4">Category</th><th className="px-5 py-4">Amount</th><th className="px-5 py-4">Best card (sample)</th><th className="px-5 py-4">Est. reward</th></tr></thead>
          <tbody>
            {ROWS.map((r) => (
              <tr key={r.merchant} className="border-b border-line last:border-0">
                <td className="px-5 py-4 font-semibold">{r.merchant}</td><td className="px-5 py-4">{r.category}</td>
                <td className="px-5 py-4">₹{r.amount.toLocaleString("en-IN")}</td><td className="px-5 py-4">{r.best}</td><td className="px-5 py-4 font-semibold">₹{r.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardShell>
      <p className="mt-4 text-sm text-muted">Statement import is a P2 feature in the PRD and is not in this build. Nothing here is imported from a bank.</p>
      <div className="mt-6"><VerifiedNote /></div>
    </div>
  );
}
