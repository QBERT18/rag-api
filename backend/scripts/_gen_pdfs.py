"""One-shot generator for PDF fixtures in the debug/ folder.

Run from project root:
    backend/venv/Scripts/python.exe backend/scripts/_gen_pdfs.py
"""

from pathlib import Path

from fpdf import FPDF

OUT_DIR = Path(__file__).resolve().parents[2] / "debug"


_REPLACEMENTS = {
    "—": "-",  # em dash
    "–": "-",  # en dash
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "…": "...",
}


def _ascii(s: str) -> str:
    for k, v in _REPLACEMENTS.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "replace").decode("latin-1")


def make_pdf(filename: str, title: str, body: str) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, _ascii(title), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", size=11)
    for line in body.strip().splitlines():
        line = _ascii(line.rstrip())
        if not line:
            pdf.ln(3)
            continue
        if line.startswith("# "):
            pdf.set_font("Helvetica", style="B", size=13)
            pdf.multi_cell(0, 7, line[2:], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=11)
            continue
        pdf.multi_cell(0, 5.5, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(OUT_DIR / filename))
    print(f"wrote {filename}")


POLICIES = """
# Acceptable Use

All Cascade Forge employees, contractors, and interns must use company-issued
hardware for company work. Personal devices may not access production systems
under any circumstances. Devices must be encrypted at rest using FileVault,
BitLocker, or LUKS depending on platform. Lost or stolen devices must be
reported to security@cascadeforge.com within two hours of discovery.

# Data Classification

Cascade Forge classifies internal information into four tiers:

  Public      - Material intended for external distribution (marketing pages,
                product documentation, public blog posts).
  Internal    - General employee communications. May be shared widely within
                the company but not outside.
  Confidential- Customer data, financial figures, unreleased product plans.
                Sharing externally requires written approval from the data
                owner.
  Restricted  - Source code for security-sensitive components, production
                credentials, individual customer PII. Access is granted on a
                least-privilege basis and logged.

Mishandling Restricted data is grounds for immediate termination.

# Access Reviews

A quarterly access review is performed by the Security team. Every employee's
access to production systems, cloud accounts, and customer data is re-attested
by their manager. Reviews must complete within ten business days of the start
of each calendar quarter. Stale access is revoked automatically by the Sentinel
tool seven days after a missed review.

# Vendor Management

Any third-party SaaS vendor that processes Cascade Forge or customer data must
complete a security questionnaire and sign a DPA prior to use. The Security
team maintains an authoritative register of approved vendors. Engineers must
not enable new integrations on production accounts without an entry in this
register.

# Incident Reporting

Any suspected security event - a phishing attempt, a leaked credential, an
unexpected device on the corporate network - must be reported to
security@cascadeforge.com or via the #sec-incidents internal channel within one
hour of discovery. The Security team will triage and, if needed, initiate the
formal incident response process described in the engineering handbook.

# Acceptable Time Off

Cascade Forge offers a flexible time-off policy. Full-time employees are
expected to take a minimum of fifteen working days per calendar year, in
addition to public holidays in their country of residence. Time off must be
requested at least two weeks in advance for blocks of more than three
consecutive days, and approved by the employee's manager.

# Travel and Expenses

All business travel must be booked through the company's travel partner. Hotel
reimbursement is capped at $300 per night in tier-1 cities and $200 per night
elsewhere. Receipts are required for all individual expenses over $25.

# Code of Conduct

Cascade Forge is committed to a respectful and inclusive workplace. Harassment,
discrimination, and retaliation will not be tolerated. Violations should be
reported to Sofia Reyes, Head of People, or anonymously via the third-party
ethics line.

This policy was last reviewed by the People and Security teams on
1 December 2025. The next scheduled review is 1 June 2026.
""".strip()


ROADMAP = """
# Theme 1 — Reliability and Scale

The 2026 reliability theme focuses on the Helix CI scheduler and the PulseDB
ingest path. Both have shown latency regressions at peak hours in the largest
customer tenants. The target by end of Q3 2026 is to sustain a 99.95% monthly
availability SLO across all three core products, measured from the customer
edge.

Key initiatives:

  Q1 2026  - Helix CI scheduler v3 rollout (sharded by tenant).
  Q1 2026  - PulseDB write-ahead log compaction rewrite.
  Q2 2026  - Stitch SDK collector multi-tenancy.
  Q3 2026  - Cross-region active-active for control plane (GA target).

# Theme 2 — Developer Experience

Helix CI's CLI will be rewritten in Rust during the first half of 2026,
replacing the current Node.js implementation. The new CLI ships as a single
static binary with sub-100ms cold start. A new VS Code extension is planned
for general availability in Q2 2026, with parity for JetBrains IDEs targeted
for Q4 2026.

PulseDB will receive a new query playground in the web UI, including saved
queries, share links, and exportable charts. Target ship date is 15 May 2026.

# Theme 3 — Stitch SDK Expansion

Stitch SDK is the company's youngest product and the focus of significant
investment in 2026. Planned milestones:

  February 2026  - Continuous profiling beta (CPU and memory).
  May 2026       - Native PHP and Ruby SDKs.
  July 2026      - Distributed-tracing-aware anomaly detection.
  October 2026   - Frontend RUM (real user monitoring) general availability.

The goal is to make Stitch SDK contribute at least 18% of total ARR by year end
2026, up from 9% at the end of 2025.

# Theme 4 — Compliance and Regions

To unlock regulated industries in EMEA, Cascade Forge will pursue ISO 27017
and ISO 27018 certification during 2026, with a target completion date of
November 2026. A dedicated EU data residency region will launch on Helix CI by
1 April 2026, hosted in Frankfurt and operated under a German legal entity
incorporated in February 2026.

A SOC 2 Type II renewal audit is scheduled for October 2026.

# Theme 5 — Pricing and Packaging

The pricing pages for Helix CI and PulseDB will be refreshed in March 2026.
A new "Growth" tier is being added between Team and Business on Helix CI,
targeted at organizations of 50 to 200 engineers. PulseDB introduces a
usage-based add-on for retention extension beyond 90 days, priced at
$0.000040 per data point per day.

# Out of Scope

The following items were considered for 2026 but have been explicitly
deferred:

  - An on-premises self-managed deployment of Helix CI.
  - A managed Postgres offering.
  - Mobile SDK support for iOS and Android.

These remain on the longer-term roadmap and will be revisited during the
2027 planning cycle.

This document was approved by the executive team on 8 January 2026.
""".strip()


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_pdf("policies.pdf", "Cascade Forge — Company Policies (v3.1)", POLICIES)
    make_pdf("roadmap_2026.pdf", "Cascade Forge — 2026 Product Roadmap", ROADMAP)
