# OSS Link Auditor

[![Test](https://github.com/Aryalmilan-max/oss-link-auditor/actions/workflows/test.yml/badge.svg)](https://github.com/Aryalmilan-max/oss-link-auditor/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

![OSS Link Auditor: Broken links. Visible redirects. Human review.](assets/social-preview.png)

**Find broken, redirected, and suspicious Markdown links before your users do.**

OSS Link Auditor is a transparent Python CLI and GitHub Action for maintainers
of documentation, awesome lists, knowledge bases, and resource catalogs. It was
extracted from real maintenance work where a redirect can be more dangerous than
a simple 404: an expired domain may now lead to unrelated or hijacked content.

It never disables TLS verification and never deletes content automatically.
Every failure remains a human-reviewable signal.

## Why another link checker?

Many link checkers optimize for a single green-or-red result. Maintainers often
need more context:

- **Broken links** need review, but a temporary network failure is not proof.
- **Redirects** may be harmless migrations—or evidence that ownership changed.
- **Repeated URLs** should be checked once, even across many Markdown files.
- **CI failures** need deterministic output that humans can inspect.

OSS Link Auditor reports these cases separately and keeps the implementation
small enough to audit.

## Quick start

Requires Python 3.10 or newer and has no runtime dependencies.

```bash
git clone https://github.com/Aryalmilan-max/oss-link-auditor.git
cd oss-link-auditor
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
oss-link-auditor README.md docs/
```

Example text report:

```text
404    https://example.com/old-guide    HTTP Error 404: Not Found
301    https://example.com/start        https://example.com/docs/start
Checked 42 unique links in 8 Markdown files; 1 failure, 1 redirect.
```

Machine-readable output:

```bash
oss-link-auditor . --json
oss-link-auditor . --json > link-report.json
```

Fail CI only when a link is broken or unreachable:

```bash
oss-link-auditor . --fail-on-broken
```

## Use as a GitHub Action

Add this workflow to `.github/workflows/link-audit.yml`:

```yaml
name: Audit Markdown links

on:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: Aryalmilan-max/oss-link-auditor@main
        with:
          paths: "."
          fail-on-broken: "true"
```

For production workflows, pin third-party actions—including this one—to a full
commit SHA after reviewing the source.

## Supported Markdown links

- inline links: `[Guide](https://example.com/guide)`
- reference definitions: `[guide]: https://example.com/guide`
- autolinks: `<https://example.com/guide>`
- recursive discovery of `.md` and `.markdown` files

Image URLs are intentionally excluded from the current release.

## Design principles

1. Keep normal TLS certificate verification enabled.
2. Treat automated failures as review signals, not deletion instructions.
3. Make redirects visible because final ownership may differ.
4. Prefer deterministic, inspectable output over hidden heuristics.
5. Keep the runtime dependency-free.

## Contributing

Good first contributions include parser edge cases, clearer reports, and tests
for real maintainer workflows. Read [CONTRIBUTING.md](CONTRIBUTING.md) and see
the [roadmap](ROADMAP.md) before opening a pull request.

## Project status

This is an early, working release. The CLI, tests, and GitHub Action are usable;
the interface may evolve based on maintainer feedback. See
[CHANGELOG.md](CHANGELOG.md).

## License

MIT. See [LICENSE](LICENSE).
