# Launch issue drafts

These are approval-ready issue bodies for the first contributor-facing tasks.
Open them only after confirming that the scope still matches the current code.
Label each issue `good first issue` only when a maintainer is available to
review and help a first-time contributor.

## Configurable URL exclusions with visible reasons

**Suggested labels:** `enhancement`, `good first issue`

Add a repeatable CLI option that excludes a URL pattern while keeping the
reason visible in the final report. The default behavior must remain unchanged,
private-target blocking must not be bypassed, and exclusions must never silently
convert a failed link into a healthy result.

Acceptance criteria:

- document the proposed CLI syntax before implementation
- preserve the current text, Markdown, and JSON output contracts
- add unit tests for one exact URL, one host pattern, and invalid input
- update the README and CLI help

## Retry transient network failures conservatively

**Suggested labels:** `enhancement`, `good first issue`

Add a small, bounded retry policy for failures that are plausibly transient.
Do not retry permanent HTTP responses such as 404, and do not weaken TLS or
private-network safeguards.

Acceptance criteria:

- document which exception/status classes are retryable
- use a strict maximum attempt count and deterministic tests
- keep the first release behavior available with zero retries
- include the attempt count in diagnostic output when a retry occurs

## Add Markdown parser edge-case fixtures

**Suggested labels:** `tests`, `good first issue`

Expand parser coverage with real, minimal Markdown fixtures. Good candidates
include escaped brackets, titles after URLs, nested parentheses, and reference
definitions with unusual whitespace.

Acceptance criteria:

- one fixture per behavior
- assertions cover both extracted URL and exact source line
- no public network calls
- document any intentionally unsupported syntax in `docs/ARCHITECTURE.md`
