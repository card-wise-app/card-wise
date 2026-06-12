"use client";
import FinderForm from "@/components/FinderForm";
import { VerifiedNote } from "@/components/ui";
import { useWallet } from "@/components/store";

export default function FinderPage() {
  const { cards } = useWallet();
  return (
    <div>
      <h1 className="text-4xl font-bold">Best Card Finder</h1>
      <p className="mt-2 max-w-2xl text-muted">Compare every card in your wallet for one purchase. Best first, alternatives next, excluded cards shown with the reason. No card number, CVV or OTP is ever asked for.</p>
      <div className="mt-8 rounded-[24px] border border-line bg-white p-6 md:p-8">
        <FinderForm cards={cards} />
      </div>
      <div className="mt-6"><VerifiedNote /></div>
    </div>
  );
}
