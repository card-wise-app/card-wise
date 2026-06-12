"use client";
import { useState } from "react";
import { Button, CardShell, Field, inputCls } from "@/components/ui";
import { useWallet } from "@/components/store";

export default function Settings() {
  const { clear } = useWallet();
  const [apiUrl, setApiUrl] = useState(process.env.NEXT_PUBLIC_API_URL || "");
  const [saved, setSaved] = useState(false);
  return (
    <div>
      <h1 className="text-4xl font-bold">Settings</h1>
      <p className="mt-2 text-muted">Demo settings only. There is no account, no password and no bank connection in this build.</p>
      <CardShell className="mt-8 p-6">
        <h2 className="text-xl font-bold">Backend (optional)</h2>
        <p className="mt-2 text-sm text-muted">The FastAPI backend runs the authoritative deterministic engine. If you set NEXT_PUBLIC_API_URL at build time, the frontend can fetch its catalogue. In this demo build, calculations run locally from the same pending-review rules, so results stay consistent with your browser wallet.</p>
        <Field label="FastAPI URL (build-time env, shown for reference)"><input className={inputCls} value={apiUrl} onChange={(e) => setApiUrl(e.target.value)} placeholder="http://localhost:8000" /></Field>
        <Button className="mt-4" onClick={() => setSaved(true)}>Save (demo only)</Button>
        {saved && <p className="mt-3 text-sm font-medium">Saved in this demo view only. To actually use a backend URL, set NEXT_PUBLIC_API_URL before building and rebuild.</p>}
      </CardShell>
      <CardShell className="mt-6 p-6">
        <h2 className="text-xl font-bold">Your data</h2>
        <p className="mt-2 text-sm text-muted">Your wallet is stored in this browser's localStorage only. Clearing it removes your wallet from this device. No card number, CVV or OTP is ever stored.</p>
        <Button variant="outline" className="mt-4" onClick={() => { clear(); alert("Wallet cleared from this browser."); }}>Clear my wallet</Button>
      </CardShell>
    </div>
  );
}
