"""CardWise ingestion pipeline — v2 (PRD section 9).

Steps: fetch official source -> extract (local, $0) -> structured
JSON -> schema validation -> diff vs previous version -> flag
material changes -> require approval before publishing.

AI extraction may ASSIST, but it must never independently
publish unverified financial rules. This script only writes to
data/verified/<card>.json as a DRAFT with verification_status
"pending_review". Promotion to "verified" is a human/admin step.

Usage:
  python -m app.ingest --pdf data/official/axis-airtel-cashback-tnc.pdf
  python -m app.ingest --hf-cards data/raw/cards.csv --out data/verified/_hf_crosscheck.json

Firecrawl note: the repo is cloned at tools/firecrawl/ for
self-hosted extraction if needed. The default path here uses
requests + BeautifulSoup + PyMuPDF and costs $0. Do not call
Firecrawl Cloud without the user's explicit approval, because
that would add a paid dependency.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import pathlib
import re


def extract_pdf_text(pdf_path: pathlib.Path) -> str:
    try:
        import pymupdf
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("pip install pymupdf  (already in requirements)") from exc
    doc = pymupdf.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)


def find_money_mentions(text: str) -> list[str]:
    """Crude extraction aid: lines mentioning Rs amounts and % rates.
    This is a drafting aid only — a human must confirm each rule."""
    out = []
    for line in text.splitlines():
        if re.search(r"(₹|Rs\.?|INR)", line) and "%" in line:
            out.append(line.strip())
    return out[:200]


def hf_crosscheck(csv_path: pathlib.Path) -> dict:
    """Parse the HF / CardAdvisor CSV, skipping its comment line 1.
    Returns fee + rate-range cross-checks only — NOT full rules."""
    lines = csv_path.read_text().splitlines()
    rows = list(csv.DictReader(io.StringIO("\n".join(lines[1:]))))
    return {
        "source": "DevchandraSah/indian-credit-card-facts (2026-08-16, CC BY 4.0)",
        "cards": len(rows),
        "note": "Rate ranges and fees only. Caps, exclusions and posting "
                "basis must come from issuer documents.",
        "by_card": {
            r["cardKey"]: {
                "name": r["name"], "issuer": r["issuer"],
                "annual_fee": r["annualFeeRs"],
                "fee_waiver_spend": r["feeWaiverSpendRs"],
                "reward_min_pct": r["rewardRateMinPct"],
                "reward_max_pct": r["rewardRateMaxPct"],
                "last_verified": r["lastVerified"],
            }
            for r in rows
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", type=pathlib.Path)
    ap.add_argument("--hf-cards", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("data/verified/_draft.json"))
    args = ap.parse_args()
    draft: dict = {"verification_status": "pending_review"}
    if args.pdf:
        text = extract_pdf_text(args.pdf)
        draft["source_pdf"] = str(args.pdf)
        draft["money_mentions"] = find_money_mentions(text)
    if args.hf_cards:
        draft["hf_crosscheck"] = hf_crosscheck(args.hf_cards)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(draft, indent=2, ensure_ascii=False))
    print(f"Wrote DRAFT (pending_review, not verified): {args.out}")


if __name__ == "__main__":
    main()
