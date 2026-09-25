# Changelog

All notable project changes are documented here.

## [Unreleased]

- Nothing yet.

## [0.1.1] - 2026-09-25

- Updated the reusable Action and test workflow to current Node 24-backed
  GitHub Actions releases.
- Expanded the supported mypy development range to include the next major
  release while retaining the tested lower bound.
- Enabled GitHub Discussions and routed usage questions away from bug reports.

## [0.1.0] - 2026-09-25

- Initial dependency-free Python CLI.
- Markdown file discovery and unique-link extraction.
- Separate reporting for failures and redirects.
- Text and JSON output.
- Optional CI failure for broken or unreachable links.
- Exact source file and line context for every link.
- Trust categories for same-host redirects, cross-host redirects, and blocked
  private-network targets.
- Markdown job-summary reports from the reusable GitHub Action.
- Deterministic local demo and Python 3.10-3.13 CI matrix.
- Community issue forms, pull-request template, security policy, and launch
  documentation.
