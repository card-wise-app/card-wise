# Ingestion checklist — per card, per issuer

Do not mark a card `verified` until every box is ticked and the
diff against the previous version is approved (PRD section 9).

- [ ] 1. Official product page filed in `data/official/<card>-product.html`
      — headline rates, fees, fee-waiver spend, network, variant
- [ ] 2. Cardholder T&C / MITC filed in `data/official/<card>-tnc.pdf`
      — caps (group, aggregate, per-transaction, base-linked),
      exclusions, statement-cycle definition, posting basis,
      eligibility / membership conditions, transaction fees
- [ ] 3. Reward redemption terms filed in `data/official/<card>-redemption.pdf`
      — point value per redemption method, minimum redemption,
      expiry, redemption fees, transfer partners and ratios
- [ ] 4. Extracted to structured JSON in `data/verified/<card>.json`
      with `source_url`, `effective_from`, `last_verified_date`
- [ ] 5. Schema validation passes (see `backend/app/ingest.py`)
- [ ] 6. Diff vs previous version reviewed; material changes flagged
- [ ] 7. Admin approval recorded; only then `verification_status=verified`

Secondary sources (HF / CardAdvisor) are used only at step 4 as
a cross-check: if a secondary rate range contradicts the issuer
document, the issuer document wins and the discrepancy is logged.

Local extraction (no paid API by default):
  requests + BeautifulSoup for pages, PyMuPDF for PDFs.
  Firecrawl (cloned in `tools/firecrawl/`, self-hosted) is an
  optional alternative extractor — see `backend/app/ingest.py`.
  Never send a user's personal data to an extraction service.
