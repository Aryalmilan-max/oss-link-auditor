# OSS Link Auditor

`oss-link-auditor` is a small Python command-line tool for checking HTTP links
across Markdown files. It was extracted from real maintenance work on public
resource lists where dead, redirected, and hijacked links require human review.

The tool keeps TLS verification enabled and reports network failures instead of
treating them as proof that a resource should be deleted.

## Features

- scans individual Markdown files or directories recursively
- recognizes inline links, reference definitions, and autolinks
- checks each unique URL once with bounded concurrency
- reports broken links separately from redirects
- produces readable text or JSON output
- optionally fails CI when broken or unreachable links are found
- uses only the Python standard library at runtime

## Install for development

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

## Usage

```bash
oss-link-auditor README.md docs/
oss-link-auditor README.md --json
oss-link-auditor . --fail-on-broken
```

Redirects are reported for review because a successful redirect can still lead
to a different or hijacked resource. A failed automated request is also a review
signal, not an instruction to remove the link.

## Development

Run the standard-library test suite:

```bash
python -m unittest discover -s tests -v
```

## Project status

This is an early release. Contributions should stay focused on transparent,
deterministic link auditing rather than automatic content deletion.

## License

MIT. See [LICENSE](LICENSE).
