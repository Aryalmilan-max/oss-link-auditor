# Copyable examples

## GitHub Action

Copy [`link-audit.yml`](link-audit.yml) into your repository at
`.github/workflows/link-audit.yml`. It audits Markdown on pull requests and
manual runs, publishes a trust report in the job summary, and fails only for
broken, unreachable, or safety-blocked links.

The example uses a version tag for readability. For production, inspect this
repository and pin the Action to a full commit SHA.

## Deterministic terminal report

From the repository root:

```bash
python3 scripts/demo.py
```

Expected invariant: one healthy link, one redirect, and one broken link. The
loopback port and temporary path vary. See [the capture guide](../docs/DEMO.md).
