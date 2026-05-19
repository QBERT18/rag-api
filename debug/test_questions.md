# Cascade Forge — RAG Test Questions

Upload every file in this `debug/` folder (except this `test_questions.md` and
`_gen_pdfs.py`) and ask the questions below. Each one has a clear,
verifiable answer somewhere in the corpus — the expected answer is included so
you can grade the model's response.

## 1. Founding and Leadership

**Q:** Who founded Cascade Forge and in what year?
**Expected:** Maya Chen and Daniel Park, in April 2018.
**Source:** `company_overview.md`

## 2. Office Locations

**Q:** Where are Cascade Forge's three offices and roughly how many staff are in each?
**Expected:** Vancouver, BC (HQ, ~70); Berlin, Germany (~25); Singapore (~15).
**Source:** `company_overview.md`

## 3. Product Revenue Split

**Q:** Which Cascade Forge product generated the largest share of 2025 revenue, and roughly what percentage?
**Expected:** Helix CI, roughly 62% of 2025 revenue.
**Source:** `products.md` and `financials_2025.txt`

## 4. PulseDB Pricing

**Q:** What is the monthly price of the PulseDB "Production" plan and what ingest rate does it allow?
**Expected:** $390 per month, up to 1 million points per second.
**Source:** `products.md`

## 5. Funding History

**Q:** How much capital has Cascade Forge raised in total, and who led the Series B?
**Expected:** $48.4 million total raised; the Series B was led by Aurora Capital.
**Source:** `company_overview.md` and `financials_2025.txt`

## 6. Release Process

**Q:** How often does Cascade Forge cut release candidates, and on what day of the week does the production rollout begin?
**Expected:** Weekly release train. Release candidate is cut on Tuesday; production rollout begins Thursday.
**Source:** `engineering_handbook.md`

## 7. On-Call Policy

**Q:** When does an engineer first become eligible for the on-call rotation, and what is the additional pay for a weekend shift?
**Expected:** After six months of tenure (and a shadow shift). Weekend shifts pay an additional $500.
**Source:** `engineering_handbook.md`

## 8. Security Compliance

**Q:** Which security certifications does Cascade Forge currently hold, and when were they obtained?
**Expected:** SOC 2 Type II (renewed October 2025) and ISO 27001 (initial certification November 2024).
**Source:** `engineering_handbook.md`

## 9. Data Classification Tiers

**Q:** What are the four data classification tiers used at Cascade Forge?
**Expected:** Public, Internal, Confidential, Restricted.
**Source:** `policies.pdf`

## 10. 2026 Roadmap — Stitch SDK

**Q:** What ARR contribution target has Cascade Forge set for Stitch SDK by the end of 2026, and what is it growing from?
**Expected:** At least 18% of total ARR by year end 2026, up from 9% at end of 2025.
**Source:** `roadmap_2026.pdf`

## Bonus — Multi-document

**Q:** Who is the engineering manager for PulseDB, and what initiative is the team delivering in Q1 2026?
**Expected:** Adaeze Eze is the PulseDB engineering manager. The Q1 2026 initiative is the PulseDB write-ahead log compaction rewrite.
**Source:** `employees.txt` and `roadmap_2026.pdf`
