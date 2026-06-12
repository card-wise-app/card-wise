# CardWise frontend — premium redesign (3 Nov 2026)

Next.js 14 + TypeScript + Tailwind CSS + Lucide icons.
Palette: paper #F7F7F5, ink #17171C, lime #C1FF72, white, border #E5E5E2.
Type: Space Grotesk headings, Inter body. 8px spacing, 20–24px card radii,
thin borders, minimal shadows. No purple gradients, no glassmorphism.

## Run

```bash
cd frontend
npm install
npm run dev      # http://localhost:3000
npm run build && npm run start
```

## Pages

- `/` — landing: nav, hero ("Your cards. Your money. Your smartest move."),
  how it works, interactive Best Card Finder preview, My Cards /
  dashboard preview, trust, FAQ, footer.
- `/dashboard` — overview (cards added, illustrative rewards, recent recs)
- `/dashboard/my-cards` — search catalogue, add/remove, Prime toggle,
  custom-card demo note (full custom editor lives in the FastAPI API)
- `/dashboard/finder` — Best Card Finder: best, alternatives, excluded
  with reason, calculation, cap note, source, confidence
- `/dashboard/rewards` — estimated rewards + remaining caps (sample)
- `/dashboard/spending` — sample spending rows (no statement import)
- `/dashboard/settings` — backend URL note + clear wallet

## Data honesty

- The browser finder in `lib/catalogue.ts` is a deterministic
  mirror of the backend seed's headline rules. Every card is
  `pending_review` and every result is labelled estimated.
- The FastAPI engine in `backend/app/engine.py` is authoritative
  for group caps, base-linked caps and posting basis. If you
  connect it (NEXT_PUBLIC_API_URL at build time), use it for
  calculations; this demo keeps wallet + calculation consistent
  in the browser so the demo works with no backend.
- Wallet is stored in localStorage on the user's device only.
  No full card number, CVV or OTP is ever asked for or stored.
- Sample dashboard numbers (₹1,875, 3,240 points, ₹1,250) are
  labelled sample/illustrative on the page. They are not a
  balance, a testimonial or a real user's spending.
