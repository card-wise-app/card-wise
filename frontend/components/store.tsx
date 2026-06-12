"use client";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { CATALOGUE, type CardDef } from "@/lib/catalogue";

export type WalletCard = { cardId: string; prime?: boolean; usedByGroup?: Record<string, number> };
type Store = {
  wallet: WalletCard[];
  add: (id: string) => void;
  remove: (id: string) => void;
  togglePrime: (id: string) => void;
  clear: () => void;
  addSampleWallet: () => void;
  cards: CardDef[];
};

const Ctx = createContext<Store | null>(null);
const KEY = "cardwise-wallet-v1";

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const [wallet, setWallet] = useState<WalletCard[]>([]);
  const [loaded, setLoaded] = useState(false);
  useEffect(() => {
    try {
      const raw = localStorage.getItem(KEY);
      if (raw) setWallet(JSON.parse(raw));
    } catch { /* empty wallet on bad storage */ }
    setLoaded(true);
  }, []);
  useEffect(() => {
    if (loaded) localStorage.setItem(KEY, JSON.stringify(wallet));
  }, [wallet, loaded]);

  const value = useMemo<Store>(() => ({
    wallet,
    cards: wallet.map((w) => CATALOGUE.find((c) => c.id === w.cardId)!).filter(Boolean),
    add: (id) => setWallet((w) => (w.some((x) => x.cardId === id) ? w : [...w, { cardId: id }])),
    remove: (id) => setWallet((w) => w.filter((x) => x.cardId !== id)),
    togglePrime: (id) => setWallet((w) => w.map((x) => (x.cardId === id ? { ...x, prime: !x.prime } : x))),
    clear: () => setWallet([]),
    addSampleWallet: () => setWallet([
      { cardId: "sbi-cashback" }, { cardId: "icici-amazon-pay", prime: true }, { cardId: "indusind-pinnacle" },
    ]),
  }), [wallet]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useWallet() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useWallet must be used inside WalletProvider");
  return v;
}
