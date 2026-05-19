# Cascade Forge — RAG Test Questions (v2)

This second test set exercises the new parser formats: `.docx`, `.html`,
`.csv`, `.json`. Each question targets content that lives **only** in one
of the new fixtures, except the cross-format question, which spans a new
fixture and an existing one.

Upload everything in `debug/` (the original seven files plus the four new
fixtures) before running these questions.

## 1. DOCX — Legacy CLI sunset

**Q:** What did the 12 February 2026 all-hands decide about the legacy CLI?
**Expected:** Sunset the legacy CLI by 30 June 2026. The new Rust CLI ships
as a static binary in May 2026.
**Source:** `meeting_minutes.docx`

## 2. HTML — SOC 2 audit partner

**Q:** Which firm is Cascade Forge partnered with for SOC 2 audit services,
and since when?
**Expected:** Arrowpath Assurance, since January 2024.
**Source:** `about.html`

## 3. CSV — Account ownership

**Q:** Who is the account owner for the Lumen Robotics account, and what is
their monthly recurring revenue?
**Expected:** Robert Hale; $12,500 MRR.
**Source:** `customers.csv`

## 4. JSON — Incident detail

**Q:** What was the postmortem owner for incident INC-2025-014, and which
service did it affect?
**Expected:** Henrik Lindqvist; Helix CI (38-minute global build outage from
build cache eviction).
**Source:** `incidents.json`

## 5. Cross-format — Berlin office expansion

**Q:** What budget was approved for the Berlin office expansion at the most
recent all-hands, and roughly how many staff currently work in that office?
**Expected:** $400,000 approved (from the 12 Feb 2026 all-hands meeting);
roughly 25 staff in Berlin.
**Source:** `meeting_minutes.docx` and `company_overview.md`
