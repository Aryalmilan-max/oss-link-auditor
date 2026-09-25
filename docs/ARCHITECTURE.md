# Architecture

OSS Link Auditor deliberately has one small, dependency-free execution path.

```mermaid
flowchart LR
  A[Markdown paths] --> B[Recursive discovery]
  B --> C[URL extraction + file:line index]
  C --> D[Unique URL queue]
  D --> E[Public-target validation]
  E --> F[Concurrent HTTPS checks]
  F --> G[Redirect-target validation]
  G --> H[Trust categories]
  H --> I[Text / JSON / Markdown report]
  I --> J[CLI exit code or GitHub Step Summary]
```

`core.py` owns discovery, extraction, network policy, concurrency, and result
models. `cli.py` owns argument validation and rendering. `action.yml` adapts the
CLI to GitHub Actions without changing audit semantics.

## Trust categories

- `HEALTHY`: request completed below HTTP 400 at the original URL.
- `REDIRECT`: final URL differs but stays on the same host.
- `REDIRECT-CROSS-HOST`: final host differs and deserves closer review.
- `BROKEN`: HTTP failure, DNS failure, timeout, or another network error.
- `BLOCKED`: target or redirect resolves to a non-public network address.

Network failures remain evidence for human review; the project never deletes or
rewrites repository content.

## Known limits

The parser intentionally supports common inline links, reference definitions,
and autolinks rather than the entire Markdown grammar. DNS rebinding cannot be
fully prevented in application code; isolate untrusted CI workloads at the
network layer. See [../SECURITY.md](../SECURITY.md).
