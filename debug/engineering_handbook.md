# Cascade Forge — Engineering Handbook

This handbook describes how the engineering organization at Cascade Forge writes, ships, and operates software. It is reviewed quarterly by the VP of Engineering.

## Tech Stack

The primary languages used across the company's services are **Rust** (storage engines, build agents, network proxies) and **TypeScript** (control plane, web UI, internal tooling). A handful of legacy services are written in Go and are being incrementally rewritten.

- **Application layer:** Rust 1.83+, TypeScript 5.5+
- **Datastores:** PostgreSQL 16, ClickHouse 24, Redis 7
- **Orchestration:** Kubernetes 1.30 on GKE (primary) and EKS (DR region)
- **Message bus:** NATS JetStream
- **Object storage:** Google Cloud Storage (primary), S3-compatible (DR)
- **CI/CD:** Cascade Forge dogfoods Helix CI for all internal builds

## Branch and Release Strategy

The default development branch on every repository is `main`. All changes go through a pull request with at least one approval from a designated reviewer in the repository's `CODEOWNERS` file. Direct pushes to `main` are blocked by branch protection.

Releases follow a **weekly train model**:

- **Tuesday 16:00 UTC** — release candidate is cut from `main`
- **Wednesday** — automated smoke and load tests run against the RC in the staging environment
- **Thursday 14:00 UTC** — production rollout begins, gated on a 24-hour soak
- **Friday** — rollout completes for all regions if no SLO regressions are detected

Hotfixes outside the train require explicit sign-off from an on-call captain.

## Code Review Standards

All pull requests must:

1. Include a clear description of the change and its motivation
2. Reference a linked issue or design document if the change is non-trivial
3. Pass all required checks (lint, unit tests, integration tests, license scan)
4. Receive at least one approving review from a code owner

Pull requests larger than 1,000 changed lines must be split or accompanied by a written justification.

## Testing Philosophy

- Unit tests are required for all business logic.
- Integration tests run against ephemeral Postgres and Redis instances spun up per build.
- End-to-end tests for the Helix CI control plane run against a dedicated long-lived staging cluster.
- Flaky tests are quarantined automatically after three failures in seven days and require explicit owner action to re-enable.

The engineering target is **90% line coverage** on Rust services and **80% line coverage** on TypeScript services.

## On-Call

Engineers are placed on the on-call rotation after **six months of tenure** and successful completion of an on-call shadow shift. Each service has a primary and secondary on-call. Shifts are 7 days, Monday to Monday, with hand-off at 09:00 in the engineer's local time.

Compensation: each weekday shift pays an additional $250, each weekend shift pays $500.

## Incident Response

Incidents are classified into four severities:

| Severity | Definition | Response Time |
|----------|------------|---------------|
| SEV1 | Customer-impacting outage of a critical path | 5 minutes |
| SEV2 | Degraded service or partial customer impact | 15 minutes |
| SEV3 | Internal-only impact or workaround available | 1 hour |
| SEV4 | Cosmetic or low-impact issue | Next business day |

Every SEV1 and SEV2 incident requires a written postmortem within five business days, published in the internal `#postmortems` channel and reviewed at the next engineering all-hands.

## Security

All production access is gated behind hardware-key WebAuthn. SSH keys are not used. Database access in production requires a time-bounded session approved by a second engineer via the internal **Sentinel** tool.

Cascade Forge holds **SOC 2 Type II** (renewed October 2025) and **ISO 27001** (initial certification November 2024). A penetration test is performed twice annually by an independent third party.
