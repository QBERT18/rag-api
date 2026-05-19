# Cascade Forge — Product Catalog

Cascade Forge ships three commercial products and one open-source project. All paid plans are billed monthly or annually in USD; annual contracts receive a 15% discount.

## 1. Helix CI

A continuous integration and build platform designed for monorepos. Helix CI uses a distributed cache and content-addressed task graph to skip work that has already been computed.

### Key features

- Remote build cache with content-addressed storage
- Native support for Bazel, Nx, Turborepo, and Cargo workspaces
- Parallel test execution with automatic shard balancing
- Flaky-test detection (statistical model retrains every 24 hours)
- GitHub, GitLab, and Bitbucket integrations

### Plans

| Plan | Monthly Price | Concurrent Jobs | Cache Storage |
|------|---------------|-----------------|---------------|
| Starter | $0 | 4 | 5 GB |
| Team | $290 / org | 50 | 200 GB |
| Business | $1,200 / org | 250 | 1 TB |
| Enterprise | Custom | Unlimited | Custom |

Helix CI launched in May 2019 and is the company's largest revenue line, accounting for roughly **62% of 2025 revenue**.

## 2. PulseDB

A managed time-series database optimized for application metrics and event data. PulseDB is a fork of an internal storage engine that was open-sourced in 2021.

### Key features

- Sub-second query latency on 90-day rolling windows
- Native PromQL and SQL endpoints
- Automatic downsampling to long-term cold storage (S3-compatible)
- Multi-region replication with bounded staleness
- Retention policies per measurement

### Plans

| Plan | Monthly Price | Ingest Rate | Retention |
|------|---------------|-------------|-----------|
| Developer | $49 | 100k points/s | 14 days |
| Production | $390 | 1M points/s | 90 days |
| Scale | $1,800 | 10M points/s | 365 days |

PulseDB entered general availability in October 2023. It accounted for roughly **23% of 2025 revenue** and is the company's fastest-growing line, with year-over-year revenue growth of 184%.

## 3. Stitch SDK

A vendor-neutral observability SDK that emits OpenTelemetry traces, metrics, and logs from application code. Stitch ships with auto-instrumentation for Node.js, Python, Go, Rust, Java, and .NET.

### Key features

- Single-binary collector with built-in tail-based sampling
- Drop-in OpenTelemetry compatibility
- Native exporters for PulseDB, Datadog, Honeycomb, and Grafana Cloud
- Static analysis to detect missing or duplicated spans
- Free for individual developers; paid tier required for team features

### Plans

| Plan | Monthly Price | Hosts | Tail-Sampling |
|------|---------------|-------|---------------|
| Individual | $0 | 1 | No |
| Team | $89 / month | 25 | Yes |
| Enterprise | Custom | Unlimited | Yes |

Stitch SDK launched in beta in June 2024 and reached GA in February 2025. It accounted for roughly **9% of 2025 revenue**, with the remaining **6%** coming from professional services.

## Open Source: Forge Build

A community-driven build orchestrator written in Rust. Forge Build is licensed under Apache 2.0 and powers the Helix CI agent runtime. The repository has over 8,200 GitHub stars and accepts external contributions through a published RFC process.
